from setuptools_scm import get_version
from setuptools_scm.version import ScmVersion


def _pmi_version_scheme(version: ScmVersion) -> str:
    return f'{version.tag}.{version.distance}'


def _pmi_local_scheme(version: ScmVersion) -> str:
    return f'+{version.node[:7]}' if version.node else ''


def _scm_version():
    try:
        return get_version(
            root="../..",
            version_scheme=_pmi_version_scheme,
            local_scheme=_pmi_local_scheme,
            fallback_version="0.0.0+g0",
            search_parent_directories=True,
        )
    except LookupError:
        return None


__version__ = _scm_version()
