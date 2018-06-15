#!/usr/bin/env python
# Usage: python alto_ocr_text.py <alto_zip_file>

import codecs
import os
import sys
import xml.etree.ElementTree as ET
import zipfile


class FullTextProfile(object):
    """
    see also https://docs.google.com/document/d/1t5yGEzQ0KV2rqU0sFDoKnI2bIDBGrmj0f1gSOCRUgJ4

    see also https://europeana.atlassian.net/browse/EA-953
    """
    def __init__(self, newspaper_title, issue_no, page_no):
        self.newspaper_title = newspaper_title
        self.issue_no = issue_no
        self.page_no = page_no
        self.type = "page"
        self.text_blocks = list()
        # page level language
        self.language = ""

    def to_fulltext(self):
        text_blocks_content = list()
        for text_block in self.text_blocks:
            text_blocks_content.append(text_block.content)

        return "\n".join(text_blocks_content)

    def to_edm_json(self):
        newspaper_fulltext = {}
        fulltext_lang = self.language
        # rare case: en-US, e.g., Te%C3%9Fmann_Library\Tiroler_Volksbote\1919-12-24.alto.zip
        if fulltext_lang is not None and '-' in fulltext_lang:
            fulltext_lang = fulltext_lang.split('-')[0]

        fulltext_lang = "" if fulltext_lang is None else fulltext_lang

        newspaper_fulltext["language"] = [fulltext_lang]
        newspaper_fulltext["doc_type"] = ["Newspaper"]
        newspaper_fulltext["issue"] = self.issue_no
        newspaper_fulltext["fulltext." + fulltext_lang] = self.to_fulltext()
        return newspaper_fulltext


class TextBlock(object):
    """
    
    """
    def __init__(self, language, content):
        self.language = language
        self.content = content


def load_fulltext_profile_from_alto_file(alto_file_path):
    with open(alto_file_path, "r", encoding="utf-8") as alto_file:
        page_no = os.path.basename(alto_file_path).split(".")[0]
        fulltext_profile = alto_ocr_2_text_profile(alto_file.read(), page_no=str(page_no))

    return fulltext_profile


def alto_ocr_2_text_profile(alto_xml_file, issue_no="", page_no=""):
    """

    :param alto_xml_file:
    :param page_no:
    :return: list, list of text blocks from given ALTO file
    """

    namespace = {'alto-1': 'http://schema.ccs-gmbh.com/ALTO',
                 'alto-2': 'http://www.loc.gov/standards/alto/ns-v2#',
                 'alto-3': 'http://www.loc.gov/standards/alto/ns-v3#'}
    tree = ET.ElementTree(ET.fromstring(alto_xml_file))
    xmlns = tree.getroot().tag.split('}')[0].strip('{')
    if xmlns == "alto":
        alto_xml_file = alto_xml_file.replace("<alto", "<alto xmlns=\"http://www.loc.gov/standards/alto/ns-v2#\"")
        # no default namespace e.g., National_Library_of_Estonia\Postimees\1897-08-08.alto.zip
        # quick fix by inserting name space
        tree = ET.ElementTree(ET.fromstring(alto_xml_file))
        xmlns = tree.getroot().tag.split('}')[0].strip('{')

    fulltext_profile = FullTextProfile("", issue_no, page_no)
    text_blocks = list()
    if xmlns in namespace.values():
        for textblocks in tree.iterfind('.//{%s}TextBlock' % xmlns):
            textblock_lang = textblocks.attrib.get('language')
            fulltext_text_lines = list()
            for lines in textblocks.iterfind('.//{%s}TextLine' % xmlns):
                for line in lines.findall('{%s}String' % xmlns):
                    text = line.attrib.get('CONTENT') + ' '
                    fulltext_text_lines.append(text)
            textblock = TextBlock(textblock_lang, "".join(fulltext_text_lines))
            text_blocks.append(textblock)
    else:
        print('ERROR: Not a valid ALTO file (namespace declaration missing)')

    fulltext_profile.text_blocks = text_blocks
    fulltext_profile.language = _determine_page_language(text_blocks)
    return fulltext_profile


def _determine_page_language(text_blocks):
    """
    determine page level language from textblock in raw alto fulltext dataset

    language is encoded in every textblock
    Not every text block contains fulltext and language,
        for example, National_Library_of_France\Le_Petit_Journal\1941-08-11

    :param text_blocks:
    :return:
    """
    #todo: reconsider the granularity of language here

    language = ""
    for text_block in text_blocks:
        if text_block.language is not None and text_block.language != "":
            language = text_block.language

    return language


def extract_fulltext_4_issue(issue_fulltext_zip_file):
    """
    load fulltext of page from an issue in sequence

    :param issue_fulltext_zip_file:
    :return:list
    """
    fulltext_alto_files = load_alto_ocr_files(issue_fulltext_zip_file)

    fulltext_list = list()
    page_no = 0

    for fulltext_alto_file, issue_name in fulltext_alto_files:
        page_no += 1
        fulltext_list.append(alto_ocr_2_text_profile(fulltext_alto_file, issue_no=issue_name, page_no=page_no))

    return fulltext_list


def load_alto_ocr_files(fulltext_zip_file_path):
    """
    load fulltext of issue from alto zip file of an issue in order

    :param fulltext_zip_file_path: absolute path of zipped alto file
    :return: generator, list of OCR file content in order
    """
    print("loading fulltext files from [%s] ... " % fulltext_zip_file_path)
    zipped_alto_files = zipfile.ZipFile(fulltext_zip_file_path)
    issue_name = os.path.basename(zipped_alto_files.filename).replace(".alto.zip", "")
    # adapt for National_Library_of_the_Netherlands dataset
    issue_name = issue_name.replace('_',' ')
    print("issue name: ", issue_name)
    alto_files = zipped_alto_files.filelist
    print("total alto file size: ", len(alto_files))
    # example file name: 1794-06-15_alto/79.alto.xml
    for f in sorted(zipped_alto_files.namelist(), key=lambda f_name: int(f_name.split("/")[1].split(".")[0])):
        xml_content = zipped_alto_files.read(f)
        # xml_content = codecs.decode(xml_content, encoding='utf-8', errors='strict')
        yield xml_content.decode(encoding='utf-8'), issue_name


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        zipped_full_text_file = str(sys.argv[1])

        print("load fulltext from %s" % zipped_full_text_file)
        if os.path.isfile(zipped_full_text_file) and zipfile.is_zipfile(zipped_full_text_file):
            issue_page_profile_list = extract_fulltext_4_issue(zipped_full_text_file)

            print("issue no: ", issue_page_profile_list[0].issue_no)
            print("page no: ", issue_page_profile_list[0].page_no)
            print("language: ", issue_page_profile_list[0].language)
            print("full text: ", issue_page_profile_list[0].to_fulltext())

            print("total pages from current issue loaded: ", len(issue_page_profile_list))
        else:
            print(zipped_full_text_file, "not exist or not a zip file!")