import pytest
from web3 import Web3

import ape
from web3client.base_client import BaseClient
from web3client.middlewares.rpc_log_middleware import (
    InternalRpcLog,
    RPCEndpoint,
    RPCResponse,
    construct_rpc_log_middleware,
)


@pytest.mark.local
def test_rpc_log_middleware_internal_log_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response"""
    log = InternalRpcLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 1
    assert log.entries[0]["method"] == "eth_sendRawTransaction"
    assert log.entries[0]["response"]["result"] == tx_hash


@pytest.mark.local
def test_rpc_log_middleware_internal_log_estimate_and_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response, for both the eth_estimateGas and eth_sendRawTransaction methods"""
    log = InternalRpcLog(rpc_whitelist=["eth_estimateGas", "eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 2
    assert log.entries[0]["method"] == "eth_estimateGas"
    assert int(log.entries[0]["response"]["result"], 16) > 0
    assert log.entries[1]["method"] == "eth_sendRawTransaction"
    assert log.entries[1]["response"]["result"] == tx_hash


@pytest.mark.local
def test_rpc_log_middleware_internal_log_empty_whitelist(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log is empty if the whitelist is
    None"""
    log = InternalRpcLog(rpc_whitelist=[])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 0


def test_unit_log_middleware_internal_log() -> None:
    """Unit test for the ``InternalRpcLog`` class"""
    # Arrange
    method = RPCEndpoint("test_method")
    params = {"param1": "value1", "param2": "value2"}
    response = RPCResponse(result="test_result")
    internal_log_entry = {
        "method": method,
        "params": params,
        "response": response,
    }
    w3 = Web3()

    # Act
    internal_log = InternalRpcLog()
    internal_log.log_response(method, params, w3, response)

    # Assert
    assert len(internal_log.entries) == 1
    assert internal_log.entries[0] == internal_log_entry
