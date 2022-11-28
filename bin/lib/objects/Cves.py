#!/usr/bin/env python3
# -*-coding:UTF-8 -*

import os
import sys

from flask import url_for

sys.path.append(os.environ['AIL_BIN'])
##################################
# Import Project packages
##################################
from lib.ConfigLoader import ConfigLoader
from lib.objects.abstract_daterange_object import AbstractDaterangeObject
from packages import Date

config_loader = ConfigLoader()
r_objects = config_loader.get_db_conn("Kvrocks_Objects")
baseurl = config_loader.get_config_str("Notifications", "ail_domain")
config_loader = None


################################################################################
################################################################################
################################################################################

# # TODO: COMPLETE CLASS

class Cve(AbstractDaterangeObject):
    """
    AIL Cve Object.
    """

    def __init__(self, id):
        super(Cve, self).__init__('cve', id)

    # def get_ail_2_ail_payload(self):
    #     payload = {'raw': self.get_gzip_content(b64=True),
    #                 'compress': 'gzip'}
    #     return payload

    # # WARNING: UNCLEAN DELETE /!\ TEST ONLY /!\
    def delete(self):
        # # TODO:
        pass

    def get_link(self, flask_context=False):
        if flask_context:
            url = url_for('correlation.show_correlation', type=self.type, id=self.id)
        else:
            url = f'{baseurl}/correlation/show?type={self.type}&id={self.id}'
        return url

    # TODO # CHANGE COLOR
    def get_svg_icon(self):
        return {'style': 'fas', 'icon': '\uf188', 'color': '#1E88E5', 'radius': 5}

    # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO
    def get_misp_object(self):
        pass

    def get_meta(self, options=set()):
        meta = self._get_meta(options=options)
        meta['id'] = self.id
        meta['subtype'] = self.subtype
        meta['tags'] = self.get_tags(r_list=True)
        return meta

    def add(self, date, item_id):
        self._add(date, item_id)


# TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO # TODO
def get_all_cves():
    cves = []
    return cves

def get_cves_by_date(date):
    # return r_objects.zrange(f'cve:date:{date}', 0, -1)
    return set(r_objects.hkeys(f'cve:date:{date}'))

def get_cves_by_daterange(date_from, date_to):
    cves = set()
    for date in Date.substract_date(date_from, date_to):
        cves | get_cves_by_date(date)
    return cves

def get_cves_meta(cves_id, options=set()):
    dict_cve = {}
    for cve_id in cves_id:
        cve = Cve(cve_id)
        dict_cve[cve_id] = cve.get_meta(options=options)
    return dict_cve

def api_get_cves_meta_by_daterange(date_from, date_to):
    date = Date.sanitise_date_range(date_from, date_to)
    return get_cves_meta(get_cves_by_daterange(date['date_from'], date['date_to']), options=['sparkline'])

# if __name__ == '__main__':