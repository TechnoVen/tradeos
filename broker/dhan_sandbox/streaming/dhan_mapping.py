"""
Mapping utilities for Dhan broker integration.
Provides exchange code mappings between TradeOS and Dhan formats.
"""

from typing import Dict

# Exchange code mappings
# TradeOS exchange code -> Dhan exchange code
TRADEOS_TO_DHAN_EXCHANGE = {
    "NSE": "NSE_EQ",
    "BSE": "BSE_EQ",
    "NFO": "NSE_FNO",
    "BFO": "BSE_FNO",
    "CDS": "NSE_CURRENCY",
    "BCD": "BSE_CURRENCY",
    "MCX": "MCX_COMM",
    "NSE_INDEX": "IDX_I",
    "BSE_INDEX": "IDX_I",
}

# Dhan exchange code -> TradeOS exchange code
DHAN_TO_TRADEOS_EXCHANGE = {v: k for k, v in TRADEOS_TO_DHAN_EXCHANGE.items()}


def get_dhan_exchange(tradeos_exchange: str) -> str:
    """
    Convert TradeOS exchange code to Dhan exchange code.

    Args:
        tradeos_exchange (str): Exchange code in TradeOS format

    Returns:
        str: Exchange code in Dhan format
    """
    return TRADEOS_TO_DHAN_EXCHANGE.get(tradeos_exchange, tradeos_exchange)


def get_tradeos_exchange(dhan_exchange: str) -> str:
    """
    Convert Dhan exchange code to TradeOS exchange code.

    Args:
        dhan_exchange (str): Exchange code in Dhan format

    Returns:
        str: Exchange code in TradeOS format
    """
    return DHAN_TO_TRADEOS_EXCHANGE.get(dhan_exchange, dhan_exchange)
