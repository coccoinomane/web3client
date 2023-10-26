import pytest
from web3.exceptions import ExtraDataLengthError
from web3.middleware import geth_poa_middleware

from web3client.base_client import BaseClient

POA_CHAIN_RPC = "https://polygon-rpc.com"
NON_POA_CHAIN_RPC = "https://arb1.arbitrum.io/rpc"


@pytest.mark.remote
def test_base_client_is_poa_chain() -> None:
    client_arbitrum = BaseClient(node_uri=NON_POA_CHAIN_RPC)
    assert client_arbitrum.is_poa_chain() == False

    client_polygon = BaseClient(node_uri=POA_CHAIN_RPC)
    assert client_polygon.is_poa_chain() == True


@pytest.mark.remote
def test_base_client_raises_with_poa_chain() -> None:
    client = BaseClient(node_uri=POA_CHAIN_RPC)
    with pytest.raises(ExtraDataLengthError):
        client.get_latest_block()


@pytest.mark.remote
def test_base_client_auto_detect_poa_with_normal_chain() -> None:
    client = BaseClient(node_uri=NON_POA_CHAIN_RPC, auto_detect_poa=True)
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0


@pytest.mark.remote
def test_base_client_auto_detect_poa_with_poa_chain() -> None:
    client = BaseClient(node_uri=POA_CHAIN_RPC, auto_detect_poa=True)
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0


@pytest.mark.remote
def test_base_client_auto_detect_poa_middleware_added_twice() -> None:
    # Should be fine if middleware is added twice
    client = BaseClient(
        node_uri=POA_CHAIN_RPC, auto_detect_poa=True, middlewares=[geth_poa_middleware]
    )
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0
