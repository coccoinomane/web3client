from datetime import datetime

import pytest
from web3 import Web3

import ape
from web3client.base_client import BaseClient
from web3client.middlewares.rpc_log_middleware import (
    MemoryLog,
    RPCEndpoint,
    RPCResponse,
    TxMemoryLog,
    construct_rpc_log_middleware,
)


@pytest.mark.local
def test_rpc_log_middleware_internal_log_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response"""
    log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 2
    # Check first log entry - the request
    assert log.entries[0]["type"] == "request"
    assert log.entries[0]["method"] == "eth_sendRawTransaction"
    assert type(log.entries[0]["params"][0]) is str
    assert log.entries[0]["params"][0].startswith("0x")
    assert isinstance(log.entries[0]["timestamp"], datetime)
    # Check second log entry - the response
    assert log.entries[1]["type"] == "response"
    assert log.entries[1]["method"] == log.entries[0]["method"]
    assert log.entries[1]["params"] == log.entries[0]["params"]
    assert log.entries[1]["timestamp"] > log.entries[0]["timestamp"]
    assert log.entries[1]["response"]["result"] == tx_hash


@pytest.mark.local
def test_rpc_log_middleware_internal_log_estimate_and_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response, for both the eth_estimateGas and eth_sendRawTransaction methods"""
    log = MemoryLog(rpc_whitelist=["eth_estimateGas", "eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 4
    # estimate gas request
    assert log.entries[0]["method"] == "eth_estimateGas"
    assert type(log.entries[0]["params"][0]) is dict
    assert log.entries[0]["params"][0].keys() == {"from", "to", "value"}
    # estimate gas response
    assert int(log.entries[1]["response"]["result"], 16) > 0
    # send raw transaction request
    assert log.entries[2]["method"] == "eth_sendRawTransaction"
    # send raw transaction response
    assert log.entries[3]["response"]["result"] == tx_hash


@pytest.mark.local
def test_rpc_log_middleware_internal_log_empty_whitelist(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log is empty if the whitelist is
    None"""
    log = MemoryLog(rpc_whitelist=[])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 0


@pytest.mark.local
def test_rpc_log_middleware_tx_internal(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the transaction is correctly decoded and
    included in the tx_entries attribute"""
    log = TxMemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.tx_entries) == 1
    # Check tx data
    tx_data = log.tx_entries[0]
    assert Web3.to_hex(tx_data["hash"]) == tx_hash
    assert tx_data["from"] == alice_base_client.user_address
    assert tx_data["to"] == bob.address
    assert int(tx_data["value"]) == 10**18


#   _   _          _   _
#  | | | |  _ _   (_) | |_
#  | |_| | | ' \  | | |  _|
#   \___/  |_||_| |_|  \__|


def test_unit_rpc_log_middleware_internal_log() -> None:
    """Unit test for the ``MemoryLog`` class"""
    # Arrange
    method = RPCEndpoint("test_method")
    params = {"param1": "value1", "param2": "value2"}
    response = RPCResponse(result="test_result")
    internal_log_entry: MemoryLog.Entry = {
        "method": method,
        "params": params,
        "response": response,
        "timestamp": datetime.now(),
        "type": "response",
    }
    w3 = Web3()

    # Act
    internal_log = MemoryLog()
    internal_log.log_response(method, params, w3, response)

    # Assert
    assert len(internal_log.entries) == 1
    assert internal_log.entries[0]["method"] == internal_log_entry["method"]
    assert internal_log.entries[0]["params"] == internal_log_entry["params"]
    assert internal_log.entries[0]["response"] == internal_log_entry["response"]
    assert internal_log.entries[0]["timestamp"] > internal_log_entry["timestamp"]
    assert internal_log.entries[0]["type"] == internal_log_entry["type"]
