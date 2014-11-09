__author__ = 'Ahmed Shabib'
from lxml.html import clean
import re

import urllib2
from lxml import etree
import json
from urlparse import urlparse
from lxml.etree import tostring

class Parsly():
    def __init__(self):
        self.__cleaner__ = clean.Cleaner(page_structure=True)

    def parse(self, url, site_name):
        response = urllib2.urlopen(url)
        htmlparser = etree.HTMLParser()
        tree = etree.parse(response, htmlparser)
        result = {}
        # # Loading the config file for the website
        config_main = json.load(open("configs/" + site_name + ".json"))
        e_thing_to_remove = config_main.get("$remove")
        for item in e_thing_to_remove:
            for elem in tree.xpath(item):
                if len(elem) > 0:
                    elem.getparent().remove(elem)
        # # Applying the XPATH filters for each of the item .


        config = config_main["content"]
        for item in config.keys():
            item_node = tree.xpath(config.get(item).get("path", "//junk"))
            if len(item_node) > 0:
                item_node = item_node[0]

                config_item = config.get(item, "")
                config_item_type = config_item.get("type", "")
                if config_item_type == "nodes":
                    for elem in item_node:
                        if config_item.get("subtype", "") == "node":
                            result[item].append(elem.get(config_item.get("query_attrib", "")).capitalize())
                        elif config_item.get("subtype", "") == "text":
                            result[item] = elem.text
                elif config_item_type == "node":
                    result[item] = item_node.get(config_item.get("query_attrib", ""))
                elif config_item_type == "html":
                    result[item] = self.__cleaner__.clean_html(tostring(item_node, method="html", encoding="utf-8"))
                elif config_item_type == "text":
                    result[item] = item_node.text
            else:
                result[item] = ""

        return result

    @staticmethod
    def __get_urls__(html_content):
        links = re.findall('"((http|ftp)s?://.*?)"', html_content)
        return links

    @staticmethod
    def __get_images__(self, url):
        pass

    @staticmethod
    def __is_path_relative__(s_url):
        if urlparse(s_url).netloc:
            return False
        else:
            return True
