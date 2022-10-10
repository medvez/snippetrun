import getpass
import logging.config
import os.path
import paramiko
import time
from threading import Thread


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
log_config = {
    'version': 1,
    'formatters': {
        'full': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'full_to_file': {
            'class': 'logging.FileHandler',
            'formatter': 'full',
            'filename': os.path.join(BASE_DIR, 'snippetrun_log.log'),
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'snippetrun': {
            'handlers': ['full_to_file'],
            'level': 'DEBUG',
        },
    },
}

logging.config.dictConfig(log_config)
logger = logging.getLogger('snippetrun')


def time_tracker(function):
    """
    Just decorator to track time function running
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = function(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f'Run time: {round(run_time, 1)} s')
        return result
    return wrapper


def log_handler(message, device_ip=None):
    """
    Control logging behavior
    """
    if device_ip is not None:
        logger.error(f"{device_ip}:{message}", exc_info=False)
        print(f"error on {device_ip} - see log!")
    else:
        logger.error(message, exc_info=False)
        print(message)


class SnippetRun(Thread):
    """
    Run all commands on single device.
    """
    def __init__(self, ssh_user: str, ssh_password: str, device_ip: str, snippet: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.device_ip = device_ip
        self.snippet = snippet

    def ssh_operation(self) -> None:
        _ssh_client = paramiko.client.SSHClient()
        _ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            _ssh_client.connect(hostname=self.device_ip,
                                username=self.ssh_user,
                                password=self.ssh_password,
                                allow_agent=False)
        except paramiko.ssh_exception.AuthenticationException:
            log_handler(message=f'wrong credentials', device_ip=self.device_ip)
        except TimeoutError:
            log_handler(message=f'device is not responding', device_ip=self.device_ip)
        else:
            print(f'Connected to {self.device_ip}')
            with _ssh_client.invoke_shell() as shell_session:
                for command in self.snippet:
                    shell_session.send(command)
                    time.sleep(1)
                time.sleep(1)

    def run(self) -> None:
        self.ssh_operation()


class DeviceController:
    """
    Main class, which combines all operations on all devices.
    It gets credentials from CLI, makes list of devices from file, list of configuration commands from file
    and runs commands on every device in multithreading mode.
    """
    def __init__(self) -> None:
        self.username = ''
        self.password = ''
        self.snippet = []
        self.devices = []

    def get_credentials(self) -> None:
        self.username = input('SSH username: ')
        self.password = getpass.getpass(prompt='SSH password: ')

    def load_snippet(self) -> None:
        with open(file=os.path.join(BASE_DIR, 'snippet.txt'),
                  mode='r',
                  encoding='utf8') as file_content:
            for line in file_content:
                if line.endswith('\n'):
                    self.snippet.append(line)
                elif line:
                    self.snippet.append(line + '\n')

    def load_devices(self) -> None:
        with open(file=os.path.join(BASE_DIR, 'devices.txt'),
                  mode='r',
                  encoding='utf8') as file_content:
            for line in file_content:
                line = line.splitlines()[0]
                if line:
                    self.devices.append(line)

    @time_tracker
    def configure_devices(self) -> None:
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

    def run(self) -> None:
        self.get_credentials()
        try:
            self.load_snippet()
            self.load_devices()
        except FileNotFoundError:
            log_handler(message="can't find txt file")
        except UnicodeDecodeError:
            log_handler(message="txt file is encrypted")
        else:
            self.configure_devices()


if __name__ == '__main__':
    controller = DeviceController()
    controller.run()
