from team_splitter.version import __version__
from .cli import main
from .logging_config import initialize_logging
#import importlib.metadata


def get_package_version():
    # try:
    #     v = importlib.metadata.version(get_package_name())
    # except importlib.metadata.PackageNotFoundError:
    #     return __version__

    # return __version__ if v is None else v
    return __version__


initialize_logging()
