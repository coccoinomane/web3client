import logging
from abc import ABC
from datetime import datetime
from typing import Any, Callable, Collection, List

from typing_extensions import Literal, NotRequired, override
from web3 import Web3
from web3._utils.compat import TypedDict
from web3.types import Middleware, RPCEndpoint, RPCResponse, TxData, TxReceipt

from web3client.helpers.tx import (
    is_rpc_response_ok,
    parse_call_tx,
    parse_estimate_gas_tx,
    parse_raw_tx,
)

TX_DATA_METHODS = ["eth_sendRawTransaction", "eth_call", "eth_estimateGas"]
"""RPC endpoints whose parameters can be mapped or decoded to a TxData object"""


class BaseRpcLog(ABC):
    """Class to log RPC requests and responses.

    The class is meant to be used in a web3.py Middleware.  Subclasses can
    override the following methods:
     - ``log_request(method, params, w3, tx_data)``: called when a request is
        received.  If the request is transaction-related, the ``tx_data``
        parameter will be available.
     - ``log_response(method, params, w3, response, tx_data, tx_receipt)``:
        called when a response is received.  If the request was to send a write
        transaction, the ``tx_data`` and ``tx_receipt`` parameters will be
        passed, provided self.fetch_tx_data and self.fetch_tx_receipt are True.
     - ``should_log_request(method, params, w3)``: whether a request should be
        logged or not.  If True, the ``log_request`` method will be called.  By
        default, all requests are logged.
     - ``should_log_response(method, params, w3, response)``: whether a response
        should be logged or not.  If True, the ``log_response`` method will be
        called.  By default, all responses are logged.
    """

    class_logger = logging.getLogger("web3client.middlewares.RpcLog")

    def __init__(
        self,
        rpc_whitelist: Collection[str] = None,
        fetch_tx_data: bool = False,
        fetch_tx_receipt: bool = False,
        decode_tx_data: bool = True,
    ) -> None:
        """Constructor

        :param rpc_whitelist: A list of RPC methods to log.  If None, all
            requests and responses will be logged.
        :param fetch_tx_data: If True, the transaction data will be fetched
            and made available to the ``log_response`` method.  Applies only
            to transactions.
        :param fetch_tx_receipt: If True, the transaction receipt will be
            fetched and made available to the ``log_response`` method.  Applies
            only to transactions.
        :param decode_tx_data: If True, requests parameters will be decoded into
            a TxData object, and made available to the ``log_request`` method.
            Applies to both transactions (eth_sendRawTransaction) and simulations
            (eth_call, eth_estimateGas).
        """
        self.rpc_whitelist = rpc_whitelist
        self.decode_tx_data = decode_tx_data
        self.fetch_tx_data = fetch_tx_data
        self.fetch_tx_receipt = fetch_tx_receipt
        self.init()

    def init(self) -> None:
        """Initialization function called in the constructor"""
        pass

    def should_log_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> bool:
        """Whether a request should be logged or not"""
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def handle_request(self, method: RPCEndpoint, params: Any, w3: Web3) -> None:
        """Receive a request, pre-process it, and pass it to the logging
        function"""
        tx_data = None
        try:
            if self.decode_tx_data:
                if method == "eth_sendRawTransaction":
                    tx_data = parse_raw_tx(params[0])
                elif method == "eth_estimateGas":
                    tx_data = parse_estimate_gas_tx(params[0])
                elif method == "eth_call":
                    tx_data = parse_call_tx(params[0])
        except Exception:
            self.class_logger.warning(f"Could not decode call to '{method}'")

        # Call logging function
        self.log_request(method, params, w3, tx_data)

    def log_request(
        self, method: RPCEndpoint, params: Any, w3: Web3, tx_data: TxData
    ) -> None:
        """Log a request.  Meant to be overridden by subclasses.

        The tx_data parameter is passed only if (1) the request is a
        transaction-related request, and (2) the instance has
        self.decode_tx_data=True.
        """
        pass

    def should_log_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> bool:
        """Whether a response should be logged or not"""
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def handle_response(
        self, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> None:
        """Receive a response, pre-process it, and pass it to the logging
        function"""
        ok = is_rpc_response_ok(response)
        # Fetch tx data if requested
        tx_data = None
        if ok and self.fetch_tx_data and method == "eth_sendRawTransaction":
            tx_data = w3.eth.get_transaction(response["result"])
        # Fetch tx receipt if requested
        tx_receipt = None
        if ok and self.fetch_tx_receipt and method == "eth_sendRawTransaction":
            tx_receipt = w3.eth.wait_for_transaction_receipt(response["result"])
        # Call logging function
        self.log_response(method, params, w3, response, tx_data, tx_receipt)

    def log_response(
        self,
        method: RPCEndpoint,
        params: Any,
        w3: Web3,
        response: RPCResponse,
        tx_data: TxData,
        tx_receipt: TxReceipt,
    ) -> None:
        """Log a response.  Meant to be overridden by subclasses.

        The tx_data and tx_receipt parameters are passed only if (1) the request
        was eth_sendRawTransaction, (2) the instance has self.fetch_tx_data=True
        and/or self.fetch_tx_receipt=True, and (3) the request was successful.
        """
        pass


class PythonLog(BaseRpcLog):
    """An RPC log class that logs requests and responses to a Python logger,
    as info-level messages.

    If no logger is provided, the class logger is used, with the name
    "web3client.middlewares.RpcLog".

    Subclasses can override the ``format_request`` and ``format_response``
    methods to customize format of the logger messages.
    """

    def __init__(
        self,
        rpc_whitelist: Collection[str] = None,
        fetch_tx_data: bool = False,
        fetch_tx_receipt: bool = False,
        decode_tx_data: bool = True,
        logger: logging.Logger = None,
    ) -> None:
        super().__init__(rpc_whitelist, fetch_tx_data, fetch_tx_receipt, decode_tx_data)
        self.logger = logger or self.class_logger

    @override
    def log_request(
        self, method: RPCEndpoint, params: Any, w3: Web3, tx_data: TxData
    ) -> None:
        self.logger.info(self.format_request(method, params, tx_data))

    @override
    def log_response(
        self,
        method: RPCEndpoint,
        params: Any,
        w3: Web3,
        response: RPCResponse,
        tx_data: TxData,
        tx_receipt: TxReceipt,
    ) -> None:
        self.logger.info(
            self.format_response(method, params, response, tx_data, tx_receipt)
        )

    def format_request(self, method: RPCEndpoint, params: Any, tx_data: TxData) -> str:
        """Return the log message for a request"""
        msg = f"RPC request: Method: {method}, Params: {params}"
        if tx_data is not None:
            msg += f", Transaction data: {tx_data}"
        return msg

    def format_response(
        self,
        method: RPCEndpoint,
        params: Any,
        response: RPCResponse,
        tx_data: TxData,
        tx_receipt: TxReceipt,
    ) -> str:
        """Return the log message for a response"""
        msg = f"RPC response: Method: {method}, Params: {params}, Response: {response}"
        if tx_data is not None:
            msg += f", Transaction data: {tx_data}"
        if tx_receipt is not None:
            msg += f", Transaction receipt: {tx_receipt}"
        return msg


class MemoryLog(BaseRpcLog):
    """An RPC log class that keeps track of requests and responses in the
    self.entries internal attribute."""

    class Entry(TypedDict):
        """Type for a memory log entry"""

        type: Literal["request", "response"]
        timestamp: datetime
        method: str
        params: Any
        response: NotRequired[RPCResponse]
        tx_data: NotRequired[TxData]
        tx_receipt: NotRequired[TxReceipt]

    entries: List[Entry]

    def get_tx_requests(self) -> List[Entry]:
        """Returns the log entries of transaction-related requests"""
        return [
            e
            for e in self.entries
            if e["type"] == "request" and e["method"] in TX_DATA_METHODS
        ]

    def get_tx_responses(self) -> List[Entry]:
        """Returns the log entries of transaction-related responses"""
        return [
            e
            for e in self.entries
            if e["type"] == "response" and e["method"] in TX_DATA_METHODS
        ]

    @override
    def init(self) -> None:
        self.entries = []

    @override
    def log_request(
        self, method: RPCEndpoint, params: Any, w3: Web3, tx_data: TxData
    ) -> None:
        self.entries.append(
            {
                "type": "request",
                "timestamp": datetime.now(),
                "method": method,
                "params": params,
                "tx_data": tx_data,
            }
        )

    @override
    def log_response(
        self,
        method: RPCEndpoint,
        params: Any,
        w3: Web3,
        response: RPCResponse,
        tx_data: TxData,
        tx_receipt: TxReceipt,
    ) -> None:
        self.entries.append(
            {
                "type": "response",
                "timestamp": datetime.now(),
                "method": method,
                "params": params,
                "response": response,
                "tx_data": tx_data,
                "tx_receipt": tx_receipt,
            }
        )


def construct_rpc_log_middleware(log: BaseRpcLog) -> Middleware:
    """
    Constructs a middleware which logs requests and/or responses based on the
    request ``method`` and ``params``.

    :param rpc_log: A instance of an RPC log class derived from ``BaseRpcLog``.
    """

    def log_middleware(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            if log.should_log_request(method, params, w3):
                log.handle_request(method, params, w3)
            response = make_request(method, params)
            if log.should_log_response(method, params, w3, response):
                log.handle_response(method, params, w3, response)
            return response

        return middleware

    return log_middleware
