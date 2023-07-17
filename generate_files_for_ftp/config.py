import os
from datetime import datetime, timedelta, time
import platform

class Config(object):
    def __init__(self, stop_at=""):
        self.SSH_HOST = "192.168.100.234"
        self.SSH_USER = "slogger"
        self.SSH_PASS = os.environ.get("SIDIB_MON_SHH_PASS") or "Sloger has default DS pass; Pyusr has my default DS pass;"
        self.SSH_PATH = "/opt/test_ftp/"
        self.LOCAL_IN = "./input/"
        self.LOCAL_OUT = "./output/"

        today = datetime.now()
        if not stop_at:
            self.stop_at = today.replace(hour=12, minute=00)
        else:
            self.stop_at = datetime.combine(today.date(), datetime.strptime(stop_at,"%H:%M").time())

        self.stop_at_max = self.stop_at + timedelta(seconds=90)
        self.env_platform = platform.platform()
        self.env_path = os.path.realpath(os.curdir)

        self.DEFAULT_TREE = ["/tap-exch/dch/TAP-IN/",
                             "/tap-exch/dch/TAP-OUT/",
                             "/tap-exch/Pk-tjk91/Out/",
                             "/tap-exch/Pk-tjk91/In/",
                             "/tap_exch/upload/",
                             "/tap-exch/download/"
                             ]

        self.DEFAULT_MASKS = [["CDTJKBD*.", "CDRUSBD*."],  # "tap-exch/dch/TAP-IN/"
                              ["CD*.","TD*.","RC*."],  # "tap-exch/dch/TAP-OUT/"
                              ["CDTJKBD*."],  # "tap-exch/Pk-tjk91/Out/"
                              ["CD*TJK91*."], # "tap-exch/Pk-tjk91/In/"
                              ["TD*.", "CDRUSBD*."],# "tap_exch/upload/"
                              ["CD*."],  # "/tap-exch/download/"
                              ]

        self.DEFAULT_ACHIVE_TREE = {
            "RAP Archive" : ["/arc/ARCHIVES/RAP/#YYMM/"],
            "DualIMSI Archive" : ["/arc/ARCHIVES/DualIMSI/TJKBD/TAP2.RCV/#YYMM/",
                                  "/arc/ARCHIVES/DualIMSI/TJKBD/TAP2.SND/#YYMM/"],
            "TAP Archive" : ["/arc/ARCHIVES/TAP2.RCV/#YYMM",
                             "/arc/ARCHIVES/TAP2.RCV/#YYMM"],
            "TADIG Archive" : ["/arc/TADIG/TAP.RCV/",
                               "/arc/TADIG/TAP.SND/"]
        }
        self.colormap ={'./output/tap-exch/dch/TAP-IN/':'green',
                        './output/tap-exch/dch/TAP-OUT/':'blue',
                        './output/tap-exch/Pk-tjk91/Out/':'purple',
                        './output/tap-exch/Pk-tjk91/In/':'green',
                        './output/tap_exch/upload/':'red',
                        './output/tap-exch/download/':'blue',
                        './output/arc/ARCHIVES/RAP/2212/':'blue',
                        './output/arc/ARCHIVES/DualIMSI/TJKBD/TAP2.RCV/2212/':'purple',
                        './output/arc/ARCHIVES/DualIMSI/TJKBD/TAP2.SND/2212/':'green',
                        './output/arc/ARCHIVES/TAP2.RCV/2212':'blue',
                        './output/arc/ARCHIVES/TAP2.RCV/2212':'red',
                        './output/arc/TADIG/TAP.RCV/':'blue',
                        './output/arc/TADIG/TAP.SND/':'red'
        }

    def print_status_time(self):
        now = datetime.now()
        tdelta = self.stop_at_max - now
        min_left = f"{tdelta.seconds // 60}:{(tdelta.seconds // 60) % 60}"
        print(f"\nLast run at {now.strftime('%X')} \t JOB ends at {self.stop_at_max.strftime('%X')}\tMinutes left: {min_left}")
