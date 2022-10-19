from typing import List, TypedDict
from typing_extensions import NotRequired
from web3.types import Middleware


class NetworkConfig(TypedDict):
    """
    Dictionary representing the configuration of a network, e.g. Ethereum,
    Avalanche, etc.
    """

    name: str
    txType: int
    chainId: int
    middlewares: NotRequired[List[Middleware]]
    rpcs: NotRequired[List[str]]
