from random import choice
from typing import Any, List, cast

from web3.middleware import geth_poa_middleware

from web3client.exceptions import NetworkNotFound
from web3client.helpers.general import findInListOfDicts
from web3factory.types import NetworkConfig

"""
List of supported networks (aka blockchains), each with its own
parameters.
"""
supported_networks: List[NetworkConfig] = [
    # Ethereum
    {
        "name": "eth",
        "tx_type": 2,
        "chain_id": 1,
        "rpcs": [
            "https://cloudflare-eth.com",
        ],
        "coin": "ETH",
    },
    # Avalanche C Chain
    {
        "name": "bnb",
        "tx_type": 1,
        "chain_id": 56,
        "middlewares": [geth_poa_middleware],
        "rpcs": [
            "https://bsc-dataseed.binance.org/",
        ],
        "coin": "BNB",
    },
    # Avalanche C Chain
    {
        "name": "avax",
        "tx_type": 2,
        "chain_id": 43114,
        "middlewares": [geth_poa_middleware],
        "rpcs": [
            "https://api.avax.network/ext/bc/C/rpc",
        ],
        "coin": "AVAX",
    },
    # Arbitrum One
    {
        "name": "arb",
        "tx_type": 2,
        "chain_id": 42161,
        "rpcs": ["https://arb1.arbitrum.io/rpc"],
        "coin": "ETH",
    },
    # zkSync Era
    {
        "name": "era",
        "tx_type": 2,
        "chain_id": 324,
        "rpcs": ["https://mainnet.era.zksync.io"],
        "coin": "ETH",
    },
]


def get_network_config(name: str) -> NetworkConfig:
    """
    Return the configuration for the network with the given
    name; raises an exception if not found
    """
    network: NetworkConfig = findInListOfDicts(
        cast(Any, supported_networks), "name", name
    )
    if network is None:
        raise NetworkNotFound(f"Network '{name}' not supported")
    return network


def pick_random_rpc(network_name: str) -> str:
    """
    Given a network return one of its RPCs, randomly,
    or None, if it has no RPC
    """
    network = get_network_config(network_name)
    rpcs = network.get("rpcs")
    return choice(rpcs) if rpcs else None


def pick_first_rpc(network_name: str) -> str:
    """
    Given a network return its first RPC or None,
    if it has no RPC
    """
    network = get_network_config(network_name)
    rpcs = network.get("rpcs")
    return rpcs[0] if rpcs else None


def is_network_supported(name: str) -> bool:
    """
    Return true if the given network is supported by
    the client factory
    """
    try:
        get_network_config(name)
        return True
    except NetworkNotFound:
        return False
