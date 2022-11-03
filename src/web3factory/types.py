from typing import List, TypedDict
from typing_extensions import NotRequired
from web3.types import Middleware

NetworkName = str
TokenName = str


class NetworkConfig(TypedDict):
    """
    Dictionary representing the configuration of a network, e.g. Ethereum,
    Avalanche, etc.
    """

    name: NetworkName
    txType: int
    chainId: int
    middlewares: NotRequired[List[Middleware]]
    rpcs: NotRequired[List[str]]
    coin: str


class Erc20TokenConfig(TypedDict):
    """
    Dictionary representing an ERC20 token
    """

    name: TokenName
    network: NetworkName
    address: str
    decimals: int
