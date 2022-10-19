from typing import Any, Union
from eth_typing.encoding import HexStr
from web3client.base_client import BaseClient
from web3.datastructures import AttributeDict
from web3.types import TxReceipt
import pprint


def printTxInfo(client: BaseClient, txHash: HexStr) -> None:
    """
    Get a transaction receipt and print it, together with
    the tx cost
    """
    print(">>> TX SENT!")
    print("Hash = " + txHash)
    print("Waiting for transaction to finalize...")
    tx_receipt = client.getTransactionReceipt(txHash)
    print(">>> TX IS ON THE BLOCKCHAIN :-)")
    pprint.pprint(tx_receipt)
    print(">>> ETH SPENT")
    print(BaseClient.getGasSpentInEth(tx_receipt))


def pprintAttributeDict(
    attributeDict: Union[TxReceipt, AttributeDict[str, Any]]
) -> None:
    """
    Web3 often returns AttributeDict instead of simple Dictionaries;
    this function pretty prints an AttributeDict
    """
    print(formatAttributeDict(attributeDict))


def formatAttributeDict(
    attributeDict: Union[TxReceipt, AttributeDict[str, Any]],
    indent: int = 4,
    nestLevel: int = 0,
) -> str:
    """
    Web3 often returns AttributeDict instead of simple Dictionaries;
    this function return a pretty string with the AttributeDict content
    """
    prefix = nestLevel * indent * " "
    output = prefix + "{\n"
    for key, value in attributeDict.items():
        if isinstance(value, AttributeDict):
            output += prefix + formatAttributeDict(value, indent, nestLevel + 1)
            output += "\n"
        else:
            output += prefix + " " * indent
            output += f"{key} -> {pprint.pformat(value, indent=indent)}"
            output += "\n"
    output += prefix + "}"

    return output
