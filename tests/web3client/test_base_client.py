from typing import List

import pytest

import ape
from web3client.base_client import BaseClient
from web3client.middlewares.rpc_log_middleware import MemoryLog


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


@pytest.mark.local
def test_base_client_transfer_non_checksum_address(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = bob.balance
    alice_base_client.send_eth_in_wei(str(bob.address).lower(), 10**18)
    assert bob.balance == bob_balance + 10**18


def test_base_client_clone(alice_base_client: BaseClient) -> None:
    alice_base_client_clone = alice_base_client.clone()
    assert alice_base_client_clone.node_uri == alice_base_client.node_uri
    assert alice_base_client_clone.private_key == alice_base_client.private_key


@pytest.mark.local
def test_base_client_rpc_logs(
    accounts_keys: List[str], ape_chain_uri: str, bob: ape.api.AccountAPI
) -> None:
    rpc_log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    client = BaseClient(
        node_uri=ape_chain_uri, private_key=accounts_keys[0], rpc_logs=[rpc_log]
    )
    tx_hash = client.send_eth_in_wei(bob.address.lower(), 10**18)
    assert len(rpc_log.entries) == 2
    assert len(rpc_log.get_requests()) == 1
    assert len(rpc_log.get_responses()) == 1
    request = rpc_log.get_requests()[0]
    response = rpc_log.get_responses()[0]
    assert request.method == "eth_sendRawTransaction"
    assert response.method == "eth_sendRawTransaction"
    assert response.response["result"] == tx_hash


@pytest.mark.local
def test_base_client_rpc_logs_class_defined(
    accounts_keys: List[str], ape_chain_uri: str, bob: ape.api.AccountAPI
) -> None:
    rpc_log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])

    class BaseClientWithClassDefinedRpcLog(BaseClient):
        rpc_logs = [rpc_log]

    client = BaseClientWithClassDefinedRpcLog(
        node_uri=ape_chain_uri, private_key=accounts_keys[0]
    )
    tx_hash = client.send_eth_in_wei(bob.address.lower(), 10**18)
    assert len(rpc_log.entries) == 2
    assert len(rpc_log.get_requests()) == 1
    assert len(rpc_log.get_responses()) == 1
    request = rpc_log.get_requests()[0]
    response = rpc_log.get_responses()[0]
    assert request.method == "eth_sendRawTransaction"
    assert response.method == "eth_sendRawTransaction"
    assert response.response["result"] == tx_hash
