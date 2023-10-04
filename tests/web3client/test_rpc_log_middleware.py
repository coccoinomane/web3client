import logging
from datetime import datetime
from pathlib import Path

import pytest
from pytest import LogCaptureFixture
from web3 import Web3

import ape
from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client
from web3client.middlewares.rpc_log_middleware import (
    MemoryLog,
    PythonLog,
    RequestEntry,
    ResponseEntry,
    RPCEndpoint,
    RPCResponse,
    construct_generic_rpc_log_middleware,
    tx_rpc_log_middleware,
)


@pytest.fixture
def request_entry() -> RequestEntry:
    return RequestEntry(
        id="whatever",
        method=RPCEndpoint("test_method"),
        params={"param1": "value1", "param2": "value2"},
        timestamp=datetime.now(),
        type="request",
        w3=Web3(),
    )


@pytest.fixture
def response_entry() -> ResponseEntry:
    return ResponseEntry(
        id="whatever",
        method=RPCEndpoint("test_method"),
        params={"param1": "value1", "param2": "value2"},
        response=RPCResponse(result="test_result"),
        timestamp=datetime.now(),
        type="response",
        elapsed=10,
        w3=Web3(),
    )


@pytest.mark.local
def test_rpc_log_middleware_memory_log_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response"""
    log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_generic_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 2
    # Extract log entries
    logged_requests = log.get_requests()
    logged_responses = log.get_responses()
    assert len(logged_requests) == 1
    assert len(logged_responses) == 1
    logged_request = logged_requests[0]
    logged_response = logged_responses[0]
    # Check first log entry - the request
    assert logged_request.type == "request"
    assert logged_request.method == "eth_sendRawTransaction"
    assert type(logged_request.params[0]) is str
    assert logged_request.params[0].startswith("0x")
    assert isinstance(logged_request.timestamp, datetime)
    # Check second log entry - the response
    assert logged_response.type == "response"
    assert logged_response.method == log.entries[0].method
    assert logged_response.params == log.entries[0].params
    assert logged_response.timestamp > log.entries[0].timestamp
    assert logged_response.response["result"] == tx_hash
    assert logged_response.elapsed > 0


@pytest.mark.local
def test_rpc_log_middleware_memory_log_estimate_and_send(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log contains the request and
    response, for both the eth_estimateGas and eth_sendRawTransaction methods"""
    log = MemoryLog(rpc_whitelist=["eth_estimateGas", "eth_sendRawTransaction"])
    alice_base_client.w3.middleware_onion.add(construct_generic_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 4
    # Extract log entries
    requests = log.get_requests()
    responses = log.get_responses()
    # Estimate gas request
    assert requests[0].method == "eth_estimateGas"
    assert type(requests[0].params[0]) is dict
    assert requests[0].params[0].keys() == {"from", "to", "value"}
    # Estimate gas response
    assert int(responses[0].response["result"], 16) > 0
    # Send raw transaction request
    assert requests[1].method == "eth_sendRawTransaction"
    # Send raw transaction response
    assert responses[1].response["result"] == tx_hash


@pytest.mark.local
def test_rpc_log_middleware_memory_log_empty_whitelist(
    alice_base_client: BaseClient,
    bob: ape.api.AccountAPI,
) -> None:
    """Send ETH and check that the internal log is empty if the whitelist is
    None"""
    log = MemoryLog(rpc_whitelist=[])
    alice_base_client.w3.middleware_onion.add(construct_generic_rpc_log_middleware(log))
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    assert len(log.entries) == 0


@pytest.mark.local
def test_rpc_log_middleware_memory_log_parse_raw(
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    """Send an ETH transfer and a token transfer, and check that the requests
    are included in the log entries with their decoded tx_data"""
    log = MemoryLog(rpc_whitelist=["eth_sendRawTransaction"])
    alice_erc20_client.w3.middleware_onion.add(
        construct_generic_rpc_log_middleware(log)
    )
    # Send ETH transfer.  This will trigger an eth_estimateGas request
    tx_hash_eth = alice_erc20_client.send_eth_in_wei(bob.address, 10**18)
    # Send a token transfer.  This will trigger an eth_estimateGas request
    tx_hash_erc20 = alice_erc20_client.transfer(bob.address, 10**18)
    # Check that the tx was logged
    tx_requests = log.get_tx_requests()
    assert len(tx_requests) == 2
    # Check decoding for the ETH transfer
    tx_data_eth = tx_requests[0].parsed_tx_data
    assert Web3.to_hex(tx_data_eth["hash"]) == tx_hash_eth
    assert tx_data_eth["from"] == alice_erc20_client.user_address
    assert tx_data_eth["to"] == bob.address
    assert int(tx_data_eth["value"]) == 10**18
    # Check decoding for the token transfer
    tx_data_erc20 = tx_requests[1].parsed_tx_data
    assert Web3.to_hex(tx_data_erc20["hash"]) == tx_hash_erc20
    assert tx_data_erc20["from"] == alice_erc20_client.user_address
    assert tx_data_erc20["to"] == alice_erc20_client.contract_address
    assert int(tx_data_erc20["value"]) == 0
    # Check that tx response does not contain tx_data or tx_receipt
    # because we did not request it
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 2
    # ... ETH transfer
    assert tx_responses[0].response["result"] == tx_hash_eth
    assert tx_responses[0].tx_data == None
    assert tx_responses[0].tx_receipt == None
    # ... token transfer
    assert tx_responses[1].response["result"] == tx_hash_erc20
    assert tx_responses[1].tx_data == None
    assert tx_responses[1].tx_receipt == None


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
    alice_base_client.w3.middleware_onion.add(construct_generic_rpc_log_middleware(log))
    tx_hash = alice_base_client.send_eth_in_wei(bob.address, 10**18)
    # Check tx response
    tx_responses = log.get_tx_responses()
    assert len(tx_responses) == 1
    # Check response tx_data
    tx_data = tx_responses[0].tx_data
    assert int(tx_data["value"]) == 10**18
    # Check response tx_receipt
    tx_receipt = tx_responses[0].tx_receipt
    assert Web3.to_hex(tx_receipt["transactionHash"]) == tx_hash
    assert type(tx_receipt["gasUsed"]) is int


@pytest.mark.local
def test_rpc_log_middleware_tx_rpc_log_middleware(
    alice_base_client: BaseClient, bob: ape.api.AccountAPI, tmp_path: Path
) -> None:
    # Set logger so that it prints to file all INFO messages
    file = tmp_path / "rpc.log"
    logger = logging.getLogger("web3client.RpcLog")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(file.resolve())
    fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(fh)
    # Add tx_rpc_log_middleware to the client
    alice_base_client.w3.middleware_onion.add(tx_rpc_log_middleware)
    # Send ETH
    alice_base_client.send_eth_in_wei(bob.address, 10**18)
    # Check that the log file contains the request and response
    assert file.exists(), f"file '{file}' not found"
    content = file.read_text()
    assert "[REQ " in content
    assert "[RES " in content


#   _   _          _   _
#  | | | |  _ _   (_) | |_
#  | |_| | | ' \  | | |  _|
#   \___/  |_||_| |_|  \__|


def test_unit_rpc_log_middleware_memory_log(
    request_entry: RequestEntry,
    response_entry: ResponseEntry,
) -> None:
    """Unit test for the ``MemoryLog`` class"""
    # Arrange

    # Act
    memory_log = MemoryLog()
    memory_log.handle_request(
        id=request_entry.id,
        method=RPCEndpoint(request_entry.method),
        params=request_entry.params,
        w3=request_entry.w3,
    )
    memory_log.handle_response(
        id=response_entry.id,
        method=RPCEndpoint(response_entry.method),
        params=response_entry.params,
        w3=response_entry.w3,
        response=response_entry.response,
        elapsed=response_entry.elapsed,
    )

    # Assert
    assert len(memory_log.entries) == 2
    # ... request entry
    logged_request = memory_log.get_requests()[0]
    assert logged_request.id == request_entry.id
    assert logged_request.method == request_entry.method
    assert logged_request.params == request_entry.params
    assert logged_request.timestamp > request_entry.timestamp
    assert logged_request.type == request_entry.type
    # ... response entry
    logged_response = memory_log.get_responses()[0]
    assert logged_response.id == response_entry.id
    assert logged_response.method == response_entry.method
    assert logged_response.params == response_entry.params
    assert logged_response.response == response_entry.response
    assert logged_response.timestamp > response_entry.timestamp
    assert logged_response.type == response_entry.type


def test_unit_rpc_log_middleware_python_log(
    caplog: LogCaptureFixture,
    request_entry: RequestEntry,
    response_entry: ResponseEntry,
) -> None:
    """Unit test for the ``PythonLog`` class"""
    # Arrange
    entry = {
        "id": "whatever",
        "method": RPCEndpoint("test_method"),
        "params": {"param1": "value1", "param2": "value2"},
        "timestamp": datetime.now(),
        "type": "request",
        "w3": Web3(),
    }
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)

    # Act
    python_log = PythonLog(logger=logger)
    python_log.log_request(request_entry)
    python_log.log_response(response_entry)

    # Get all info records in `test_logger` log
    records = [
        r
        for r in caplog.record_tuples
        if r[0] == "test_logger" and r[1] == logging.INFO
    ]

    # Assert
    assert len(records) == 2
    assert "[REQ" in records[0][2]
    assert "[RES" in records[1][2]
