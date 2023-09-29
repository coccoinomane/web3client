import json
from datetime import datetime
from pathlib import Path

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
    log = InternalRpcLog(rpc_whitelist=["eth_estimateGas", "eth_sendRawTransaction"])
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


def test_unit_log_middleware_internal_log_dump_json(tmp_path: Path) -> None:
    # Create a temporary file to write to
    f = tmp_path / "internal_log_dump.json"

    # Create an instance of InternalRpcLog
    log = InternalRpcLog()

    # Add some entries to the log
    log.entries = [
        {
            "type": "request",
            "timestamp": datetime.now(),
            "method": "eth_getBlockByNumber",
            "params": ["0x0", True],
        },
        {
            "type": "response",
            "timestamp": datetime.now(),
            "method": "eth_getBlockByNumber",
            "params": ["0x0", True],
            "response": {"result": "0x1234", "error": None},
        },
    ]

    # Dump the log to the temporary file
    log.dump_json(f)

    # Read the contents of the file and parse the JSON
    contents = json.loads(f.read_text())

    print("contents")
    print(contents)

    # Check that the contents of the file match the log entries
    assert contents == log.entries
