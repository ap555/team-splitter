import os
import platform
from logging.config import dictConfig
from pathlib import Path


def initialize_logging():
    localappdata_path = os.getenv('LOCALAPPDATA') if platform.system(
    ) == "Windows" else os.path.join(Path.home(), '.local')
    company_name = '828'
    package_name = 'team_splitter'

    log_folder = Path(localappdata_path) / company_name / package_name
    if not log_folder.exists():
        log_folder.mkdir(parents=True)

    log_path = log_folder / f'{package_name}.txt'

    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s:%(levelname)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                # 'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_path,
                'maxBytes': 10000000,
                'backupCount': 2,
                # 'level': 'INFO',
                'formatter': 'default',
                "encoding": "utf-8"
            },
        },
        'root': {                                     # ← configure root here
            'level': 'INFO',                         # or DEBUG, whatever you need
            'handlers': ['console', 'file'],
        },
    })
