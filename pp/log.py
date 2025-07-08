'''
A module to create loggers with custom handlers and a custom formatter.

usage examples to initialise a logger:
    ```python
    # 1. initialise logger to stderr:
    logger = getLogger('my_logger', level=logging.DEBUG, stream=sys.stderr)

    # 2. initialise logger to file:
    logger = getLogger('my_logger', level=logging.DEBUG, filename='my_log.log')

    # 3. initialise logger to both stderr and file:
    logger = getLogger('my_logger', level=logging.DEBUG, stream=sys.stderr, files={LogLevel.INFO: 'info.log'})
    ```

usage examples to log messages:
    ```python
    logger.info('This is a basic info message')
    # {"timestamp": "2024-12-09T15:05:43.904417", "msg": "This is a basic info message", "data": {}}

    logger.info('This is an info message', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904600", "msg": "This is an info message", "data": {"key": "value"}}

    logger.debug('This is a debug message', 'arg1', 'arg2', {'key': 'value'})
    # {"timestamp": "2024-12-09T15:05:43.904749", "msg": "This is a debug message", "data": {"args": ["arg1", "arg2"], "key": "value"}}
    ```
'''

from datetime import datetime
import io
import json
import logging
import sys

from pp.pp import _json_default

class LogLevel:
    'An enum type for log levels.'
    CRITICAL = logging.CRITICAL
    ERROR    = logging.ERROR
    WARNING  = logging.WARNING
    INFO     = logging.INFO
    DEBUG    = logging.DEBUG
    NOTSET   = logging.NOTSET


class LogFormatter(logging.Formatter):
    'Custom log formatter that formats log messages as JSON, aka "Structured Logging".'
    def __init__(self, defaults: dict = {}):
        '''
        Initializes the log formatter with optional default context.
        - `defaults` is a dictionary of default context values to include in every log message.
        '''
        self.defaults = defaults
        super().__init__()

    def format(self, record) -> str:
        'Formats the log message as JSON.'

        args, kwargs = None, {}
        if isinstance(record.args, tuple):
            if len(record.args) == 1:
                args = record.args
            elif len(record.args) > 1:
                *args, kwargs = record.args
        elif isinstance(record.args, dict):
            kwargs = record.args

        record.msg = json.dumps(
            {
                'timestamp': datetime.now().isoformat(),
                'level':     record.levelname,
                'name':      record.name,
                'msg':       record.msg,
                'event':     {'args': args} if args else {} | kwargs or {},
                **({'context': self.defaults} if self.defaults else {}),
            },
            default=_json_default,
        )
        record.args = ()
        return super().format(record)


def _getLogger(
    name:     str,
    level:    int                   = logging.CRITICAL,
    handlers: list[logging.Handler] = [],
    context:  dict                  = {},
) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - If no handlers are provided, the logger will not output any logs.
    - This function requires the handlers to be initialized when passed as args.
    - the same log level is applied to all handlers.
    '''

    # create the root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

    # create the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # close/remove any existing handlers
    while logger.handlers:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)

    # add the new handlers
    for handler in handlers:
        logger.addHandler(handler)

    if logger.handlers:
        # only set the first handler to use the custom formatter
        logger.handlers[0].setFormatter(LogFormatter(defaults=context))

    return logger


def getLogger(
    name:     str,
    level:    int                 = logging.INFO,
    stream:   io.TextIOBase       = sys.stderr,
    files:    dict[LogLevel, str] = {},
    context:  dict                = {},
) -> logging.Logger:
    '''
    Creates a logger with the given name, level, and handlers.
    - `name` is the name of the logger.
    - `stream` is the output stream for the logger (default is STDERR).
    - `files` is a dictionary of log levels and filenames for file handlers.
      - The keys are log levels (e.g., LogLevel.INFO, LogLevel.DEBUG).
      - The values are the filenames to log to at the corresponding level.
      - The file handlers will use `TimedRotatingFileHandler` to rotate logs at midnight and keep 7 backups.
    - `level` is the log level for the logger and all handlers (default is INFO).
    '''
    handlers = []
    if stream:
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)
        handlers.append(handler)

    for flevel, filename in files.items():
        handler = logging.handlers.TimedRotatingFileHandler(
            filename, when='midnight', backupCount=7, encoding='utf-8',
        )
        handler.setLevel(flevel)
        handlers.append(handler)

    return _getLogger(name, level, handlers, context=context)
