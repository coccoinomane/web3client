"""
Define shared state for all tests
"""
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
        "ethereum": "https://mainnet.infura.io/v3/db0e363aad2f43ee8a2f259733721512",
    }


@pytest.fixture()
def address() -> str:
    return "0x3A8c8833Abe2e8454F59574A2A18b9bA8A28Ea4F"


@pytest.fixture()
def private_key() -> str:
    return "53caa63985c6089c84be07e3f42d5d7ebd47a8a097835ede937d4c5e1f1021dd"


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
