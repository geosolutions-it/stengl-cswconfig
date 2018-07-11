# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


class BaseOutput(object):

    @classmethod
    def _get_output(cls, type, config):
        _sub_classes = [clazz for clazz in cls.__subclasses__()]
        for _clz in _sub_classes:
            if _clz.type() == type:
                return _clz(config)  # initialize here
        return None

    @classmethod
    def type(cls):
        raise NotImplemented

    def stream(self, buffer):
        raise NotImplemented


class FileOutput(BaseOutput):

    def __init__(self, config):
        self._dest_file = config.get(self.__class__.__name__, 'dest_file')

    @classmethod
    def type(cls):
        return 'FILE'

    def stream(self, buffer):
        with open(self._dest_file, "w") as text_file:
            text_file.write(buffer)

    def __str__(self):
        return "File Output Stream"


class CSWOutput(BaseOutput):

    def __init__(self, config):
        self._csw_url = config.get(self.__class__.__name__, 'csw_url')

        self._csw_usr = config.get(self.__class__.__name__, 'csw_usr') if \
            config.has_option(self.__class__.__name__, 'csw_usr') else None

        self._csw_pwd = config.get(self.__class__.__name__, 'csw_pwd') if \
            config.has_option(self.__class__.__name__, 'csw_pwd') else None

        from owslib.csw import CatalogueServiceWeb
        self._csw = CatalogueServiceWeb(url=self._csw_url, skip_caps=True)

    @classmethod
    def type(cls):
        return 'CSW'

    def stream(self, buffer):
        self._csw.transaction(ttype='insert', typename='gmd:MD_Metadata', record=buffer)

    def __str__(self):
        return "CSW Output Stream"
