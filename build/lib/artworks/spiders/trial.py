# -*- coding: utf-8 -*-
# Any additional imports (items, libraries,..)
import scrapy
from artworks.items import ArtworksItem
from scrapy.loader import ItemLoader
import re


class TrialSpider(scrapy.Spider):
    name = "trial"
    main_url = "http://pstrial-2019-12-16.toscrape.com/browse/{category}?page={page}"
    start_urls = [
        main_url.format(category="summertime", page=0),
        main_url.format(category="insunsh", page=0),
    ]

    def parse(self, response):
        # Check if there items in the page to collect
        current_category = re.search(r"browse/(.+)\?page", response.url).group(1)
        categories = current_category.split("/")

        arts = response.css("div a[href*='/item']::attr(href)").getall()
        if arts:
            # go for all itens in the current category
            for art in arts:
                il = ItemLoader(item=ArtworksItem(), selector=art)
                item_url = response.urljoin(art)

                yield scrapy.Request(
                    item_url,
                    callback=self.parse_inside_info,
                    cb_kwargs={
                        "item": il,
                        "item_url": item_url,
                        "categories": categories,
                    },
                )

            next_page = response.css('form.next input[name="page"]::attr(value)').get()
            next_page = self.main_url.format(category=current_category, page=next_page)
            yield scrapy.Request(next_page, callback=self.parse)
        else:
            all_subcategories = response.css("#subcats div > a::attr(href)").getall()
            if all_subcategories:
                # check in order check if category have been visited, if not:
                for subcategory in all_subcategories:
                    # add category to visited categories
                    next_category = re.search(r"browse/(.+)", subcategory).group(1)
                    next_category = self.main_url.format(category=next_category, page=0)
                    yield scrapy.Request(next_category, callback=self.parse)

    def parse_inside_info(self, response, item, item_url, categories):
        item.selector = response

        item.add_css("artist", "h2.artist::text")
        item.add_css("title", "h1::text")
        img_url = response.urljoin(response.css("img::attr(src)").get())
        item.add_value("image", img_url)

        item.add_value("url", item_url)
        item.add_value("categories", categories)

        dimensions = response.css('td.key:contains("Dimensions") ~ td.value::text').get()
        if dimensions and "cm" in dimensions:
            patterns = [
                # pattern 12.12 x 123,12 X 43
                r"(\d+) . ([\d.,]+) . ([\d.,]+)",
                # pattern 12.12 x 123,12 cm
                r"([\d.,]+)[xX ]{0,3}([\d.,]+) cm",
            ]
            for p in patterns:
                result = re.search(p, dimensions)
                if result is not None:
                    height = result[1]
                    width = result[2]
                    item.add_value("height", height)
                    item.add_value("width", width)
                    break

        item.add_css("description", "div.description p::text")

        yield item.load_item()
