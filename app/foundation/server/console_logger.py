import logging


__all__ = ['ConsoleLogger']


class ConsoleLogger(object):

    def __init__(self, name=None):
        self._logger = logging.getLogger(name) if name else logging.root

    def logger(self, name):
        return ConsoleLogger(name)

    def log_struct(self, info, *, client=None, **kwargs):
        severity = info.pop('severity', 'INFO')
        if severity == 'ERROR':
            self._logger.error(info)
            return

        if severity == 'INFO':
            self._logger.info(info)
            return

        if severity == 'DEBUG':
            self._logger.debug(info)
            return

        if severity == 'WARNING':
            self._logger.warning(info)
            return
        if severity == 'CRITICAL':
            self._logger.critical(info)
            return
        raise RuntimeError(f"Unknown severity {severity}")

    def log_text(self, text):
        self._logger.info(text)
