from typing import Any, Awaitable, Callable, Literal

from web3.types import TxData

SubscriptionType = Literal[
    "newHeads", "newPendingTransactions", "logs", "alchemy_newPendingTransactions"
]

SubscriptionCallback = Callable[[Any, SubscriptionType, TxData], None]
AsyncSubscriptionCallback = Callable[[Any, SubscriptionType, TxData], Awaitable[None]]
