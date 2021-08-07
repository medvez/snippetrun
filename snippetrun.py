import paramiko
import getpass
import time


class SnippetRun:
    def __init__(self):
        self.usernanme = ''
        self.password = ''
        self.snippet = []
        self.devices = []