"""
PyTest Fixtures.
"""

import json
from pathlib import Path

import pytest
from web3.types import ABI

import ape


@pytest.fixture()
def simple_abi() -> ABI:
    """A simple ABI for a contract with a single function"""
    return [
        {
            "constant": False,
            "inputs": [{"name": "a", "type": "uint256"}],
            "name": "foo",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function",
        }
    ]


@pytest.fixture()
def erc20_abi_string() -> str:
    """The ABI for the ERC20 token standard, as a string"""
    return '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'


@pytest.fixture()
def erc20_abi_file(tmp_path: Path, erc20_abi_string: str) -> str:
    """The path of a JSON file containing the ABI for the ERC20 token
    standard"""
    f = tmp_path / "erc20.json"
    f.write_text(erc20_abi_string)
    return str(f)


@pytest.fixture()
def erc20_abi(erc20_abi_string: str) -> ABI:
    """The ABI for the ERC20 token standard, as a JSON object"""
    return json.loads(erc20_abi_string)


@pytest.fixture()
def alice() -> ape.api.accounts.AccountAPI:
    """An ape account preloaded in the local chain"""
    return ape.accounts[0]


@pytest.fixture()
def bob() -> ape.api.accounts.AccountAPI:
    """An ape account preloaded in the local chain"""
    return ape.accounts[1]
