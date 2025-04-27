import os
import configparser

DEFAULT_CONFIG_PATH = "/var/opt/kaspersky/config.ini"

class ConfigLoader:
    """
    Загружает ini-файл, позволяет получать секции и значения параметров.
    Путь к файлу берется из переменной окружения CONFIG_PATH или по умолчанию.
    """
    def __init__(self, path: str = None):
        self.config_path = path or os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        self.config.read(self.config_path)

    def get_section(self, section_name: str) -> configparser.SectionProxy:
        if not self.config.has_section(section_name):
            raise ValueError(f"Section '{section_name}' not found in config")
        return self.config[section_name]

    def get_value(self, section: str, key: str) -> str:
        if not self.config.has_section(section):
            raise ValueError(f"Section '{section}' missing")
        if key not in self.config[section]:
            raise ValueError(f"Key '{key}' missing in section '{section}'")
        return self.config[section][key]