from lxml import etree
import os

current_path = os.path.abspath(os.curdir)
task1_xml = os.path.join(current_path, 'out\\task1.xml')


def run():
    with open(task1_xml, 'r', encoding='utf-8') as xml:
        tree = etree.parse(xml)
    hyper_links = tree.xpath("//page/@url | //fragment[starts-with(text(), 'http')]/text()")

    for hyper_link in hyper_links:
        print(hyper_link)

