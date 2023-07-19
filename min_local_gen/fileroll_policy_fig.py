from __future__ import annotations
from dataclasses import dataclass, field
import re
import os
from siu_utils import min_ium_fig as IUMfig


@dataclass
class FileRollPolicyFig(IUMfig.Lightfig):
    verbose = False
    dirS = "./"
    baseN = ""
    maxV = 100
    minDig = 0
    inc = 1
    defFileContent = b""

    @staticmethod
    def setBaseFileName(target: IUMfig.Lightfig, fns: str):
        target.baseN = fns.rstrip(" ")
        if target.verbose:
            print(f"Set BaseFileName {fns}")

    @staticmethod
    def setInitialInputFile(target: FileRollPolicyFig, fns: any):
        "Providing existing file overrides every other option"
        if os.path.isfile(fns):
            target.defFileContent = target.toBuffer(fns)
            ...  # TODO valid f - should src it's details
        else:
            target.initF = fns
        if target.verbose:
            print(f"Set InitialInputFile {fns}")

    @staticmethod
    def setMaxVal(target: IUMfig.Lightfig, maxV=1024):
        target.maxV = maxV
        if target.verbose:
            print(f"Set maxVal {maxV}")

    @staticmethod
    def setMinDigits(target: IUMfig.Lightfig, minDig=0):
        target.mindDig = minDig
        if target.verbose:
            print(f"Set minDig {minDig}")

    @staticmethod
    def setRollIncrement(target: IUMfig.Lightfig, inc=1):
        target.inc = inc
        if target.verbose:
            print(f"Set inc {inc}")

    @staticmethod
    def setSrcDir(target: IUMfig.Lightfig, dirStr="./"):
        target.dirS = dirStr
        if target.verbose:
            print(f"Set dirStr {dirStr}")

    @staticmethod
    def setSuffix(target: IUMfig.Lightfig, suffix=""):
        target.suf = suffix
        if target.verbose:
            print(f"Set suf {suffix}")

    def decode(self, cfgLikeStr: str) -> None:
        self.update(super().from_iumfig_like_str(cfgLikeStr))
        for k, v in self.items():
            if k in self.attr_map.keys():
                self.attr_map.get(k)(self, v)

    def configure(self, cfg: IUMfig.Lightfig) -> None:
        self.update(cfg)
        for k, v in self.items():
            if k in self.attr_map.keys():
                self.attr_map.get(k)(self, v)

    def calculateProperStart(self) -> int:
        if len(self.initF) <= 0:
            return 0
        if len(self.baseN) <= 0:
            return int(self.longestNumSeq(self.initF))
        numStr = self.initF.strip(self.baseN)
        if len(self.suf) > 0:
            numStr = numStr.strip(self.suf)
        return int(numStr)

    def withTrailingZeroes(self, i: int):
        if self.minDig > len(str(i)):
            return '0' * (self.minDig - len(str(i))) + str(i)
        else:
            return str(i)

    @staticmethod
    def longestNumSeq(s: str) -> int:
        l = re.findall(r"(?P<D>\d{1,})", s)
        lens = [len(s) for s in l]
        return l[lens.index(max(lens))]

    @staticmethod
    def toBuffer(fpath: str) -> bytes:
        buf = b''
        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'Expected readable file at {fpath}')
        with open(fpath, 'rb') as fh:
            while True:
                if lb := fh.read(1024):
                    buf += lb
                else:
                    break
        return buf

    def fixdir(self):
        ds = os.path.abspath(self.dirS)
        ds.replace("//", os.sep).replace(r"\\", os.sep)
        ds = ds + os.sep
        return ds

    def createFilePaths(self, amount=None, content=None, **kwargs) -> list[str]:
        fpaths = []
        if not amount:
            amount = self.maxV;
        if not content:
            content = self.defFileContent
        for i in range(0, amount, self.inc):
            fnums = self.withTrailingZeroes(i + self.calculateProperStart())
            if self.verbose:
                print(f"num:{fnums}, base:{self.baseN}, dir:{self.fixdir()}")
            abs_p = self.fixdir() + self.baseN + fnums + self.suf
            fpaths.append(abs_p)
        if self.verbose:
            print(fpaths)
        return fpaths

    def createFiles(self, amount=None, **kwargs):
        if not amount:
            amount = self.maxV
        fpaths = self.createFilePaths(amount, **kwargs)
        for p in fpaths:
            with open(p, 'wb') as fh:
                resp = fh.write(self.defFileContent)

    def setFileContent(self, paths: str):
        self.defFileContent = FileRollPolicyFig.toBuffer(paths)

    attr_map = {
        'BaseFileName': setBaseFileName,
        'InitialInputFile': setInitialInputFile,
        'MaxValue': setMaxVal,
        'RollIncrement': setRollIncrement,
        'SrcDir': setSrcDir,
        'Suffix': setSuffix
    }


if __name__ == "__main__":
    ex_cfg = r"""
        ClassName=SequenceNumberFilePolicy 
        SrcDir=\SIU\var\SampleData\Netflow
        BaseFileName=nfc. 
        Padding=3 
        Suffix=.log
        InitialInputFile=nfc.001.log
    """

    fpfig = FileRollPolicyFig()
    fpfig.verbose = True
    fpfig.decode(ex_cfg)
    fpfig.createFilePaths()
    # fpfig.createFiles()
