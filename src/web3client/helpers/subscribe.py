import json
from typing import Any, Callable, Dict, List, Tuple, Union

from websockets.client import WebSocketClientProtocol

from web3client.exceptions import Web3ClientException
from web3client.types import SubscriptionType


async def subscribe_to_notification(
    ws: WebSocketClientProtocol,
    type: SubscriptionType,
    on_subscribe: Callable[[Any, SubscriptionType], None] = None,
    logs_addresses: List[str] = None,
    logs_topics: List[str] = None,
) -> str:
    """Given a websocket connection to an RPC, subscribe to the given
    notification type, and return the subscription id.

    Optinally, call the given callback with the subscription response."""
    # Build subsciption params
    params: Dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": [type],
    }
    # Add logs filter if needed
    if type == "logs":
        logs_args: Dict[str, Any] = {}
        if logs_addresses:
            logs_args["address"] = logs_addresses
        if logs_topics:
            logs_args["topics"] = logs_topics
        params["params"].append(logs_args)
    # Subscribe to the notification type
    await ws.send(json.dumps(params))
    subscription_response = await ws.recv()
    try:
        subscription_id = json.loads(subscription_response)["result"]
    except Exception as e:
        raise Web3ClientException(f"Failed to subscribe to {type}: {e}")
    # Call on_subscribe callback
    if on_subscribe:
        on_subscribe(json.loads(subscription_response), type)
    return subscription_id


def parse_notification(
    notification: Union[str, bytes], type: SubscriptionType
) -> Tuple[str, Any]:
    """Given a notification, return the subscription ID and
    notification data"""
    try:
        as_dict = json.loads(notification)
    except json.JSONDecodeError as e:
        raise Web3ClientException(
            f"Notification from websocket is malformed: {notification!r}"
        )

    try:
        subscription_id = as_dict["params"]["subscription"]
    except KeyError:
        raise Web3ClientException(
            f"Cannot extract 'subscription' field from websocket notification: {notification!r}"
        )

    try:
        data = as_dict["params"]["result"]
    except KeyError:
        raise Web3ClientException(
            f"Cannot extract 'result' field from websocket notification: {notification!r}"
        )

    return subscription_id, data
