import getpass
import logging.config
import paramiko
import time
from pathlib import Path
from threading import Thread


log_config = {
    'version': 1,
    'formatters': {
        'full': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'main_full_to_file': {
            'class': 'logging.FileHandler',
            'formatter': 'full',
            'filename': 'snippetrun.log',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['main_full_to_file'],
            'level': 'DEBUG',
        },
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger('main')


def time_tracker(function):
    def intermediate(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f'Run time: {round(run_time, 1)} s')
        return result

    return intermediate


class SnippetRun(Thread):
    def __init__(self, ssh_user, ssh_password, device_ip, snippet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.device_ip = device_ip
        self.snippet = snippet

    def ssh_operation(self):
        ssh_client = paramiko.client.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=self.device_ip,
                               username=self.ssh_user,
                               password=self.ssh_password,
                               allow_agent=False)
        except Exception:
            logger.exception(f'Can not connect to {self.device_ip}')
        else:
            print(f'Connected to {self.device_ip}')
            logger.info(f'Connected to {self.device_ip}')
            ssh_session = ssh_client.invoke_shell()
            for command in self.snippet:
                ssh_session.send(command)
                time.sleep(1)
            time.sleep(1)
            ssh_client.close()

    def run(self):
        self.ssh_operation()


class DeviceController:
    def __init__(self):
        self.username = ''
        self.password = ''
        self.snippet = []
        self.devices = []
        self.program_hosting_folder = Path(__file__).parent.resolve()

    def get_credentials(self):
        self.username = input('SSH username: ')
        self.password = getpass.getpass(prompt='SSH password: ')

    def load_snippet(self):
        _snippet_full_path = self.program_hosting_folder / 'snippet.txt'
        with open(file=_snippet_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                if line.endswith('\n'):
                    self.snippet.append(line)
                elif line:
                    self.snippet.append(line + '\n')

    def load_devices(self):
        _devices_full_path = self.program_hosting_folder / 'devices.txt'
        with open(file=_devices_full_path, mode='r', encoding='utf8') as file_content:
            for line in file_content:
                line = line.splitlines()[0]
                if line:
                    self.devices.append(line)

    @time_tracker
    def configure_devices(self):
        _runners = []
        for device_ip in self.devices:
            snippet_runner = SnippetRun(ssh_user=self.username,
                                        ssh_password=self.password,
                                        device_ip=device_ip,
                                        snippet=self.snippet)
            snippet_runner.start()
            _runners.append(snippet_runner)
        for runner in _runners:
            runner.join()

    def run(self):
        self.get_credentials()
        try:
            self.load_snippet()
            self.load_devices()
        except Exception:
            print('Error! See log!')
            logger.exception(f'Loading data error')
        else:
            self.configure_devices()


if __name__ == '__main__':
    controller = DeviceController()
    controller.run()
