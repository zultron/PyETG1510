"""データ永続化モジュール"""
import os
import json
from collections.abc import Mapping
import copy
from pyetg1510.helper import SysLog

logger = SysLog.logger


class settings:
    def __init__(self, initial_data, *file_name):
        self._fp = None
        self._setting_data = initial_data
        self._origin_data = initial_data
        self._logger = SysLog.logger
        if len(file_name) > 0:
            self._setting_dir = os.path.dirname(file_name[0])
            self._setting_file = os.path.basename(file_name[0])
            self._fullpath = self._setting_dir + "/" + self._setting_file
            self._inititalize()

    @property
    def file(self):
        return self._setting_file

    @file.setter
    def file(self, f):
        self._setting_file = f
        self._fullpath = self._setting_dir + "/" + self._setting_file

    @property
    def dir(self):
        return self._setting_dir

    @dir.setter
    def dir(self, f):
        self._setting_dir = f
        self._fullpath = self._setting_dir + "/" + self._setting_file

    @property
    def data(self):
        return self._setting_data

    def _inititalize(self):
        if not os.path.exists(self._setting_dir):
            os.mkdir(self._setting_dir)
        if os.path.isfile(self._fullpath):
            self.load()
        else:
            self._fp = open(self._fullpath, "w", encoding="utf-8")
            self.save()

    def _deepupdate(self, dict_base, other):
        for k, v in other.items():
            if isinstance(v, Mapping) and k in dict_base:
                self._deepupdate(dict_base[k], v)
            else:
                dict_base[k] = v

    def _report_diff(self, before: dict, after: dict, path: str = ""):
        for k, v in after.items():
            if isinstance(v, Mapping) and k in before:
                if path == "":
                    parent = path
                else:
                    parent = path + "."
                self._report_diff(before[k], v, parent + str(k))
            else:
                if k in before and before[k] != v:
                    self._logger.warning(
                        "Setting changed : " + path + "." + str(k) + " : " + str(before[k]) + " -> " + str(v)
                    )

    def save(self):
        try:
            self._fp = open(self._fullpath, "w", encoding="utf-8")
            self._report_diff(self._origin_data, self._setting_data, "")
            json.dump(
                self._setting_data, self._fp, ensure_ascii=False, indent=4, sort_keys=True, separators=(",", ": ")
            )
            self._origin_data = copy.deepcopy(self._setting_data)
            self._fp.close()
        except Exception as e:
            logger.exception(e)

    def load(self):
        try:
            self._fp = open(self._fullpath, "r", encoding="utf-8")
            self._deepupdate(self._setting_data, json.load(self._fp))
            self._origin_data = copy.deepcopy(self._setting_data)
            self._fp.close()
        except json.JSONDecodeError as e:
            logger.exception(e)
            raise e
        except ValueError as e:
            logger.exception(e)
            raise e
        self.save()

    def make_slice_object(self, start, count):
        s = start - 1
        c = s + count
        return slice(s, c)

    def __del__(self):
        if not self._fp is None:
            self._fp.close()
