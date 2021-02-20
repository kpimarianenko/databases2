from urllib.error import HTTPError

import requests
import os
from urllib.request import urlopen
from lxml import etree

current_path = os.path.abspath(os.curdir)


def run():
    url = 'https://www.ukraine-is.com/uk/'
    out_file_name = 'out\\task1.xml'
    out_file_path = os.path.join(current_path, out_file_name)
    links = get_page_links(url, 20)

    root = etree.Element('data')

    for link in links:
        get_xml_page_from_url(root, link)

    xml = etree.ElementTree(root)
    xml.write(out_file_path, pretty_print=True, xml_declaration=True, encoding="utf-8")


def get_xml_page_from_url(root, url):
    response = urlopen(url)

    html_parser = etree.HTMLParser()
    tree = etree.parse(response, html_parser)
    text_nodes = tree.xpath('body//*[not(self::svg | self::style | self::script | self::img)]/text() | body//img/@src')
    res_text_nodes = []
    for node in text_nodes:
        node = node.strip('\n, ')
        if len(node) > 0:
            res_text_nodes.append(node)

    return convert_to_xml_page(root, res_text_nodes, url)


def convert_to_xml_page(root, nodes, url):
    page = etree.SubElement(root, 'page')
    page.set('url', url)

    for node in nodes:
        is_image = node.startswith('https') or node.startswith('data:image')
        tag_type = 'image' if is_image else 'text'
        tag = etree.SubElement(page, 'fragment')
        tag.set('type', tag_type)
        tag.text = node

    return page


def get_page_links(url, max_pages):
    response = urlopen(url)
    html_parser = etree.HTMLParser()
    tree = etree.parse(response, html_parser)
    page_links = tree.xpath('body//a/@href')
    page_links = list(filter(lambda item: not item.startswith('#') and item.startswith(url), page_links))
    links = [url]
    for link in page_links:
        is_valid = True
        if link not in links:
            try:
                urlopen(link)
            except HTTPError:
                is_valid = False
            finally:
                if is_valid:
                    links.append(link)
        if len(links) == max_pages:
            return links
    return links
