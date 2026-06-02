import json
from pathlib import Path


class AppSettings:

    SETTINGS_FILE = (
        Path("settings/settings.json")
    )

    @classmethod
    def load(cls):

        if not cls.SETTINGS_FILE.exists():

            return {}

        with open(
            cls.SETTINGS_FILE,
            "r"
        ) as f:

            return json.load(f)

    @classmethod
    def save(cls, data):

        cls.SETTINGS_FILE.parent.mkdir(
            exist_ok=True
        )

        with open(
            cls.SETTINGS_FILE,
            "w"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )