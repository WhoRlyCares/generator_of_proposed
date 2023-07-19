from __future__ import annotations

import socket
import ssl
from dataclasses import dataclass, field

import random
import string
import hashlib
from config import Config
from datetime import datetime
import os
import shutil



class GeneratedFile:
    """
    Wrapper to generate and store crc md5 hashes  for files.
    reg_dt: datetime - init dt
    rel_path: str - relative path for fh
    scheme : str name of file distribution scheme
    generator : Callable which yields appropriate file content
    """

    def __init__(self, cfg: Config, fpath:str, scheme, gen):
        if not os.path.isfile(fpath):
            raise ValueError(f"Trying to describe non existing file at {fpath}")
        self.reg_dt = datetime.now()
        self.rel_path = fpath
        self.scheme = scheme
        self.generator = gen
        self.calc_md5()

    def __repr__(self):
        return f"File Details {self.rel_path}, Registred at: {self.reg_dt.strftime('%d.%m.%y %X')}\n md5: {self.md5}"

    def set_mask(self, mask: str):
        self.mask = mask

    def calc_md5(self):
        self.md5 = hashlib.md5(open(self.rel_path, 'rb').read()).hexdigest()

    def calc_crc(self):
        self.sha256 = hashlib.sha256(open(self.rel_path, 'rb').read()).hexdigest()


