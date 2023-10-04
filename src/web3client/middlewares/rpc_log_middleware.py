from __future__ import annotations

import inspect
import uuid
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from logging import Logger, getLogger
from typing import Any, Callable, Dict, List, Self, Union

from typing_extensions import Literal, override
from web3 import Web3
from web3.types import Middleware, RPCEndpoint, RPCResponse, TxData, TxReceipt

from web3client.helpers.tx import is_rpc_response_ok, parse_raw_tx

TX_WRITE_METHODS = ["eth_sendRawTransaction", "eth_sendTransaction"]
"""RPC endpoints that submit a transaction to the blockchain"""

"""
  _____
 |_   _|  _  _   _ __   ___   ___
   | |   | || | | '_ \ / -_) (_-<
   |_|    \_, | | .__/ \___| /__/
          |__/  |_|
"""


@dataclass
class RpcEntry:
    """Data common to an RPC request or response"""

    id: str
    """Unique ID for the request-response pair.  Can be used to match the
    request to the response."""
    timestamp: datetime
    """Refers to the time from when the entry was stored in the log"""
    method: str
    """RPC method name"""
    params: Any
    """Parameters for the RPC method"""
    w3: Web3
    """Web3 instance used to send the request"""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Allow to initialize a dataclass from a dictionary"""
        return cls(
            **{
                key: (
                    data[key]
                    if val.default == val.empty
                    else data.get(key, val.default)
                )
                for key, val in inspect.signature(cls).parameters.items()
            }
        )


@dataclass
class RequestEntry(RpcEntry):
    """Data specific to an RPC request"""

    type: Literal["request"]
    """Whether the entry is for a request or a response"""
    parsed_tx_data: TxData = None
    """The transaction data sent along with the RPC request.  Populated
    only if (1) it is a eth_sendRawTransaction request, and (2) if the
    instance has parse_raw_tx_data=True"""


@dataclass
class ResponseEntry(RpcEntry):
    """Data specific to an RPC response"""

    type: Literal["response"]
    """Whether the entry is for a request or a response"""
    response: RPCResponse
    """Response returned by the RPC method"""
    elapsed: float
    """Time elapsed between the request and the response, including the time
    spent in the middleware."""
    tx_data: TxData = None
    """The data of the transaction sent with the RPC request, as fetched from
    the blockchain with eth_getTransaction"""
    tx_receipt: TxReceipt = None
    """The receipt of the transaction sent with the RPC request, as fetched from
    the blockchain with eth_getTransactionReceipt"""


"""
  ___
 | _ )  __ _   ___  ___
 | _ \ / _` | (_-< / -_)
 |___/ \__,_| /__/ \___|

"""


class BaseRpcLog(ABC):
    """
    Class to log RPC requests and responses.

    The class is meant to be used in a web3.py Middleware.  Subclasses can
    override the following methods:

     - ``should_log_request(method, params, w3)``: whether a request should be
        logged or not.  If True, the ``log_request`` method will be called.  By
        default, all requests are logged.

     - ``should_log_response(method, params, w3, response)``: whether a response
        should be logged or not.  If True, the ``log_response`` method will be
        called.  By default, all responses are logged.

     - ``log_request(RequestEntry)``: called when a request is received.  If the
        request is to eth_sendRawTransaction, the ``parsed_tx_data`` field will be
        populated, with the decoded transaction data.

     - ``log_response(ResponseEntry)``: called when a response is received.
        If the request was to submit a transaction, the ``tx_data`` and ``tx_receipt``
        fields will be populated, but only if self.fetch_tx_data=True and
        self.fetch_tx_receipt=True, respectively.
    """

    class_logger = getLogger("web3client.RpcLog")

    def __init__(
        self,
        rpc_whitelist: List[str] = None,
        fetch_tx_data: bool = False,
        fetch_tx_receipt: bool = False,
        parse_raw_tx_data: bool = True,
    ) -> None:
        """
        :param rpc_whitelist: A list of RPC methods to log.  If None, all
            requests and responses will be logged.
        :param fetch_tx_data: If True, the transaction data will be fetched
            and made available to the ``log_response`` method.  Applies only
            to transactions.
        :param fetch_tx_receipt: If True, the transaction receipt will be
            fetched and made available to the ``log_response`` method.  Applies
            only to transactions.
        :param parse_raw_tx_data: If True, requests parameters will be decoded into
            a TxData object, and made available to the ``log_request`` method.
            Applies only when sending raw transactions (eth_sendRawTransaction).
        """
        self.rpc_whitelist = rpc_whitelist
        self.parse_raw_tx_data = parse_raw_tx_data
        self.fetch_tx_data = fetch_tx_data
        self.fetch_tx_receipt = fetch_tx_receipt
        self.init()

    def init(self) -> None:
        """Initialization function called in the constructor"""
        pass

    def should_log_request(
        self, id: str, method: RPCEndpoint, params: Any, w3: Web3
    ) -> bool:
        """Whether a request should be logged or not"""
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def handle_request(
        self, id: str, method: RPCEndpoint, params: Any, w3: Web3
    ) -> None:
        """Receive a request, pre-process it, and pass it to the logging
        function.  Use the ID to match the response to the request."""
        # Decode tx data if requested
        tx_data = None
        try:
            if self.parse_raw_tx_data:
                if method == "eth_sendRawTransaction":
                    tx_data = parse_raw_tx(params[0])
        except Exception:
            self.class_logger.warning(
                f"Could not parse raw tx in request to '{method}'"
            )
        # Build log entry
        entry = RequestEntry(
            id=id,
            type="request",
            timestamp=datetime.now(),
            method=method,
            params=params,
            parsed_tx_data=tx_data,
            w3=w3,
        )
        # Call logging function
        self.log_request(entry)

    def log_request(self, entry: RequestEntry) -> None:
        """
        Log a request.  Meant to be overridden by subclasses.

        The `parsed_tx_data` field is included in `entry` only if (1) the
        request is a transaction-related request, and (2) the instance has
        self.parse_raw_tx_data=True.
        """
        pass

    def should_log_response(
        self, id: str, method: RPCEndpoint, params: Any, w3: Web3, response: RPCResponse
    ) -> bool:
        """Whether a response should be logged or not"""
        if self.rpc_whitelist is None:
            return True
        return method in self.rpc_whitelist

    def handle_response(
        self,
        id: str,
        method: RPCEndpoint,
        params: Any,
        w3: Web3,
        response: RPCResponse,
        elapsed: float,
    ) -> None:
        """Receive a response, pre-process it, and pass it to the logging
        function.  Use the ID to match the response to the request."""
        ok = is_rpc_response_ok(response)
        # Fetch tx data if requested
        tx_data = None
        if ok and self.fetch_tx_data and method in TX_WRITE_METHODS:
            tx_data = w3.eth.get_transaction(response["result"])
        # Fetch tx receipt if requested
        tx_receipt = None
        if ok and self.fetch_tx_receipt and method in TX_WRITE_METHODS:
            tx_receipt = w3.eth.wait_for_transaction_receipt(response["result"])
        # Build log entry
        entry = ResponseEntry(
            id=id,
            type="response",
            timestamp=datetime.now(),
            method=method,
            params=params,
            response=response,
            elapsed=elapsed,
            tx_data=tx_data,
            tx_receipt=tx_receipt,
            w3=w3,
        )
        # Call logging function
        self.log_response(entry)

    def log_response(self, entry: ResponseEntry) -> None:
        """
        Log a response.  Meant to be overridden by subclasses.

        The tx_data and tx_receipt parameters are passed only if:
        (1) the RPC request submitted a transaction,
        (2) if the instance has fetch_tx_data=True and fetch_tx_receipt=True, respectively, and
        (3) if the request was successful.
        """
        pass


"""
  ___          _     _                   _
 | _ \  _  _  | |_  | |_    ___   _ _   | |     ___   __ _
 |  _/ | || | |  _| | ' \  / _ \ | ' \  | |__  / _ \ / _` |
 |_|    \_, |  \__| |_||_| \___/ |_||_| |____| \___/ \__, |
        |__/                                         |___/
