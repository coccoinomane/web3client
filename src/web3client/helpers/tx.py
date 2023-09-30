from typing import Any, Dict, cast

from eth.abc import SignedTransactionAPI
from eth.vm.forks.arrow_glacier.transactions import (
    ArrowGlacierTransactionBuilder as TransactionBuilder,
)
from eth_utils import encode_hex, to_bytes
from hexbytes import HexBytes
from web3 import Web3
from web3.types import AccessList, Nonce, RPCResponse, TxData, Wei


def parse_raw_tx_pyevm(raw_tx: str) -> SignedTransactionAPI:
    """Convert a raw transaction to a py-evm signed transaction object.

    Inspired by:
     - https://github.com/ethereum/web3.py/issues/3109#issuecomment-1737744506
     - https://snakecharmers.ethereum.org/web3-py-patterns-decoding-signed-transactions/
    """
    return TransactionBuilder().decode(to_bytes(hexstr=raw_tx))


def parse_raw_tx(raw_tx: str) -> TxData:
    """Convert a raw transaction to a web3.py TxData dict.

    Inspired by:
     - https://ethereum.stackexchange.com/a/83855/89782
     - https://docs.ethers.org/v5/api/utils/transactions/#utils-parseTransaction
    """
    tx = parse_raw_tx_pyevm(raw_tx)

    return {
        "accessList": cast(AccessList, tx.access_list),
        "blockHash": None,
        "blockNumber": None,
        "chainId": tx.chain_id,
        "data": HexBytes(Web3.to_hex(tx.data)),
        "from": Web3.to_checksum_address(encode_hex(tx.sender)),
        "gas": tx.gas,
        "gasPrice": None if tx.type_id is not None else cast(Wei, tx.gas_price),
        "maxFeePerGas": cast(Wei, tx.max_fee_per_gas),
        "maxPriorityFeePerGas": cast(Wei, tx.max_priority_fee_per_gas),
        "hash": HexBytes(tx.hash),
        "input": None,
        "nonce": cast(Nonce, tx.nonce),
        "r": HexBytes(tx.r),
        "s": HexBytes(tx.s),
        "to": Web3.to_checksum_address(tx.to),
        "transactionIndex": None,
        "type": tx.type_id,
        "v": None,
        "value": cast(Wei, tx.value),
    }


def parse_estimate_gas_tx(params: Dict[str, Any]) -> TxData:
    """Takes the parameters passed to the RPC method eth_estimateGas
    and returns a TxData dict with them"""

    maxFeePerGas = (
        cast(Wei, int(params["maxFeePerGas"], 16))
        if params.get("maxFeePerGas")
        else None
    )
    maxPriorityFeePerGas = (
        cast(Wei, int(params["maxPriorityFeePerGas"], 16))
        if params.get("maxPriorityFeePerGas")
        else None
    )
    gasPrice = cast(
        Wei, int(params["gasPrice"], 16) if params.get("gasPrice") else None
    )

    return {
        "accessList": params.get("accessList", ()),
        "blockHash": None,
        "blockNumber": None,
        "chainId": int(params["chainId"], 16) if params.get("chainId") else None,
        "data": HexBytes(params["data"]) if params.get("data") else None,
        "from": params.get("from", None),
        "gas": params.get("gas", None),
        "gasPrice": gasPrice,
        "maxFeePerGas": maxFeePerGas,
        "maxPriorityFeePerGas": maxPriorityFeePerGas,
        "hash": None,
        "input": None,
        "nonce": cast(Nonce, int(params["nonce"], 16)) if params.get("nonce") else None,
        "r": None,
        "s": None,
        "to": params.get("to", None),
        "transactionIndex": None,
        "type": int(params["type"], 16) if params.get("type") else None,
        "v": None,
        "value": cast(Wei, int(params["value"], 16) if params.get("value") else 0),
    }


def parse_call_tx(params: Dict[str, Any]) -> TxData:
    """Takes the parameters passed to the RPC method eth_call
    and returns a TxData dict with them.  This is treated exactly the same as an
    eth_estimateGas call."""
    return parse_estimate_gas_tx(params)


def is_rpc_response_ok(response: RPCResponse) -> bool:
    """Check if an RPC response did not error"""
    return (
        "error" not in response
        and "result" in response
        and response["result"] is not None
    )
