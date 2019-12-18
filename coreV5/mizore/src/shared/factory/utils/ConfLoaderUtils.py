"""
This class handles loading the config files for other modules to read.
"""

import toml
import yaml

from src.shared.factory.utils.DockerUtils import DockerUtils #pylint: disable=import-error

class ConfLoaderUtils:

    # The different auth files we will need to load
    _AUTH = None
    _IZUMI = None
    _ENCODER = None

    _auth_path = "conf/auth.yml"
    _izumi_path = "conf/izumi.toml"
    _encoder_path = "conf/encoder.toml"

    if DockerUtils.docker:
        _auth_path = DockerUtils.path + _auth_path
        _izumi_path = DockerUtils.path + _izumi_path
        _encoder_path = DockerUtils.path + _encoder_path

    # Load the auth yaml file
    with open(_auth_path) as ayml:
        _AUTH = yaml.load(ayml, Loader=yaml.BaseLoader)

    # Load the Shared Master Izumi conf file
    with open(_izumi_path) as iml:
        _IZUMI = toml.load(iml)

    # Load Encoder conf file
    with open(_encoder_path) as eml:
        _ENCODER = toml.load(eml)

    @classmethod
    def get_auth(cls) -> dict:
        return cls._AUTH

    @classmethod
    def get_izumi(cls) -> dict:
        return cls._IZUMI

    @classmethod
    def get_encoder(cls) -> dict:
        return cls._ENCODER