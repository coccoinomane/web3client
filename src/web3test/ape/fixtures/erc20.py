"""
PyTest Fixtures.
"""

import json
from pathlib import Path
from typing import Iterator

import pytest
from web3.types import ABI

import ape
from web3test.ape.helpers.token import deploy_token


@pytest.fixture(scope="session")
def erc20_abi_string() -> Iterator[str]:
    """The ABI for the ERC20 token standard, as a string"""
    yield '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]'


@pytest.fixture(scope="function")
def erc20_abi_file(tmp_path: Path, erc20_abi_string: str) -> Iterator[str]:
    """The path of a JSON file containing the ABI for the ERC20 token
    standard"""
    f = tmp_path / "erc20.json"
    f.write_text(erc20_abi_string)
    yield str(f)


@pytest.fixture(scope="session")
def erc20_abi(erc20_abi_string: str) -> Iterator[ABI]:
    """The ABI for the ERC20 token standard, as a JSON object"""
    yield json.loads(erc20_abi_string)


@pytest.fixture(scope="function")
def Token() -> ape.contracts.ContractContainer:
    """The token contract container, which can be used to deploy token
    contracts on the local chain"""
    return ape.project.get_contract("Token")


@pytest.fixture(scope="function")
def WETH(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """A token deployed on the local chain, with 18 decimals, that
    we will use as if it were WETH. Supply of 1 billion tokens, shared between
    all accounts."""
    return deploy_token(
        accounts,
        Token,
        f"WrappedEther",
        f"WETH",
        18,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST token deployed on the local chain, with 18 decimals.
    Supply of 1 billion tokens, shared between all accounts."""
    return deploy_token(
        accounts,
        Token,
        f"Test token (18 decimals)",
        f"TST",
        18,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST_0(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST_0 token deployed on the local chain, with 18 decimals.
    Supply of 1 billion tokens, shared between all accounts."""
    return deploy_token(
        accounts,
        Token,
        f"Test token 0 (18 decimals)",
        f"TST_0",
        18,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST_1(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST_1 token deployed on the local chain, with 18 decimals.
    Supply of 1 billion tokens, shared between all accounts."""
    return deploy_token(
        accounts,
        Token,
        f"Test token 1 (18 decimals)",
        f"TST_1",
        18,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST6(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST6 token deployed on the local chain, with 6 decimals.
    Supply of 1 billion tokens, shared between all accounts"""
    return deploy_token(
        accounts,
        Token,
        f"Test token (6 decimals)",
        f"TST6",
        6,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST6_0(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST6_0 token deployed on the local chain, with 6
    decimals; each account will have a billion tokens"""
    return deploy_token(
        accounts,
        Token,
        f"Test token 0 (6 decimals)",
        f"TST6_0",
        6,
        10**9,
        True,
    )


@pytest.fixture(scope="function")
def TST6_1(
    accounts: ape.managers.accounts.AccountManager,
    Token: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """TST6_1 token deployed on the local chain, with 6
    decimals; each account will have a billion tokens"""
    return deploy_token(
        accounts,
        Token,
        f"Test token 1 (6 decimals)",
        f"TST6_1",
        6,
        10**9,
        True,
    )
