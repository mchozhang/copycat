import os
import yaml


class Config:
    def __init__(self):
        config = Config.load_config()
        self.server_url = os.environ.get("COPYCAT_SERVER_URL") or config.get("server_url")
        self.user_id = os.environ.get("COPYCAT_USER_ID") or config.get("user_id")
        self.api_key = os.environ.get("COPYCAT_API_KEY") or config.get("api_key")

    @staticmethod
    def load_config():
        """
        Load config from config.yaml into the Config instance, env vars take precedence.
        """
        xdg = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
        config_path = os.path.join(xdg, "copycat", "config.yaml")

        if not os.path.isfile(config_path):
            return {}

        with open(config_path) as f:
            config = yaml.safe_load(f) or dict()
        return config
