import paramiko
import getpass
import time


class SnippetRun:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.data_folder_path = ''
        self.snippet = []
        self.devices = []

    def get_credentials(self):
        self.data_folder_path = input('Full path to data files folder: ')
        self.username = input('SSH username: ')
        self.password = getpass.getpass('SSH password: ')

    def load_snippet(self):
        pass

    def load_devices(self):
        pass

