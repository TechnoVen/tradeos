# Mapping TradeOS API Request https://tradeos.io/docs
# FivePaisaXTS does not provide Margin Calculator API

from utils.logging import get_logger

logger = get_logger(__name__)


def transform_margin_positions(positions):
    """
    Transform TradeOS margin position format to broker format.

    Note: FivePaisaXTS does not provide a margin calculator API.

    Args:
        positions: List of positions in TradeOS format

    Raises:
        NotImplementedError: FivePaisaXTS does not support margin calculator API
    """
    raise NotImplementedError("FivePaisaXTS does not support margin calculator API")


def parse_margin_response(response_data):
    """
    Parse broker margin calculator response to TradeOS standard format.

    Note: FivePaisaXTS does not provide a margin calculator API.

    Args:
        response_data: Raw response from broker margin calculator API

    Raises:
        NotImplementedError: FivePaisaXTS does not support margin calculator API
    """
    raise NotImplementedError("FivePaisaXTS does not support margin calculator API")
