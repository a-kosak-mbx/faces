import yaml

from bootstrap.db import reset as reset_db
from bootstrap.s3 import reset as reset_s3, fill as fill_s3


def main():
    # Read configuration file.
    configuration = {}
    with open("config.yml", "r", encoding="utf-8") as f:
        configuration = yaml.safe_load(f)

    if configuration:
        # Reset database.
        reset_db(configuration)
        reset_s3(configuration)
        fill_s3(configuration)


if __name__ == "__main__":
    main()
