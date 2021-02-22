from lxml import etree
from urllib.request import urlopen
import os


class Good:
    def __init__(self, name, img, price, description):
        self.name = name
        self.img = img
        self.price = price
        self.description = description


current_path = os.path.abspath(os.curdir)


def run():
    page_url = 'https://instrument.in.ua'
    katalog_page_url = '/katalog'
    response = urlopen(page_url + katalog_page_url)

    out_file_name = 'out\\task3.xml'
    out_file_path = os.path.join(current_path, out_file_name)
    html_parser = etree.HTMLParser()
    tree = etree.parse(response, html_parser)
    goods_link_nodes = tree.xpath("//div[contains(@class, 'catalogCard-title')]/a/@href")[:20]

    goods = []
    for good_link in goods_link_nodes:
        goods.append(get_good_info(page_url, good_link))

    root = etree.Element('data')

    for good in goods:
        append_good_to_root(good, root)

    xml = etree.ElementTree(root)
    xml.write(out_file_path, pretty_print=True, xml_declaration=True, encoding="utf-8")


def get_good_info(root, page):
    url = root + page
    response = urlopen(url)

    html_parser = etree.HTMLParser()
    tree = etree.parse(response, html_parser)

    good_name = tree.xpath("//h1/text()")[0]
    good_img = root + tree.xpath("//img[contains(@class, 'gallery__photo-img')]/@src")[0]
    good_price = tree.xpath("//div[contains(@class, 'product-price__item')]/meta/@content")[0]
    good_description = tree.xpath("//div[contains(@class, 'product-description')]/div[contains(@class, 'text')]/p/text()"
    "| //div[contains(@class, 'product-description')]/div[contains(@class, 'text')]/div/p/text()")[0]

    return Good(good_name, good_img, good_price, good_description)


def append_good_to_root(good, root):
    goodEl = etree.SubElement(root, 'good')

    name = etree.SubElement(goodEl, 'name')
    name.text = good.name
    img = etree.SubElement(goodEl, 'img')
    img.text = good.img
    price = etree.SubElement(goodEl, 'price')
    price.text = good.price
    description = etree.SubElement(goodEl, 'description')
    description.text = good.description



