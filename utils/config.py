import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    """
    Loads the YAML configuration file.

    Args:
        path: The path to the configuration file.

    Returns:
        A dictionary containing the configuration.
    """
    config_path = Path(path)
    if not config_path.exists():
        # In a real-world application, you might want to create a default
        # config file here or raise a more specific error.
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
