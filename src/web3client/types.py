from typing import Literal

SubscriptionType = Literal[
    "newHeads", "newPendingTransactions", "logs", "alchemy_newPendingTransactions"
]
