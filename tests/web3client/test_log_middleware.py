import pytest

import ape
from web3client.base_client import BaseClient
from web3client.middlewares.log_middleware import (
    InternalLog,
    RPCEndpoint,
    RPCResponse,
    Web3WithInternalLog,
    construct_log_middleware,
)


@pytest.mark.local
def test_log_middleware_internal_log_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response"""
    alice_base_client.w3.middleware_onion.add(
        construct_log_middleware(
            log_class=InternalLog, rpc_whitelist=["eth_sendRawTransaction"]
        )
    )
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(alice_base_client.w3.internal_log) == 1  # type: ignore
    assert alice_base_client.w3.internal_log[0]["method"] == "eth_sendRawTransaction"  # type: ignore
    assert alice_base_client.w3.internal_log[0]["response"]["result"] == tx_hash  # type: ignore


@pytest.mark.local
def test_log_middleware_internal_log_estimate_and_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response, for both the eth_estimateGas and eth_sendRawTransaction methods"""
    alice_base_client.w3.middleware_onion.add(
        construct_log_middleware(
            log_class=InternalLog,
            rpc_whitelist=["eth_estimateGas", "eth_sendRawTransaction"],
        )
    )
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(alice_base_client.w3.internal_log) == 2  # type: ignore
    assert alice_base_client.w3.internal_log[0]["method"] == "eth_estimateGas"  # type: ignore
    assert int(alice_base_client.w3.internal_log[0]["response"]["result"], 16) > 0  # type: ignore
    assert alice_base_client.w3.internal_log[1]["method"] == "eth_sendRawTransaction"  # type: ignore
    assert alice_base_client.w3.internal_log[1]["response"]["result"] == tx_hash  # type: ignore


@pytest.mark.local
def test_log_middleware_internal_log_empty_whitelist(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log is empty if the whitelist is None"""
    alice_base_client.w3.middleware_onion.add(
        construct_log_middleware(log_class=InternalLog, rpc_whitelist=[])
    )
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(alice_base_client.w3.internal_log) == 0  # type: ignore


def test_unit_log_middleware_internal_log() -> None:
    """Unit test for the ``InternalLog`` class"""
    # Arrange
    method = RPCEndpoint("test_method")
    params = {"param1": "value1", "param2": "value2"}
    response = RPCResponse(result="test_result")
    internal_log_entry = {
        "method": method,
        "params": params,
        "response": response,
    }
    w3 = Web3WithInternalLog()

    # Act
    internal_log = InternalLog(method, params, w3)
    internal_log.log_response(response)

    # Assert
    assert len(w3.internal_log) == 1
    assert w3.internal_log[0] == internal_log_entry
