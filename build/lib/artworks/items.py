# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
import re


def clean_artist_name(value):
    return [re.sub(r".+: ?([aA]fter)?", "", artist) for artist in value.split(";")]


def clean_url(value):
    return re.sub(r"\?back=.+", "", value)


def clean_title(value):
    clean_title = re.search(r"(Untitled )?[\[\()]?([\w\W]+[^\]\)])", value)
    try:
        clean_title.group(2)
    except:
        print("Not able to change title value")
        return value


class ArtworksItem(scrapy.Item):

    url = scrapy.Field(
        input_processor=MapCompose(clean_url),
        output_processor=TakeFirst(),
    )
    artist = scrapy.Field(input_processor=MapCompose(clean_artist_name))
    title = scrapy.Field(
        input_processor=MapCompose(clean_title),
        output_processor=TakeFirst(),
    )
    image = scrapy.Field(output_processor=TakeFirst())
    height = scrapy.Field(
        input_processor=MapCompose(float),
        output_processor=TakeFirst(),
    )
    width = scrapy.Field(
        input_processor=MapCompose(float),
        output_processor=TakeFirst(),
    )
    description = scrapy.Field(output_processor=TakeFirst())
    categories = scrapy.Field()
