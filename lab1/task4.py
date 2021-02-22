from lxml import etree
import os

current_path = os.path.abspath(os.curdir)
task3_xml = os.path.join(current_path, 'out\\task3.xml')
task4_xsl = os.path.join(current_path, 'out\\task4.xsl')
out_file_path = os.path.join(current_path, 'out\\task4.html')


def run():
    tree = etree.parse(task3_xml)
    raw_xslt = etree.parse(task4_xsl)
    xslt = etree.XSLT(raw_xslt)
    xhtml = xslt(tree)
    xhtml.write('out\\task4.html', pretty_print=True, xml_declaration=True, encoding="utf-8")
