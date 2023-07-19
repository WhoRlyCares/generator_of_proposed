from __future__ import annotations
from dataclasses import field, dataclass

class ConfigurationException(Exception):
    """Exceptions during configure, start-up"""
    ...

class IUMfigException(ConfigurationException):
    """Exceptions at parsing underlying IUMfigs"""


class Lightfig(dict):
    verbose = False
    @staticmethod
    def nodes(d_inst: dict, nodel=None):
        if nodel is None:
            nodel = []
        for k, v in d_inst.items:
            if issubclass(v, dict):
                nodel.append(k)
            elif Lightfig.islink(v):
                raise NotImplementedError

    @staticmethod
    def islink(v: any) -> int:
        if issubclass(v, str):
            # 0 - not linked; 1 - linear link; 2 - link 2 templates;
            unsupported_expr = ["link=", "/templates/"]
            return sum(1 for s in unsupported_expr if s in v)

    @staticmethod
    def from_iumfig_like_str(cfgLike: str) -> Lightfig:
        lf = Lightfig()
        for s in cfgLike.split("\n"):
            s = s.rstrip("\r").lstrip(" ")
            eq_i = s.find("=")
            if eq_i != -1:
                lf.update({s[:eq_i]: s[eq_i + 1:]})
        return lf