"""


class PythonLog(BaseRpcLog):
    """
    An RPC log class that logs requests and responses to a Python logger, as
    info-level messages.

    Subclasses can override the ``format_request`` and ``format_response``
    methods to customize the format of the logged messages.

    If no logger is provided, the class logger is used, with the name
    "web3client.RpcLog". IMPORTANT: The level of the logger must be
    set to INFO or lower for the messages to be logged.

    To configure the way log messages are shown, use the standard Python logging
    configuration.  For example, to log to file with timestamp:

        import logging
        logger = logging.getLogger("web3client.RpcLog")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("rpc.log")
        fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger.addHandler(fh)

    More examples here:
    https://web3py.readthedocs.io/en/stable/examples.html#adjusting-log-levels
    """

    def __init__(
        self,
        rpc_whitelist: List[str] = None,
        fetch_tx_data: bool = False,
        fetch_tx_receipt: bool = False,
        parse_raw_tx_data: bool = True,
        logger: Logger = None,
    ) -> None:
        super().__init__(
            rpc_whitelist, fetch_tx_data, fetch_tx_receipt, parse_raw_tx_data
        )
        self.logger = logger or self.class_logger

    @override
    def log_request(self, entry: RequestEntry) -> None:
        self.logger.info(self.format_request(entry))

    @override
    def log_response(self, entry: ResponseEntry) -> None:
        self.logger.info(self.format_response(entry))

    def format_request(self, entry: RequestEntry) -> str:
        """Return the log message for a request"""
        e = entry
        msg = f"[REQ {e.method}] ID: {e.id}, Params: {e.params}"
        if e.parsed_tx_data is not None:
            msg += f", Parsed TX data: {e.parsed_tx_data}"
        return msg

    def format_response(self, entry: ResponseEntry) -> str:
        """Return the log message for a response"""
        e = entry
        msg = f"[RES to {e.method}] ID: {e.id}, Params: {e.params}, Response: {e.response}"
        if e.tx_data is not None:
            msg += f", TX data: {e.tx_data}"
        if e.tx_receipt is not None:
            msg += f", TX receipt: {e.tx_receipt}"
        return msg


"""
  __  __                                    _
 |  \/  |  ___   _ __    ___   _ _   _  _  | |     ___   __ _
 | |\/| | / -_) | '  \  / _ \ | '_| | || | | |__  / _ \ / _` |
 |_|  |_| \___| |_|_|_| \___/ |_|    \_, | |____| \___/ \__, |
                                     |__/               |___/
"""


class MemoryLog(BaseRpcLog):
    """An RPC log class that keeps track of requests and responses in the
    self.entries internal attribute"""

    entries: List[Union[RequestEntry, ResponseEntry]]

    @override
    def init(self) -> None:
        self.entries = []

    @override
    def log_request(self, entry: RequestEntry) -> None:
        self.entries.append(entry)

    @override
    def log_response(self, entry: ResponseEntry) -> None:
        self.entries.append(entry)

    def get_requests(self) -> List[RequestEntry]:
        """Returns all requests in the log"""
        return [e for e in self.entries if e.type == "request"]

    def get_responses(self) -> List[ResponseEntry]:
        """Returns all responses in the log"""
        return [e for e in self.entries if e.type == "response"]

    def get_tx_requests(self) -> List[RequestEntry]:
        """Returns the logged requests to RPC methdos that submit a transaction"""
        return [e for e in self.get_requests() if e.method in TX_WRITE_METHODS]

    def get_tx_responses(self) -> List[ResponseEntry]:
        """Returns the logged responses from RPC methdos that submit a transaction"""
        return [e for e in self.get_responses() if e.method in TX_WRITE_METHODS]


"""
  __  __   _      _      _   _
 |  \/  | (_)  __| |  __| | | |  ___  __ __ __  __ _   _ _   ___
 | |\/| | | | / _` | / _` | | | / -_) \ V  V / / _` | | '_| / -_)
 |_|  |_| |_| \__,_| \__,_| |_| \___|  \_/\_/  \__,_| |_|   \___|

