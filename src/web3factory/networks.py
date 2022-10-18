from typing import Any, List, cast
from web3client.helpers.general import findInListOfDicts
from web3client.exceptions import NetworkNotFound
from web3client.types import NetworkConfig
from web3.middleware import geth_poa_middleware

supported_networks: List[NetworkConfig] = [
    # Ethereum
    {
        "name": "Ethereum",
        "txType": 1,
        "chainId": 1,
        "middlewares": [],
    },
    # Avalanche C Chain
    {
        "name": "Avalanche",
        "txType": 2,
        "chainId": 43114,
        "middlewares": [geth_poa_middleware],
    },
    # Swimmer Network Avalanche subnet
    {
        "name": "Swimmer Network",
        "txType": 1,
        "chainId": 73772,
        "middlewares": [geth_poa_middleware],
    },
]


def get_network_config(networkName: str) -> NetworkConfig:
    """
    Return the configuration for the network with the given
    name; raises an exception if not found
    """
    network: NetworkConfig = findInListOfDicts(
        cast(Any, supported_networks), "name", networkName
    )
    if network is None:
        raise NetworkNotFound(f"Network '{networkName}' not supported")
    return network


def is_network_supported(networkName: str) -> bool:
    """
    Return true if the given network is supported by the client
    """
    try:
        get_network_config(networkName)
        return True
    except NetworkNotFound:
        return False
