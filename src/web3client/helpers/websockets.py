import json
from typing import Any, Callable

from websockets.client import WebSocketClientProtocol

from web3client.exceptions import Web3ClientException


async def subscribe_to_notification(
    ws: WebSocketClientProtocol,
    type: str,
    on_subscribe: Callable[[Any], None] = None,
) -> str:
    """Given a websocket connection to an RPC, subscribe to the given
    notification type, and return the subscription id.

    Optinally, call the given callback with the subscription response."""
    # Subscribe to the notification type
    await ws.send(
        '{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["'
        + type
        + '"]}'
    )
    subscription_response = await ws.recv()
    try:
        subscription_id = json.loads(subscription_response)["result"]
    except Exception as e:
        raise Web3ClientException(f"Failed to subscribe to {type}: {e}")
    # Call on_subscribe callback
    if on_subscribe:
        on_subscribe(json.loads(subscription_response))
    return subscription_id
