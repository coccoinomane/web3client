from typing import Dict

import pytest

from web3client.base_client import BaseClient

ethereum_foundation = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"


@pytest.mark.remote
def test_get_nonce(networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        nonce = client.get_nonce(ethereum_foundation)
        assert type(nonce) is int
        assert nonce >= 0


@pytest.mark.remote
def test_get_latest_block(networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        block = client.get_latest_block()
        assert type(block.get("number")) is int
        assert block.get("number") >= 0
        assert type(block.get("size")) is int
        assert block.get("size") >= 0
        assert type(block.get("difficulty")) is int
        assert block.get("difficulty") >= 0
        assert type(block.get("transactions")) is list


@pytest.mark.remote
def test_get_eth_balance(networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        balance = client.get_balance_in_wei(ethereum_foundation)
        assert type(balance) is int
        assert balance >= 0
