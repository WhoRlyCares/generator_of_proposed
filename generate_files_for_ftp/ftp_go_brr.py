from __future__ import annotations
from typing import Protocol

import datetime
import glob
import socket
import ssl
import ftplib
from pathlib import Path
import paramiko
import hashlib
from siu_utils.min_ium_fig import ConfigurationException


class FTPProvider(Protocol):
    def adjust_files2transfer(self, fl: list) -> list:
        ...

    def goFTP(self) -> list:
        ...


class FTPviaSmth:
    target_path = None  # directory to use as root
    files2transfer: list  # list of local filepaths to be delivered
    alreadyTransferred: dict  # fname:crc2
    failed2transfer: dict  # fname:error

    def __init__(self, hosts: str, usr: str, psw: str, target_path: str):
        self.files2transfer = []
        self.failed2transfer = {}
        self.alreadyTransferred = {}
        if target_path:
            self.target_path = target_path

    def set_files2transfer(self, fl: list) -> list:
        """Sets and returns files2tranfser to existing files from list"""
        res_l = [Path(f) for f in fl if Path.is_file(Path(f))]
        self.files2transfer = res_l
        return res_l

    def adjust_files2transfer(self, fl: list) -> list:
        """Extends and returns files2transfer with existing files from list"""
        ext_l = [Path(f) for f in fl if Path.is_file(Path(f))]
        self.files2transfer.extend(ext_l)
        return self.files2transfer

    def tearUp(self, log_tearup: str):
        if log_tearup:
            with open(log_tearup, 'a+') as fh:
                fh.write(f"{datetime.datetime.now().strftime('%d.%m.%y %X:')} Cleaning up...")
                for f, h in self.alreadyTransferred.items():
                    fh.write(f"\tTransfered {Path(f)}, with {str(h)[:30]}...\n")
                for f, e in self.failed2transfer.items():
                    fh.write(f"\tFailed to deliver {Path(f)}, cause {str(e)}")
        self.alreadyTransferred = {}


class SFTPviaParamiko(FTPviaSmth):
    """Wrapper Over Paramiko SSHClient
    Usage: init->set/extend_files2trnasfer->goSFTP->tearUp"""
    ssh_cl: paramiko.SSHClient

    def __init__(self, hosts="192.168.100.246", usr="ftpuser", psw="ftpsiu", target_path=None):
        super().__init__(hosts, usr, psw, target_path)
        self.ssh_cl = paramiko.SSHClient()
        self.ssh_cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_cl.connect(hosts, username=usr, password=psw)
        except paramiko.AuthenticationException as authExc:
            raise ConfigurationException(
                f"Authentication failed, please verify your credentials:{authExc}") from authExc
        except paramiko.BadHostKeyException as badHostKeyExc:
            raise ConfigurationException(f"Unable to verify server's host key: {badHostKeyExc}") from badHostKeyExc
        except paramiko.SSHException as sshExc:
            raise ConfigurationException(f"Unable to establish SSH connection: {sshExc}") from sshExc

    def goFTP(self) -> list:
        return self.goSFTP()

    def goSFTP(self) -> list:
        """Attempts to deliver files from files2transfer. Returns only files which were delivered"""
        res = []
        for f in self.files2transfer:
            fp = Path(f)
            tp = f'{self.target_path}/{fp.name}' if self.target_path else f'./{fp.name}'
            with open(fp, "rb") as fh:
                digest = hashlib.file_digest(fh, "sha256")
                if fp in self.alreadyTransferred.keys():
                    if digest == self.alreadyTransferred[fp]:
                        continue
                try:
                    sftp = self.ssh_cl.open_sftp()
                    sftp.put(fp, tp)
                    self.alreadyTransferred[fp] = digest
                    res.append(fp)
                except paramiko.SSHException as SSHExc:
                    self.failed2transfer[fp] == str(SSHExc)
                    print(f"Encountered {SSHExc} while transfering {f}")
        for ffp, exc in self.failed2transfer.items():
            print(f"Failed to deliver {ffp} cause: {str(exc)}")
        return res

    def tearUp(self, log_tearup="./tearupLog.txt"):
        """Clean up and log"""
        self.ssh_cl.close()
        super().tearUp(log_tearup)


class FTPviaFTPLib(FTPviaSmth):
    def __init__(self,  hosts="192.168.100.246", usr="ftpuser", psw="ftpsiu", target_path=None):
        super().__init__(hosts, usr, psw, target_path)


class ImplicitFTPnTLS(ftplib.FTP_TLS):
    """
    FTP_TLS subclass that automatically wraps sockets in SSL to support implicit FTPS.
    Prefer explicit TLS whenever possible.
    """

    def __init__(self, *args, **kwargs):
        """Initialise self."""
        super().__init__(*args, **kwargs)
        self._sock = None

    @property
    def sock(self):
        """Return the socket."""
        return self._sock

    @sock.setter
    def sock(self, value):
        """When modifying the socket, ensure that it is SSL wrapped."""
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)
        self._sock = value

    def ntransfercmd(self, cmd, rest=None):
        """Override the ntransfercmd method"""
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        conn = self.sock.context.wrap_socket(
            conn, server_hostname=self.host, session=self.sock.session
        )
        return conn, size


def ftp_targets_test(host_str="192.168.100.246", u_str="ftpuser", pswds="ftpsiu", fp="test.svg"):
    file_path = Path(fp)
    with ImplicitFTPnTLS(host_str, u_str, pswds) as ftp:
        ftp.prot_p()
        with open(file_path, 'rb') as fh:
            print(f'Sending {fh.name} to {host_str}')
            ftp.storbinary(f'STOR {fh.name}', fh)


def sftp_bruteforce(host_str="192.168.100.246", u_str="ftpuser", pswds="ftpsiu", fp="test.svg"):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host_str, username=u_str, password=pswds)
    sftp = ssh.open_sftp()
    file_path = Path(fp)
    tp = f'./ftp_dir/{file_path.name}'
    sftp.put(fp, tp)
    sftp.close()
    ssh.close()


def test_unchrooted(host_str="192.168.100.246", u_str="ftpuser", pswds="ftpsiu"):
    sftp_p = SFTPviaParamiko(host_str, u_str, pswds)
    fl = list(glob.glob("./*.svg"))
    print(fl)
    sftp_p.adjust_files2transfer(fl)
    sftp_p.goSFTP()
    sftp_p.tearUp()


if __name__ == "__main__":
    # ftp_targets_test()
    # sftp_bruteforce()
    test_unchrooted()
    ...
