import pytest

import ape
from web3client.base_client import BaseClient


@pytest.mark.local
def test_base_client_balance_in_wei(
    base_client: BaseClient,
    alice: ape.api.AccountAPI,
) -> None:
    alice_balance_in_wei = base_client.get_balance_in_wei(alice.address)
    assert alice.balance == alice_balance_in_wei


@pytest.mark.local
def test_base_client_transfer(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = bob.balance
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert bob.balance == bob_balance + 10**18


def test_base_client_clone(alice_base_client: BaseClient) -> None:
    alice_base_client_clone = alice_base_client.clone()
    assert alice_base_client_clone.node_uri == alice_base_client.node_uri
    assert alice_base_client_clone.private_key == alice_base_client.private_key
