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
        "0xdd23ca549a97cb330b011aebb674730df8b14acaee42d211ab45692699ab8ba5",
        "0xf1aa5a7966c3863ccde3047f6a1e266cdc0c76b399e256b8fede92b1c69e4f4e",
        "0x43f149de89d64bf9a9099be19e1b1f7a4db784af8fa07caf6f08dc86ba65636b",
        "0xb0ff29f0f33edc39aaf8789ea9637c360f9e479b8755f4565652b2594f8835df",
        "0x6789ede33b84cbd4e735e12924d07e48b15df0ded10de3c206eeac585852ab22",
        "0xefba7c0fc77822d0e13b0c36249b129628abff7be84c6b86d8d3444f14618361",
        "0xcbd4d57ea225a831c496b5305d542579222ebdef58a02ea61d55ec1ebecdeb3a",
        "0xb08786f38934aac966d10f0bc79a72f15067896d3b3beba721b5c235ffc5cc5f",
        "0x4a354f72d8069e05fa0a19218ef561dde1db5f78c3d46f2005f9706706171d94",
        "0x16dd30d52297ff9973cbbd5f35c0fef37309fbbfd5b540615b255fbeb8c1283d",
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
