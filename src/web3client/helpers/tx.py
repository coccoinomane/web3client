from typing import cast

from eth.abc import SignedTransactionAPI
from eth.vm.forks.arrow_glacier.transactions import (
    ArrowGlacierTransactionBuilder as TransactionBuilder,
)
from eth_utils import encode_hex, to_bytes
from hexbytes import HexBytes
from web3 import Web3
from web3.types import AccessList, Nonce, TxData, Wei


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
