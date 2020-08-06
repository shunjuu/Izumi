"""
This class handles loading the config files for other modules to read.
"""

import toml
import yaml

from src.shared.factory.utils.DockerUtils import DockerUtils #pylint: disable=import-error

class ConfLoaderUtils:

    # The different auth files we will need to load
    _AUTH = None
    _DASHBOARD_AUTH = None
    _RCLONE = None
    _IZUMI = None
    _ENCODER = None
    _NOTIFIER = None
    _DISTRIBUTOR = None

    _auth_path = "conf/auth.yml"
    _dashboard_auth_path = "conf/dashboard_auth.yml"
    _rclone_path = "conf/rclone.conf"
    _izumi_path = "conf/izumi.toml"
    _encoder_path = "conf/encoder.toml"
    _notifier_path = "conf/notifier.toml"
    _distributor_path = "conf/distributor.toml"

    if DockerUtils.docker:
        _auth_path = DockerUtils.path + _auth_path
        _dashboard_auth_path = DockerUtils.path + _dashboard_auth_path
        _rclone_path = DockerUtils.path + _rclone_path
        _izumi_path = DockerUtils.path + _izumi_path
        _encoder_path = DockerUtils.path + _encoder_path
        _notifier_path = DockerUtils.path + _notifier_path
        _distributor_path = DockerUtils.path + _distributor_path

    # Load the auth yaml file
    with open(_auth_path) as ayml:
        _AUTH = yaml.load(ayml, Loader=yaml.BaseLoader) or dict()

    # Load the dashboard yaml file
    with open(_dashboard_auth_path) as dayml:
        _DASHBOARD_AUTH = yaml.load(dayml, Loader=yaml.BaseLoader) or dict()

    # Load rclone conf just purely as a string
    with open(_rclone_path) as rconf:
        _RCLONE = rconf.read()

    # Load the Shared Master Izumi conf file
    with open(_izumi_path) as iml:
        _IZUMI = toml.load(iml)

    # Load Encoder conf file
    with open(_encoder_path) as eml:
        _ENCODER = toml.load(eml)

    # Load Notifier conf file
    with open(_notifier_path) as nml:
        _NOTIFIER = toml.load(nml)

    # Load Distributor conf file
    with open(_distributor_path) as dml:
        _DISTRIBUTOR = toml.load(dml)

    @classmethod
    def get_auth(cls) -> dict:
        return cls._AUTH

    @classmethod
    def get_dashboard_auth(cls) -> dict:
        return cls._DASHBOARD_AUTH

    @classmethod
    def get_rclone(cls) -> str:
        return cls._RCLONE

    @classmethod
    def get_izumi(cls) -> dict:
        return cls._IZUMI

    @classmethod
    def get_encoder(cls) -> dict:
        return cls._ENCODER

    @classmethod
    def get_notifier(cls) -> dict:
        return cls._NOTIFIER

    @classmethod
    def get_distributor(cls) -> dict:
        return cls._DISTRIBUTOR