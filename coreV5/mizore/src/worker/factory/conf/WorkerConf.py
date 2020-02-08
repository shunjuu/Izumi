#pylint: disable=import-error,no-self-argument,unsubscriptable-object
"""
File that loads worker configurations. This is exclusively for the WORKER segments.
Separate becaues ConfPickleUtils loads all configs, which we don't want.
"""

import toml

from typing import List

from astropy.utils.decorators import classproperty
from src.shared.factory.utils.DockerUtils import DockerUtils

class WorkerConf:

    _WORKER_CONF = None
    _worker_path = "conf/worker.toml"

    if DockerUtils.docker:
        _worker_path = DockerUtils.path + _worker_path

    # Load the worker file
    with open(_worker_path) as wml:
        _WORKER_CONF = toml.load(wml)

    # Properties

    @classproperty
    def redis_host(cls) -> str:
        return str(cls._WORKER_CONF['redis']['host'])

    @classproperty
    def redis_port(cls) -> int:
        return int(cls._WORKER_CONF['redis']['port'])

    @classproperty
    def redis_password(cls) -> str:
        return str(cls._WORKER_CONF['redis']['password'])

