from pathlib import Path
from typing import Any, Dict

import yaml


def read_configuration() -> Dict[str, Any]:
    configuration = {}
    config_path = Path(__file__).parent.parent / "config.yml"
    with open(config_path, "r", encoding="utf-8") as file:
        configuration = yaml.safe_load(file)

    return configuration

def get_service_url(configuration: Dict[str, Any], endpoint_name: str) -> str:
    return f"{configuration['vectorize']['endpoint_url']}api/v1/{endpoint_name}"
