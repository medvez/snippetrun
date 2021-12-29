import paramiko
import getpass
import time
import os


def time_tracker(function):
    def intermediate(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f'Run time: {round(run_time, 1)} s')
        return result

    return intermediate


class SnippetRun:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.data_folder_path = ''
        self.snippet = []
        self.devices = []

    def get_credentials(self):
        self.username = input('SSH username: ')
        self.password = getpass.getpass(prompt='SSH password: ')

    def load_snippet(self):
        _norm_path = os.path.normpath('load_data/snippet.txt')
        _snippet_full_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], _norm_path)
        with open(file=_snippet_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                if line.endswith('\n'):
                    self.snippet.append(line)
                elif line:
                    self.snippet.append(line + '\n')

    def load_devices(self):
        _norm_path = os.path.normpath('load_data/devices.txt')
        _devices_full_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], _norm_path)
        with open(file=_devices_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                line = line.splitlines()[0]
                if line:
                    self.devices.append(line)

    def ssh_operation(self, device_ip):
        ssh_client = paramiko.client.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f'Connecting to {device_ip}...')
        ssh_client.connect(hostname=device_ip, username=self.username, password=self.password)
        print('Connected!')
        ssh_session = ssh_client.invoke_shell()
        for command in self.snippet:
            ssh_session.send(command)
            time.sleep(1)
        time.sleep(2)
        ssh_client.close()

    def configure_devices(self):
        for device_ip in self.devices:
            self.ssh_operation(device_ip)

    @time_tracker
    def run(self):
        self.get_credentials()
        try:
            self.load_snippet()
            self.load_devices()
            self.configure_devices()
        except Exception as exc:
            print(exc)


if __name__ == '__main__':
    snippet_run = SnippetRun()
    snippet_run.run()
