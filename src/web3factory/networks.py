from random import choice
from typing import Any, List, cast
from web3client.helpers.general import findInListOfDicts
from web3client.exceptions import NetworkNotFound
from web3factory.types import NetworkConfig
from web3.middleware import geth_poa_middleware


"""
List of supported networks (aka blockchains), each with its own
parameters.
"""
supported_networks: List[NetworkConfig] = [
    # Ethereum
    {
        "name": "ethereum",
        "txType": 2,
        "chainId": 1,
        "rpcs": [
            "https://mainnet.infura.io/v3/98c23dcc2c3947cbacc2a0c7e1b1757a",
            "https://ethereum-mainnet--rpc.datahub.figment.io/apikey/cfd6d301706d81d97fd78bced8211f27",
        ],
        "coin": "ETH",
    },
    # Avalanche C Chain
    {
        "name": "binance",
        "txType": 1,
        "chainId": 56,
        "middlewares": [geth_poa_middleware],
        "rpcs": [
            "https://bsc-dataseed.binance.org/",
            "https://bsc--mainnet--rpc.datahub.figment.io/apikey/1e03acdcb04656b9412009ac14b1a201",
        ],
        "coin": "BNB",
    },
    # Avalanche C Chain
    {
        "name": "avalanche",
        "txType": 2,
        "chainId": 43114,
        "middlewares": [geth_poa_middleware],
        "rpcs": [
            "https://api.avax.network/ext/bc/C/rpc",
            "https://avalanche-mainnet.infura.io/v3/98c23dcc2c3947cbacc2a0c7e1b1757a",
            "https://avalanche--mainnet--rpc.datahub.figment.io/apikey/cfd6d301706d81d97fd78bced8211f27/ext/bc/C/rpc",
        ],
        "coin": "AVAX",
    },
    # Swimmer Network Avalanche subnet
    {
        "name": "swimmer",
        "txType": 1,
        "chainId": 73772,
        "middlewares": [geth_poa_middleware],
        "rpcs": ["https://avax-cra-rpc.gateway.pokt.network"],
        "coin": "TUS",
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


def pick_rpc(network_name: str) -> str:
    """
    Given a network return one of its RPCs, randomly,
    or None, if it has no RPC
    """
    network = get_network_config(network_name)
    rpcs = network.get("rpcs")
    return choice(rpcs) if rpcs else None


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
