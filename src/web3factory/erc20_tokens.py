from typing import List
from web3client.exceptions import (
    Erc20TokenNotFound,
    Erc20TokenNotUnique,
    NetworkNotFound,
)
from web3factory.networks import is_network_supported
from web3factory.types import Erc20TokenConfig


"""
List of supported ERC20 tokens acrosso networks
"""
supported_tokens: List[Erc20TokenConfig] = [
    # Ethereum
    {
        "name": "USDC",
        "network": "ethereum",
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "decimals": 6,
    },
    # Binance
    {
        "name": "BUSD",
        "network": "binance",
        "address": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
        "decimals": 18,
    },
    {
        "name": "BETH",
        "network": "binance",
        "address": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        "decimals": 18,
    },
    # Avalanche
    {
        "name": "USDC",
        "network": "avalanche",
        "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "decimals": 6,
    },
]


def get_token_config(name: str, network: str) -> Erc20TokenConfig:
    """
    Return the configuration for the given token on the given
    network; raises an exception if not found or more than one
    is found
    """
    # Raise if network does not exist
    if not is_network_supported(network):
        raise NetworkNotFound(f"Network '{network}' not supported")
    # Get all tokens with given name and network
    tokens: List[Erc20TokenConfig] = [
        t for t in supported_tokens if t["name"] == name and t["network"] == network
    ]
    # Must have exactly one token
    if len(tokens) == 0:
        raise Erc20TokenNotFound(f"ERC20 token '{name}' on '{network}' not supported")
    if len(tokens) > 1:
        raise Erc20TokenNotUnique(
            f"Found more than one ERC20 token with '{name}' on '{network}' (found '{len(tokens)}')"
        )
    # Return the one token
    return tokens[0]


def is_token_supported(name: str, network: str) -> bool:
    """
    Return true if the given token and network pair is
    supported by the client factory
    """
    try:
        get_token_config(name, network)
        return True
    except Erc20TokenNotFound:
        return False
