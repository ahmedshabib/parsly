import urllib
from urllib.parse import urlparse

import requests

__author__ = 'Ahmed Shabib'
from lxml.html import clean, HTMLParser, parse, tostring
import re
from io import StringIO, BytesIO

import json


class Parsly():
    def __init__(self):
        self.htmlparser = HTMLParser()
        self.__cleaner__ = clean.Cleaner(page_structure=True)

    def process_tree(self, tree, config):
        param_keys = config.keys()

        result = {}
        for item in param_keys:
            config_item = config.get(item, {})
            item_nodes = tree.xpath(config_item.get("path", "//junk"))
            # item_nodes = tree.cssselect(config_item.get("selector", "//junk"))
            if len(item_nodes) > 0:
                if config_item["type"] == "nodes":
                    node_meta = config_item["node"]
                    for elem in item_nodes:
                        if node_meta["type"] == "node":
                            if not result.get(item, None):
                                result[item] = []
                            result[item].append(self.process_tree(parse(BytesIO(tostring(elem)), self.htmlparser),
                                                                  node_meta["$parameters"]))
                        elif node_meta["type"] == "text":
                            result[item].append(elem.text)
                elif config_item["type"] == "node":
                    item_node = item_nodes[0]
                    node_meta = config_item["node"]
                    if node_meta["type"] == "query":
                        result[item] = item_node.get(config_item.get("query_attrib", ""))
                    elif node_meta["type"] == "text":
                        result[item] = item_node.text
                    elif node_meta["type"] == "html":
                        result[item] = self.__cleaner__.clean_html(tostring(item_node, method="html", encoding="utf-8"))
                    elif node_meta["type"] == "node":
                        result[item] = self.process_tree(parse(BytesIO(tostring(item_node)), self.htmlparser),
                                                         node_meta["$parameters"])
                elif config_item["type"] == "html":
                    item_node = item_nodes[0]
                    result[item] = self.__cleaner__.clean_html(tostring(item_node, method="html", encoding="utf-8"))
                elif config_item["type"] == "text":
                    item_node = item_nodes[0]
                    result[item] = item_node.text
            else:
                result[item] = ""
        return result

    def parse(self, url, file_name):
        response = requests.get(url)
        tree = parse(StringIO(response.text), self.htmlparser)
        result = {}
        # # Loading the config file for the website
        config_main = json.load(open(file_name))
        e_thing_to_remove = config_main.get("$remove")
        for item in e_thing_to_remove:
            for elem in tree.xpath(item):
                if len(elem) > 0:
                    elem.getparent().remove(elem)
        # # Applying the XPATH filters for each of the item .

        config = config_main["$parameters"]
        result = self.process_tree(tree, config)
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


p = Parsly()
result = p.parse("http://www.cargoupdate.com/tracktrace/loaddata.aspx?carrier=SV&awb=065-27894812",
                 "../config/mashable.json")
print(result)
