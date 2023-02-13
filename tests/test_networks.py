from typing import Dict

from web3client.base_client import BaseClient


def test_get_nonce(address: str, networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        nonce = client.get_nonce(address)
        assert type(nonce) is int
        assert nonce >= 0


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


def test_get_eth_balance(address: str, networks_clients: Dict[str, BaseClient]) -> None:
    for network, client in networks_clients.items():
        balance = client.get_balance_in_wei(address)
        assert type(balance) is int
        assert balance >= 0


def test_get_sign_message(
    private_key: str, networks_clients: Dict[str, BaseClient]
) -> None:
    msg = "Hello world!"
    for network, client in networks_clients.items():
        client.set_account(private_key=private_key)
        signed_message = client.sign_message(msg)
        assert client.is_message_signed_by_me(msg, signed_message)
