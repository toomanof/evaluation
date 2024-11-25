import importlib
import os
import yaml
from logging import config as loging_config
from glob import glob

from core.project.utils import import_string


class Settings:
    def __init__(self):
        self.DEFAULT_LIST_SQL_CREATE_TABLES = []
        self.load_settings()
        for key, val in self.get_yml_config().items():
            setattr(self, key, val)
        self.list_tables_to_be_created()
        self.set_routes()
        self.set_middlewares()
        loging_config.dictConfig(getattr(self, "LOGGING_CONFIG"))

    def load_settings(self):
        global_settings = importlib.import_module("core.settings.__init__")
        for setting in dir(global_settings):
            if setting.isupper():
                setattr(self, setting, getattr(global_settings, setting))

    def get_yml_config(self):
        result = {}
        for file_yml in glob(os.path.join(getattr(self, "PATH_SETTINGS"), "*.yml")):
            with open(file_yml) as f_yaml:
                result |= yaml.safe_load(f_yaml) or {}
        return result

    def list_tables_to_be_created(self):
        self.DEFAULT_LIST_SQL_CREATE_TABLES = []
        for path in glob(f"{getattr(self, 'PATH_APPS')}/*"):
            path_models = os.path.join(path, getattr(self, "DEFAULT_DIR_FOR_MODELS"))
            if not os.path.exists(path_models):
                continue

            for file_module in glob(f"{path_models}/*.py"):
                list_path_model = file_module.split("/")[-5:]
                list_path_model[-1] = list_path_model[-1].removesuffix(".py")
                module = ".".join(list_path_model)
                try:
                    tables_in_module = import_string(f"{module}.{getattr(self, 'DEFAULT_VAR_SQL_CREATE_TABLES')}")
                except ImportError:
                    pass
                else:
                    self.DEFAULT_LIST_SQL_CREATE_TABLES.extend(tables_in_module)

    def set_routes(self):
        setattr(
            self,
            "ROUTES",
            import_string(f"{getattr(self, 'ROOT_URLCONF')}.{getattr(self, 'DEFAULT_VAR_ROUTES')}"),
        )

    def set_middlewares(self):
        setattr(
            self,
            "MIDDLEWARE",
            [import_string(middleware) for middleware in getattr(self, "MIDDLEWARE")],
        )


settings = Settings()