class FTPSource:
    """FTP access source."""
    verb = True

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.init_dt = datetime.now()
        self.created_files = []
        self.created_dirs = []
        self.ensure_default_dirs(cfg)

    @staticmethod
    def join_cfg_paths(cfg: Config, local_out: str, local_in=None) -> str:
        """
        JOIN paths act as defined in Config and relative to os.cwd
        :param cfg: Config instance
        :param local_out: path_where_output_expected
        :param local_in: path_where_input_expected
        :return:
        """
        dir_path = ""
        if not local_in:
            local_in = cfg.LOCAL_IN
        if local_out.startswith('/') or local_out.startswith(os.sep):
            return (
                (cfg.LOCAL_OUT + local_out[1:])
                if cfg.LOCAL_OUT.endswith('/') or cfg.LOCAL_OUT.endswith(os.sep)
                else (cfg.LOCAL_OUT + local_out)
            )
        elif cfg.LOCAL_OUT.endswith('/') or cfg.LOCAL_OUT.endswith(os.sep):
            return (cfg.LOCAL_OUT + local_out)
        else:
            return f'{cfg.LOCAL_OUT}/{local_out}'

    @staticmethod
    def resolve_diez(cfg: Config, pstr: str, dt=None) -> str:
        """
        #YYMMDD in str --> to dt.parts as formated.
        :param cfg:  Config instance, for fetching defaults
        :param pstr: path string which may have #notations inside
        :param dt: datetime instance, if missing use now
        :return: reformated pathlike string
        """
        if not dt:
            dt = datetime.now()
        if '#' not in pstr:
            return pstr
        diez_idx = pstr.find("#")
        next_sep = pstr.find("/", diez_idx)
        if next_sep == -1:
            remaining_str = pstr[diez_idx:]
            format = FTPSource.diezYMD_notation_to_stf(remaining_str)
            return pstr[:diez_idx] + dt.strftime(format)
        else:
            remaining_str = pstr[diez_idx:next_sep]
            format = FTPSource.diezYMD_notation_to_stf(remaining_str)
            return pstr[:diez_idx] + dt.strftime(format) + pstr[next_sep:]

    @staticmethod
    def diezYMD_notation_to_stf(s: str) -> str:
        """
        #YYMMDD -> stftime notation in laziest way possible
        :param s: string to reformat, must start with #
        :return: format string compatible with strftime
        """
        if not s.startswith("#"):
            raise ValueError(f"Expected string, starting with #. Got {s}")
        tmp2 = s.upper()
        tmp1 = tmp2.replace("YYYY", "%Y")
        tmp2 = tmp1.replace("YY", "%y")
        tmp1 = tmp2.replace("MM", "%m")
        tmp2 = tmp1.replace("MMMM", "%b")
        tmp1 = tmp2.replace("DD", "%d")
        return tmp1[1:]

    def ensure_default_dirs(self, cfg: Config):
        os.makedirs(cfg.LOCAL_IN, exist_ok=True)
        os.makedirs(cfg.LOCAL_OUT, exist_ok=True)

        for p in cfg.DEFAULT_TREE:
            dir_path = FTPSource.join_cfg_paths(cfg, p, cfg.LOCAL_IN)
            if FTPSource.verb:
                print(f"Creating\t{dir_path}")
            os.makedirs(dir_path, exist_ok=True)
            self.created_dirs.append(dir_path)

        for k, arch_paths in cfg.DEFAULT_ACHIVE_TREE.items():
            print(f"{k}:{arch_paths}")
            for path_var in arch_paths:
                resolved_path = FTPSource.resolve_diez(cfg, path_var)
                dir_path = FTPSource.join_cfg_paths(cfg, resolved_path, cfg.LOCAL_IN)
                if FTPSource.verb:
                    print(f"Creating\t{dir_path}")
                self.created_dirs.append(dir_path)
                os.makedirs(dir_path, exist_ok=True)

    def purge_output(self):
        for dir_p in self.created_dirs:
            for fh in os.listdir(dir_p):
                os.remove(dir_p + fh)
        try:
            shutil.rmtree('./output')
        except OSError as e:
            print(f"Deletion failed: {e.filename} - {e.strerror}")
        self.created_dirs = []
        self.created_files = []

    def generate_any_f(self, ftype='noise', fpd=10):
        for p2dir in self.created_dirs:
            if FTPSource.is_exch(p2dir):
                self.generate_ftp_f(p2dir, ftype, fpd)
            else:
                self.generate_arch_f(p2dir, ftype, fpd)

    def generate_ftp_f(self, p2dir: str, ftype, fpd: int):
        clr = self.color_from_path(p2dir)
        idx = next(
            (i for i, subs in enumerate(self.cfg.DEFAULT_TREE) if subs in p2dir),
            -1,
        )
        if idx == -1:
            print(f"Masks not defined for {p2dir}, aborting")
            return None
        masks = self.cfg.DEFAULT_MASKS[idx]
        if FTPSource.verb:
            print(f"Expect {masks} for {p2dir}")
        for _ in range(fpd):
            mask = random.choice(masks)
            fname = FTPSource.resolve_wildcards(mask)
            rel_path = p2dir + fname if p2dir.endswith('/') else f'{p2dir}/{fname}'
            FTPSource.writen_b_noise_to(rel_path)
            gen_f = GeneratedFile(self.cfg, rel_path, clr, FTPSource.writen_b_noise_to)
            self.created_files.append(gen_f)
            if FTPSource.verb:
                print(f"{gen_f} \t<{clr}>")

    def generate_arch_f(self, p2dir, ftype, fpd):
        print(f"{p2dir} is arch")

    def color_from_path(self, p2dir: str) -> str:
        return (
            'orange'
            if p2dir not in self.cfg.colormap.keys()
            else self.cfg.colormap.get(p2dir)
        )

    @staticmethod
    def writen_b_noise_to(fpath: str, fSizeBytes=1024) -> None:
        with open(fpath, 'wb') as fb_out:
            fb_out.write(os.urandom(fSizeBytes))

    @staticmethod
    def write_random_forms_to(fpath, form) -> None:
        pass

    @staticmethod
    def random_char_seq(len):
        lst = string.ascii_letters
        return ''.join(random.choice(lst) for _ in range(len))

    @staticmethod
    def resolve_wildcards(fpath: str, format=None, wildcards={'*': 10, '?': 1}):
        for wc, wc_len in wildcards.items():
            while wc in fpath:
                replacement = FTPSource.random_char_seq(random.randint(1, wc_len))
                fpath = fpath.replace(wc, replacement, 1)
        if format and not fpath.endswith(os.sep):  # TODO
            fpath += format
        return fpath

    @staticmethod
    def is_exch(pstr: str) -> bool:
        return 'exch' in pstr

    @staticmethod
    def is_arch(pstr: str) -> bool:
        return 'arch' in pstr


def random_tests():
    cfg = Config("15:00")
    cfg.print_status_time()
    ftps = FTPSource(cfg)
    fst = ftps.resolve_diez(cfg, "/arc/ARCHIVES/TAP2.RCV/#YYMM")
    scnd = ftps.resolve_diez(cfg, "/arc/ARCHIVES/TAP2.RCV/#YYMM/deeperdir/")
    for _ in range(10):
        print(ftps.resolve_wildcards("/some/pa*/fdsa*", ".cdr"))



if __name__ == "__main__":
    """
    cfg = Config("15:00")
    cfg.print_status_time()
    ftps = FTPSource(cfg)
    print(2 + 2)
    ftps.generate_any_f()
    """
    # ftps.purge_output()
    ...
