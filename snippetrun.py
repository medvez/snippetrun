import paramiko
import getpass
import time
import os.path


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
        self.password = getpass.getpass(prompt='SSH password: ')

    def load_snippet(self):
        _snippet_full_path = os.path.join(self.data_folder_path, 'snippet.txt')
        with open(file=_snippet_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                self.snippet.append(line)

    def load_devices(self):
        _devices_full_path = os.path.join(self.data_folder_path, 'devices.txt')
        with open(file=_devices_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                if line:
                    self.devices.append(line[:-1])

    def ssh_operation(self, device_ip):
        ssh_client = paramiko.client.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print('Connecting to', device_ip)
        ssh_client.connect(hostname=device_ip, username=self.username, password=self.password)
        print('Connected!')
        ssh_session = ssh_client.invoke_shell()
        time.sleep(1)
        for command in self.snippet:
            ssh_session.send(command)
            time.sleep(1)
        time.sleep(4)
        ssh_client.close()

    def configure_devices(self):
        for device_ip in self.devices:
            self.ssh_operation(device_ip)

    def run(self):
        self.get_credentials()
        self.load_snippet()
        self.load_devices()
        self.configure_devices()


if __name__ == '__main__':
    snippet_run = SnippetRun()
    snippet_run.run()