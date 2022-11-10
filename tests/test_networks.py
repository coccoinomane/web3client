from typing import Dict
from web3client.base_client import BaseClient


def test_get_nonce(address: str, networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        nonce = client.getNonce(address)
        assert type(nonce) is int
        assert nonce >= 0


def test_get_latest_block(networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        block = client.getLatestBlock()
        assert type(block.get("number")) is int
        assert block.get("number") >= 0
        assert type(block.get("size")) is int
        assert block.get("size") >= 0
        assert type(block.get("difficulty")) is int
        assert block.get("difficulty") >= 0
        assert type(block.get("transactions")) is list


def test_get_eth_balance(address: str, networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        balance = client.getBalanceInWei(address)
        assert type(balance) is int
        assert balance >= 0


def test_get_sign_message(
    private_key: str, networks_clients: Dict[str, BaseClient]
) -> None:
    msg = "Hello world!"
    for network, client in networks_clients.items():
        client.setAccount(privateKey=private_key)
        signed_message = client.signMessage(msg)
        assert client.isMessageSignedByMe(msg, signed_message)
