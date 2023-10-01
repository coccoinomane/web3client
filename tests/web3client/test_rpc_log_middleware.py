import logging
from datetime import datetime

import pytest
from pytest import LogCaptureFixture
from web3 import Web3

import ape
from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client
from web3client.middlewares.rpc_log_middleware import (
    MemoryLog,
    PythonLog,
    RPCEndpoint,
    RPCResponse,
    construct_rpc_log_middleware,
)


@pytest.mark.local
def test_rpc_log_middleware_memory_log_send(
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
def test_rpc_log_middleware_memory_log_estimate_and_send(
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
def test_rpc_log_middleware_memory_log_empty_whitelist(
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
def test_rpc_log_middleware_memory_log_decode_raw(
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    """Send an ETH transfer and a token transfer, and check that the requests
    are included in the log entries with their decoded tx_data"""
    log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_erc20_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    # Send ETH transfer.  This will trigger an eth_estimateGas request
    tx_hash_eth = alice_erc20_client.send_eth_in_wei(bob.address, 10**18)
    # Send a token transfer.  This will trigger an eth_estimateGas request
    tx_hash_erc20 = alice_erc20_client.transfer(bob.address, 10**18)
    # Check that the tx was logged
    tx_requests = log.get_tx_requests()
    assert len(tx_requests) == 2
    # Check decoding for the ETH transfer
    tx_data_eth = tx_requests[0]["tx_data"]
    assert Web3.to_hex(tx_data_eth["hash"]) == tx_hash_eth
    assert tx_data_eth["from"] == alice_erc20_client.user_address
    assert tx_data_eth["to"] == bob.address
    assert int(tx_data_eth["value"]) == 10**18
    # Check decoding for the token transfer
    tx_data_erc20 = tx_requests[1]["tx_data"]
    assert Web3.to_hex(tx_data_erc20["hash"]) == tx_hash_erc20
    assert tx_data_erc20["from"] == alice_erc20_client.user_address
    assert tx_data_erc20["to"] == alice_erc20_client.contract_address
    assert int(tx_data_erc20["value"]) == 0
    # Check that tx response does not contain tx_data or tx_receipt
    # because we did not request it
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 2
    # ... ETH transfer
    assert tx_responses[0]["response"]["result"] == tx_hash_eth
    assert tx_responses[0]["tx_data"] == None
    assert tx_responses[0]["tx_receipt"] == None
    # ... token transfer
    assert tx_responses[1]["response"]["result"] == tx_hash_erc20
    assert tx_responses[1]["tx_data"] == None
    assert tx_responses[1]["tx_receipt"] == None


@pytest.mark.local
def test_rpc_log_middleware_memory_log_decode_estimate_gas(
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    """Estimate gas spent for an ETH transfer and a token transfer, and check
    that the requests are included in the log entries with their decoded tx_data"""
    log = MemoryLog(rpc_whitelist=["eth_estimateGas"])
    alice_erc20_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    # Send ETH transfer.  This will trigger an eth_estimateGas request
    alice_erc20_client.send_eth_in_wei(bob.address, 10**18)
    # Send a token transfer.  This will trigger an eth_estimateGas request
    alice_erc20_client.transfer(bob.address, 10**18)
    # Check that the txs were logged
    tx_requests = log.get_tx_requests()
    assert len(tx_requests) == 2
    # Check decoding for the ETH transfer
    tx_data_eth = tx_requests[0]["tx_data"]
    assert tx_data_eth["from"] == alice_erc20_client.user_address
    assert tx_data_eth["to"] == bob.address
    assert not tx_data_eth["data"]
    assert int(tx_data_eth["value"]) == 10**18
    # Check decoding for the token transfer
    tx_data_erc20 = tx_requests[1]["tx_data"]
    assert tx_data_erc20["from"] == alice_erc20_client.user_address
    assert tx_data_erc20["to"] == alice_erc20_client.contract_address
    assert tx_data_erc20["data"]
    assert int(tx_data_erc20["value"]) == 0
    # Check that both response were simply integer numbers
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 2
    # ... ETH transfer
    assert type(tx_responses[0]["response"]["result"]) is str
    assert tx_responses[0]["response"]["result"].startswith("0x")
    assert int(tx_responses[0]["response"]["result"], 16) > 0
    # ... token transfer
    assert type(tx_responses[1]["response"]["result"]) is str
    assert tx_responses[1]["response"]["result"].startswith("0x")
    assert int(tx_responses[1]["response"]["result"], 16) > 0


@pytest.mark.local
def test_rpc_log_middleware_memory_log_decode_call(
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    """Simulate an ETH transfer using eth_call, and check that the requests are
    included in the log entries with their decoded tx_data"""
    log = MemoryLog(rpc_whitelist=["eth_call"])
    alice_erc20_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    # Simulate a token transfer.  This will trigger an eth_estimateGas request
    alice_erc20_client.functions.transfer(bob.address, 10**18).call(),
    # Check that the tx was logged
    tx_requests = log.get_tx_requests()
    assert len(tx_requests) == 1
    # Check that the outgoing eth_estimateGas request was correctly decoded
    tx_data = tx_requests[0]["tx_data"]
    assert tx_data["from"] == alice_erc20_client.user_address
    assert tx_data["to"] == alice_erc20_client.contract_address
    assert tx_data["data"]
    assert int(tx_data["value"]) == 0
    # Check that there is no hash in tx_data
    assert not tx_data["hash"]
    # Check that the response is a True boolean
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 1
    assert type(tx_responses[0]["response"]["result"]) is str
    assert (
        tx_responses[0]["response"]["result"]
        == "0x0000000000000000000000000000000000000000000000000000000000000001"
    )


@pytest.mark.local
def test_rpc_log_middleware_memory_log_fetch(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the transaction response is included in the
    entries with its fetched tx_data and tx_receipts"""
    log = MemoryLog(
        rpc_whitelist=["eth_sendRawTransaction"],
        fetch_tx_data=True,
        fetch_tx_receipt=True,
    )
    alice_base_client.w3.middleware_onion.add(construct_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    # Check tx response
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 1
    # Check response tx_data
    tx_data = tx_responses[0]["tx_data"]
    assert int(tx_data["value"]) == 10**18
    # Check response tx_receipt
    tx_receipt = tx_responses[0]["tx_receipt"]
    assert Web3.to_hex(tx_receipt["transactionHash"]) == tx_hash
    assert type(tx_receipt["gasUsed"]) is int


#   _   _          _   _
#  | | | |  _ _   (_) | |_
#  | |_| | | ' \  | | |  _|
#   \___/  |_||_| |_|  \__|


def test_unit_rpc_log_middleware_memory_log() -> None:
    """Unit test for the ``MemoryLog`` class"""
    # Arrange
    method = RPCEndpoint("test_method")
    params = {"param1": "value1", "param2": "value2"}
    response = RPCResponse(result="test_result")
    memory_log_entry: MemoryLog.Entry = {
        "method": method,
        "params": params,
        "response": response,
        "timestamp": datetime.now(),
        "type": "response",
    }
    w3 = Web3()

    # Act
    memory_log = MemoryLog()
    memory_log.log_response(method, params, w3, response, None, None)

    # Assert
    assert len(memory_log.entries) == 1
    assert memory_log.entries[0]["method"] == memory_log_entry["method"]
    assert memory_log.entries[0]["params"] == memory_log_entry["params"]
    assert memory_log.entries[0]["response"] == memory_log_entry["response"]
    assert memory_log.entries[0]["timestamp"] > memory_log_entry["timestamp"]
    assert memory_log.entries[0]["type"] == memory_log_entry["type"]


def test_unit_rpc_log_middleware_python_log(caplog: LogCaptureFixture) -> None:
    """Unit test for the ``PythonLog`` class"""
    # Arrange
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    method = RPCEndpoint("test_method")
    params = {"param1": "value1", "param2": "value2"}
    response = RPCResponse(result="test_result")
    w3 = Web3()

    # Act
    python_log = PythonLog(logger=logger)
    python_log.log_request(method, params, w3, None)
    python_log.log_response(method, params, w3, response, None, None)

    # Get all info records in `test_logger` log
    records = [
        r
        for r in caplog.record_tuples
        if r[0] == "test_logger" and r[1] == logging.INFO
    ]

    # Assert
    assert len(records) == 2
    assert "RPC request" in records[0][2]
    assert "RPC response" in records[1][2]
