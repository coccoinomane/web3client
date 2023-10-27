import pytest
from web3.exceptions import ExtraDataLengthError
from web3.middleware import geth_poa_middleware

from web3client.base_client import BaseClient

POA_CHAIN_RPC = "https://polygon-rpc.com"
NON_POA_CHAIN_RPC = "https://arb1.arbitrum.io/rpc"


@pytest.mark.remote
def test_base_client_poa_with_poa_chain() -> None:
    client = BaseClient(node_uri=POA_CHAIN_RPC)
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0


@pytest.mark.remote
def test_base_client_poa_with_poa_chain_if_no_support_raises() -> None:
    client = BaseClient(node_uri=POA_CHAIN_RPC, add_poa_support=False)
    with pytest.raises(ExtraDataLengthError):
        client.get_latest_block()


@pytest.mark.remote
def test_base_client_poa_with_normal_chain() -> None:
    client = BaseClient(node_uri=NON_POA_CHAIN_RPC)
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0


@pytest.mark.remote
def test_base_client_poa_middleware() -> None:
    # Should work with middleware only.  This works only if the middleware
    # is added at layer 0, so if the test fails it is likely you added
    # the middleware at the wrong layer (or using .add instead of .inject)
    client = BaseClient(
        node_uri=POA_CHAIN_RPC, middlewares=[geth_poa_middleware], add_poa_support=False
    )
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0


@pytest.mark.remote
def test_base_client_poa_middleware_and_no_poa_support() -> None:
    # Should work with middleware and poa support
    client = BaseClient(node_uri=POA_CHAIN_RPC, middlewares=[geth_poa_middleware])
    block = client.get_latest_block()
    assert type(block.get("number")) is int
    assert block.get("number") >= 0
