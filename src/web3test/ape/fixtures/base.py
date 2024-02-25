"""
PyTest Fixtures.
"""

from typing import Any, List, cast

import pytest
from web3.types import ABI

import ape

#   ____   _               _
#  / ___| | |__     __ _  (_)  _ __
# | |     | '_ \   / _` | | | | '_ \
# | |___  | | | | | (_| | | | | | | |
#  \____| |_| |_|  \__,_| |_| |_| |_|


@pytest.fixture(scope="session")
def ape_chain(
    chain: ape.managers.chain.ChainManager,
) -> ape.managers.chain.ChainManager:
    """Alias for the 'chain' fixture of Brownie, to avoid naming
    conflicts with the Chain model of web3core."""
    return chain


@pytest.fixture(scope="session")
def ape_chain_uri(
    chain: ape.managers.chain.ChainManager,
) -> str:
    """Return the URI of the local chain"""
    try:
        return cast(Any, chain.provider).uri
    except AttributeError:
        try:
            return cast(Any, chain.provider).web3.provider.endpoint_uri
        except AttributeError:
            return "http://localhost:8545"


@pytest.fixture(scope="session")
def is_eip1559(
    chain: ape.managers.chain.ChainManager,
) -> bool:
    """Return True if the local chain supports eip1599 (type 2 transactions)."""
    return hasattr(chain.blocks[0], "base_fee") or hasattr(
        chain.blocks[0], "base_fee_per_gas"
    )


@pytest.fixture(scope="session")
def ape_chain_name(
    chain: ape.managers.chain.ChainManager,
) -> str:
    """Return whether we are running tests on ganache or anvil."""
    if chain.chain_id == 1337:
        return "ganache"
    elif chain.chain_id == 31337:
        return "anvil"
    raise ValueError(f"Unknown chain type '{chain.chain_id}'")


#     _                                            _
#    / \      ___    ___    ___    _   _   _ __   | |_   ___
#   / _ \    / __|  / __|  / _ \  | | | | | '_ \  | __| / __|
#  / ___ \  | (__  | (__  | (_) | | |_| | | | | | | |_  \__ \
# /_/   \_\  \___|  \___|  \___/   \__,_| |_| |_|  \__| |___/


@pytest.fixture(scope="session")
def alice(
    accounts: ape.managers.accounts.AccountManager, accounts_keys: List[str]
) -> ape.api.AccountAPI:
    """A Brownie account preloaded in the local chain"""
    accounts[0].private_key = accounts_keys[0]
    return accounts[0]


@pytest.fixture(scope="session")
def bob(
    accounts: ape.managers.accounts.AccountManager, accounts_keys: List[str]
) -> ape.api.AccountAPI:
    """A Brownie account preloaded in the local chain"""
    accounts[1].private_key = accounts_keys[1]
    return accounts[1]


@pytest.fixture(scope="session")
def alice_private_key(accounts_keys: List[str]) -> str:
    return accounts_keys[0]


@pytest.fixture(scope="session")
def bob_private_key(accounts_keys: List[str]) -> str:
    return accounts_keys[1]


@pytest.fixture(scope="session")
def accounts_keys() -> List[str]:
    """Private keys of the local accounts created by ape.
    There are just the keys from the mnemonic phrase
    'test test test test test test test test test test test junk'
    following the standard path m/44'/60'/0'/0/{account_index}"""
    return [
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
        "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
        "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
        "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
        "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
        "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
        "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",
        "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
        "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",
        "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",
    ]


#     _      ____    ___
#    / \    | __ )  |_ _|
#   / _ \   |  _ \   | |
#  / ___ \  | |_) |  | |
# /_/   \_\ |____/  |___|


@pytest.fixture(scope="session")
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
