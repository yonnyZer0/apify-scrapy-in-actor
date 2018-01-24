import logging
import re
__author__ = 'seni'

from nameparser import HumanName
from unidecode import unidecode

from nameparser.config import CONSTANTS

class TextProcessingPipeline(object):
    professional_suffixes = ["CFA"]

    def __init__(self):
        CONSTANTS.titles.remove('Wing')

    def process_item(self, item, spider):
        if not 'name_full' in item:
            logging.warn("name_full key not found in item from url %s" % item['url'])
            return item

        full_name = item['name_full']

        prepared_fullname = self.prepare_name_for_parsing(full_name)
        prepared_fullname = self.format_name_dots(prepared_fullname) # example : J. P. Grownder =>
                                                                     #           JP Grownder
        name = HumanName(prepared_fullname)

        item['split_title'] = name.title
        item['split_first_name'] = name.first
        item['split_mid_name'] = name.middle
        item['split_last_name'] = name.last
        item['split_suffix'] = name.suffix

        if len(name.first) == 1 and len(name.middle) == 1:
            item['split_first_name'] = ''.join([name.first, name.middle])
            item['split_mid_name'] = ''
        if len(name.last) == 1 and len(name.middle) == 1:
            item['split_last_name'] = ''.join([name.first, name.last])
            item['split_mid_name'] = ''

        item["username"] = self.generate_username(name.first, name.middle, name.last)
        item["simplified_joined_name"] = self.generate_simplified_joined_name(name.first, name.middle, name.last)

        return item

    def generate_username(self, first_name, middle_name, last_name):
        username = "%s%s%s" % (first_name, middle_name, last_name)
        username = re.sub(r'[^\w]', '', username)
        return username

    def generate_simplified_joined_name(self, first_name, middle_name, last_name):
        return "%s %s" % (first_name, last_name)

    def prepare_name_for_parsing(self, name):
        # convert foreign characters
        name = unidecode(name)

        # remove suffixes, example : Milena Muller, CFA => Milena Muller
        for suffix in self.professional_suffixes:
            name = name.replace(suffix, "")

        name = name.strip()
        name = name.rstrip(',').lstrip(',')
        name = name.strip()

        return name
    def format_name_dots(self, name):
        """
        name: J. P. Gownder | Julie A. Ask
        :return: J P Grownder | Julie A Ask
        """
        stripped_dots_name = name.replace('.', '')
        return stripped_dots_name
