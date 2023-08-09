from typing import Dict

import pytest

from web3client.base_client import BaseClient
from web3factory.factory import make_client
from web3factory.networks import supported_networks


@pytest.fixture()
def rpcs() -> Dict[str, str]:
    """
    Let's use difrerent RPCs for tests, in case the regular ones
    are throttled
    """
    return {
        "eth": "https://mainnet.infura.io/v3/db0e363aad2f43ee8a2f259733721512",
    }


@pytest.fixture()
def networks_clients(rpcs: Dict[str, str]) -> Dict[str, BaseClient]:
    """
    Ready-to-use clients, indexed by network name, no signer
    """
    clients = {}
    for network in supported_networks:
        name = network["name"]
        node_uri = rpcs.get(name)
        clients[name] = make_client(name, node_uri)
    return clients
