import abc
import argparse
import asyncio
import logging as local_logging
import logging.config
import os
import signal
import traceback
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from sys import _current_frames
from typing import Union

from google.auth import default
from google.cloud import firestore
from google.cloud import logging as cloud_logging

from .config import AppConfig
from .console_logger import ConsoleLogger
from ..env import is_debug, is_test, is_cloud, port, get_env


__all__ = ['AsyncServer']


logger = logging.getLogger(__name__)


def handler(signum, frame):
    print("====================================================\n")
    print("*** STACKTRACE - START ***")
    code = []
    for threadId, stack in _current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append(f'File: "{filename}:{lineno}", in {name}')
            if line:
                code.append("  %s" % (line.strip()))

    for line in code:
        print(line)
    print("\n*** STACKTRACE - END ***")
    print("====================================================\n")
    raise KeyboardInterrupt()


class AsyncServer(metaclass=abc.ABCMeta):

    def __init__(self):
        signal.signal(signal.SIGINT, handler)
        _ = self.logging_client
        logger.info('Init %s', self.name)

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    @cached_property
    def logger(self):
        return self.logging_client.logger('main')

    @cached_property
    def logging_client(self) -> Union[cloud_logging.Client, ConsoleLogger]:
        if self.config['cloud']:
            local_logging.root.handlers.clear()
            logging_client = cloud_logging.Client()
            logging_client.get_default_handler()
            logging_client.setup_logging(log_level=logging.DEBUG if self.config['debug'] else logging.INFO)
            logging.getLogger("httpx").setLevel(logging.WARNING)
            return logging_client

        local_logging.root.handlers.clear()
        ch = local_logging.StreamHandler()
        ch.setLevel(logging.DEBUG if self.config['debug'] else logging.INFO)
        ch.setFormatter(logging.Formatter(style='{', fmt='{levelname:8}{lineno:5}:{filename:30}{message}'))

        local_logging.root.addHandler(ch)
        local_logging.root.setLevel(logging.DEBUG if self.config['debug'] else logging.INFO)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        return ConsoleLogger()

    @cached_property
    def loop(self):
        loop = asyncio.get_event_loop()
        loop.set_default_executor(self.loop_executor)
        return loop

    @cached_property
    def loop_executor(self):
        return ThreadPoolExecutor(max_workers=self.config.concurrency or os.cpu_count())

    @cached_property
    def args(self):
        credentials, project_id = default()
        parser = argparse.ArgumentParser(prog=self.name)
        parser.add_argument('-d', '--debug', help='Run in debug mode', default=bool(is_debug()), action='store_true')
        parser.add_argument('-c', '--config', help="Path to config file", default='config.yml')
        parser.add_argument('-p', '--port', help="Port to listen", default=int(port()), type=int)
        parser.add_argument('--cloud', help="Run in cloud mode", default=bool(is_cloud()), action='store_true')
        parser.add_argument('--dry-run', help='Run in dry-run mode', default=bool(is_test()), action='store_true')
        parser.add_argument('--project-id', help='Google Cloud project ID', default=str(get_env('GOOGLE_CLOUD_PROJECT', project_id)))
        parser.add_argument('--region', help='Google Cloud region', default=str(get_env('GOOGLE_CLOUD_REGION', 'us-central1')))
        self.add_arguments(parser)
        args, _ = parser.parse_known_args()
        return dict(vars(args))

    @cached_property
    def config(self):
        cfg = AppConfig()
        cfg.load_yml(self.args['config'])
        cfg.load_db(firestore.Client())
        for a in ['debug', 'cloud', 'project_id', 'region']:
            cfg[a] = self.args[a]
        return cfg

    def check_config(self):
        # Check config every 5 minutes
        self.loop.call_later(300, self.check_config)
        try:
            if self.config.load_db(firestore.Client()):
                logger.critical("Config update detected. Stop")
                signal.raise_signal(signal.SIGTERM)
            logger.debug(f"Config is the same.")
        except Exception as error:
            logger.warning(f"An error occurred when updating the config - {error}")

    @property
    def name(self):
        return self.__class__.__name__

    def __call__(self, *args, **kwargs):
        return self.run()

    def run(self) -> int:
        try:
            if self.args['cloud']:
                logger.warning(f'Start {self.name}')
            else:
                logger.warning(f'Start {self.name}\n {self.config}')
            if self.args['dry_run']:
                logger.info('Dry run of %s complete', self.name)
                return 0

            self.loop.call_later(1, self.check_config)
            with self.loop_executor:
                return self.execute()
        except KeyboardInterrupt:
            logger.info('Interrupted %s', self.name)
        except Exception as err:
            logger.error(err, exc_info=err)
            raise
        return 1

    def execute(self):
        try:
            return self.loop.run_forever()
        finally:
            self.loop.close()

