from __future__ import annotations
import re
import inspect
from types import FrameType
from typing import cast
import datetime
import croniter


class CommonNS:
    """Basic structures operations, merges, pastes and force"""

    @staticmethod
    def paste_in_d(d: dict, k: str, v, merge_dicts_in_place=False) -> dict:
        """ We mostly work with dicts of complex stuff so pasting values by types is common operation """
        ''' Args: d target dict, k - key to paste, v -value to paste
            merge_dicts_in_place if True will merge dicts if val is dict, otherwise will create list of dicts
        '''
        if k in d.keys():
            old_v = d.get(k)
            if type(old_v) == list:
                old_v.append(v)
                d[k] = old_v
            elif (merge_dicts_in_place) and (type(old_v) == dict) and (type(v) == dict):
                d[k] = CommonNS.merge_dicts(old_v, v)
            elif type(old_v) == type(v):
                d[k] = [old_v, v]
        else:
            d[k] = v
        return d

    @staticmethod
    def current_fn_name() -> str:
        """Return the current function's name."""
        return cast(FrameType, cast(FrameType, inspect.currentframe()).f_back).f_code.co_name

    @staticmethod
    def current_caller_name() -> str:
        """Return the calling function's name."""
        return cast(FrameType, cast(FrameType, inspect.currentframe()).f_back.f_back).f_code.co_name

    @staticmethod
    def ium_cfg_to_ini(ins: str, outs: str, silent=True):
        """@Depricated.
        Changes node names from IUM.config to .ini style where amount of square brackets equals to node lvl"""

        lvl = len(ins.split('/')) - 2
        outs = ("[" * lvl) + ins + ("]" * lvl)
        if not silent:
            print(f"lvl: {lvl}\t instr: {ins}\n {outs}")
        return outs

    @staticmethod
    def merge_dicts(d1: dict, d2: dict) -> dict:
        """" In case d={**d1, **d2} not supported """
        if not isinstance(d1, dict) or not isinstance(d2, dict):
            raise TypeError(f"Tried merging {type(d1)} with {type(d2)} as dicts")
        d = d1.copy()
        d.update(d2)
        return d

    @staticmethod
    def merge_lists(l1: list, l2: list) -> list:
        """Ugly merger to list from unknown type"""
        if isinstance(l1, list):
            if isinstance(l2, list):
                return [*l1, *l2]
            elif l2 is None:
                return l1
            else:
                return l1.append(l2)
        elif isinstance(l2, list):
            if l1 is None:
                return l2
            else:
                return l2.append(l1)
        elif l1 is None:
            return [l2]
        elif l2 is None:
            return [l1]
        else:
            return [l1, l2]


class DateTimeHelper:
    log_time_stamp_re = re.compile(r'^(?P<mdy>[\d]{2}/[\d]{2}/[\d]{4}) (?P<hms>[\d]{2}:[\d]{2}:[\d]{2})')

    @staticmethod
    def seconds_from_midnight_utc(dt: datetime.datetime) -> int:
        """Zone unaware total seconds from midnight in datetime object"""
        if dt.tzinfo:
            raise ValueError("Call for zone aware methods")
        return dt.hour * 3600 + dt.minute * 60 + dt.second

    @staticmethod
    def seconds_from_now(dt: datetime.datetime) -> int:
        """Zone unaware difference between now and dt"""
        if dt.tzinfo:
            raise ValueError("Call for zone aware methods")
        now = datetime.datetime.now()
        td = dt - now
        return dt.hour * 3600 + dt.minute * 60 + dt.second

    @staticmethod
    def dt_next_from_cron_str(cron_str: str) -> datetime.datetime:
        """
        Parses valid cron string, returns datetime obj of closest scheduled execution
        """
        now = datetime.datetime.now
        cron_inst = croniter(cron_str, now)
        schedule = cron_inst.next(now)
        return schedule.next()

    @staticmethod
    def date_from_IUM(date_str: str, form="%m/%d/%Y %H:%M:%S"):
        m = DateTimeHelper.log_time_stamp_re.match(date_str)
        d = m.groupdict()
        return datetime.datetime.strptime(d.get("mdy") + " " + d.get("hms"), form)

    @staticmethod
    def join_mdy_hms(mdy: str, hms: str, form="%m/%d/%Y %H:%M:%S"):
        """ IUMLOG style dateStr split (as if fetched by groupdict)-> Datetime (zoneaware from sys time)"""
        mdyhms = mdy + " " + hms
        return datetime.datetime.strptime(mdyhms, form)

    @staticmethod
    def sec_from_hms(time_str: str):
        """ HMS -> Secs : Int to contruct timedeltas from H:M:S Strs"""
        if not isinstance(time_str, str):
            raise TypeError
        h, m, s = time_str.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
