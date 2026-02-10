# utils/plugin_loader.py
#
# Dynamically loads broker plugins from the broker/ directory.
# Each broker has a plugin.json with metadata including:
#   - "enabled": true/false — whether the broker is active
#   - "region": "IN"/"US"/"GLOBAL" — geographic region of the broker
#
# Indian brokers (region="IN") are disabled by default. Set
# ENABLE_INDIAN_BROKERS=true in .env to load them.

import importlib
import json
import os

from flask import current_app

from utils.logging import get_logger

logger = get_logger(__name__)


def _is_broker_enabled(broker_path, broker_name):
    """Check if a broker should be loaded based on its plugin.json settings.

    A broker is enabled if:
    1. It has no plugin.json (legacy broker, assumed enabled)
    2. Its plugin.json has "enabled": true
    3. Its plugin.json has "region": "IN" AND ENABLE_INDIAN_BROKERS=true in .env

    Returns True if the broker should be loaded, False otherwise.
    """
    plugin_json_path = os.path.join(broker_path, broker_name, "plugin.json")

    if not os.path.exists(plugin_json_path):
        # Legacy broker without plugin.json — load it (backwards compatible)
        return True

    try:
        with open(plugin_json_path) as f:
            plugin_data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Could not read plugin.json for {broker_name}: {e}")
        return True  # Default to enabled if plugin.json is unreadable

    # Check the enabled flag
    enabled = plugin_data.get("enabled", True)

    if not enabled:
        # Check if this is an Indian broker that can be enabled via env var
        region = plugin_data.get("region", "")
        if region == "IN":
            enable_indian = os.getenv("ENABLE_INDIAN_BROKERS", "false").lower() == "true"
            if enable_indian:
                logger.info(f"Indian broker {broker_name} enabled via ENABLE_INDIAN_BROKERS")
                return True
        return False

    return True


def load_broker_auth_functions(broker_directory="broker"):
    auth_functions = {}
    broker_path = os.path.join(current_app.root_path, broker_directory)
    # List all items in broker directory and filter out __pycache__ and non-directories
    broker_names = [
        d
        for d in os.listdir(broker_path)
        if os.path.isdir(os.path.join(broker_path, d)) and d != "__pycache__"
    ]

    for broker_name in broker_names:
        # Check if broker is enabled via plugin.json
        if not _is_broker_enabled(broker_path, broker_name):
            logger.debug(f"Broker {broker_name} is disabled in plugin.json, skipping")
            continue

        try:
            # Construct module name and import the module
            module_name = f"{broker_directory}.{broker_name}.api.auth_api"
            auth_module = importlib.import_module(module_name)
            # Retrieve the authenticate_broker function
            auth_function = getattr(auth_module, "authenticate_broker", None)
            if auth_function:
                auth_functions[f"{broker_name}_auth"] = auth_function
        except ImportError as e:
            logger.error(f"Failed to import broker plugin {broker_name}: {e}")
        except AttributeError as e:
            logger.error(f"Authentication function not found in broker plugin {broker_name}: {e}")

    return auth_functions
