"""
Zerodha WebSocket streaming module for TradeOS.

This module provides WebSocket integration with Zerodha's market data streaming API,
following the TradeOS WebSocket proxy architecture.
"""

from .zerodha_adapter import ZerodhaWebSocketAdapter

__all__ = ["ZerodhaWebSocketAdapter"]