"""


def construct_generic_rpc_log_middleware(rpc_log: BaseRpcLog) -> Middleware:
    """
    Constructs a middleware which logs RPC requests and/or responses,
    based on the passed RPC log instance.

    :param rpc_log: A instance of an RPC log class derived from ``BaseRpcLog``.
    """

    def log_middleware(
        make_request: Callable[[RPCEndpoint, Any], RPCResponse], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            # Generate a unique ID for the request-response pair
            request_id = uuid.uuid4().hex
            # Log response
            if rpc_log.should_log_request(request_id, method, params, w3):
                rpc_log.handle_request(request_id, method, params, w3)
            # Time & send the request
            start = datetime.now()
            response = make_request(method, params)
            end = datetime.now()
            # Optionally log response
            if rpc_log.should_log_response(request_id, method, params, w3, response):
                rpc_log.handle_response(
                    request_id,
                    method,
                    params,
                    w3,
                    response,
                    (end - start).total_seconds(),
                )
            return response

        return middleware

    return log_middleware


def construct_tx_rpc_log(
    logger: Logger = None, fetch_tx_data: bool = False, fetch_tx_receipt: bool = False
) -> PythonLog:
    """Return a PythonLog that logs transactions sent to the blockchain"""
    return PythonLog(
        rpc_whitelist=TX_WRITE_METHODS,
        fetch_tx_data=fetch_tx_data,
        fetch_tx_receipt=fetch_tx_receipt,
        logger=logger,
    )


def construct_tx_rpc_log_middleware(
    logger: Logger = None, fetch_tx_data: bool = False, fetch_tx_receipt: bool = False
) -> Middleware:
    """
    Return a middleware that logs transactions sent to the blockchain.

    :param logger: A Python logger instance.  If None, will use the logger
        'web3client.RpcLog'
    :param fetch_tx_data: If True, the transaction data will be fetched and
        logged
    :param fetch_tx_receipt: If True, the transaction receipt will be fetched
        and logged
    """
    rpc_log = construct_tx_rpc_log(
        fetch_tx_data=fetch_tx_data, fetch_tx_receipt=fetch_tx_receipt, logger=logger
    )
    return construct_generic_rpc_log_middleware(rpc_log)


tx_rpc_log = construct_tx_rpc_log()
"""Instance that logs transactions sent to the blockchain, using the logger
named "web3client.RpcLog".  See docs of the PythonLog class for more
details on how to customize the output and destination."""


tx_rpc_log_middleware = construct_tx_rpc_log_middleware()
"""A middleware that logs transactions sent to the blockchain.  See docs of
the PythonLog class for more details on how to customize the output and
destination."""
