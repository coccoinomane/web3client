"""
PyTest Fixtures.
"""

import json
from pathlib import Path
from typing import Any, Iterator, List, cast

import pytest
from web3.types import ABI

import ape
from tests.ape.tests.helpers.compound_v2 import (
    deploy_cerc20,
    deploy_cether,
    deploy_comptroller,
    deploy_interest_rate_model,
)
from tests.ape.tests.helpers.token import deploy_token

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
def alice(accounts: ape.managers.accounts.AccountManager) -> ape.api.AccountAPI:
    """A Brownie account preloaded in the local chain"""
    return accounts[0]


@pytest.fixture(scope="session")
def bob(accounts: ape.managers.accounts.AccountManager) -> ape.api.AccountAPI:
    """A Brownie account preloaded in the local chain"""
    return accounts[1]


@pytest.fixture(scope="session")
def accounts_keys() -> Iterator[List[str]]:
    """Private keys of the local accounts created by ape.
    There are just the keys from the mnemonic phrase
    'test test test test test test test test test test test junk'
    following the standard path m/44'/60'/0'/0/{account_index}"""
    yield [
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
def simple_abi() -> Iterator[ABI]:
    """A simple ABI for a contract with a single function"""
    yield [
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


#   ____                   _             _
#  / ___|   ___    _ __   | |_    __ _  (_)  _ __     ___   _ __   ___
# | |      / _ \  | '_ \  | __|  / _` | | | | '_ \   / _ \ | '__| / __|
# | |___  | (_) | | | | | | |_  | (_| | | | | | | | |  __/ | |    \__ \
#  \____|  \___/  |_| |_|  \__|  \__,_| |_| |_| |_|  \___| |_|    |___/


@pytest.fixture(scope="function")
def Token() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("Token")


@pytest.fixture(scope="function")
def CompoundV2Comptroller() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("Comptroller")


@pytest.fixture(scope="function")
def CompoundV2InterestRateModel() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("WhitePaperInterestRateModel")


@pytest.fixture(scope="function")
def CompoundV2FixedPriceOracle() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("FixedPriceOracle")


@pytest.fixture(scope="function")
def CompoundV2Erc20() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("CErc20Immutable")


@pytest.fixture(scope="function")
def CompoundV2Ether() -> ape.contracts.ContractContainer:
    return ape.project.get_contract("CEther")


#  _____           _
# |_   _|   ___   | | __   ___   _ __    ___
#   | |    / _ \  | |/ /  / _ \ | '_ \  / __|
#   | |   | (_) | |   <  |  __/ | | | | \__ \
#   |_|    \___/  |_|\_\  \___| |_| |_| |___/


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


#    ____                                                           _
#   / ___|   ___    _ __ ___    _ __     ___    _   _   _ __     __| |
#  | |      / _ \  | '_ ` _ \  | '_ \   / _ \  | | | | | '_ \   / _` |
#  | |___  | (_) | | | | | | | | |_) | | (_) | | |_| | | | | | | (_| |
#   \____|  \___/  |_| |_| |_| | .__/   \___/   \__,_| |_| |_|  \__,_|
#                              |_|


@pytest.fixture(scope="function")
def compound_v2_price_oracle(
    accounts: ape.managers.accounts.AccountManager,
    CompoundV2FixedPriceOracle: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """The Compound V2 price oracle contract.  This is a simple
    implementation that sets the price of each token to 1 ETH."""
    return CompoundV2FixedPriceOracle.deploy(10**18, sender=accounts[0])


@pytest.fixture(scope="function")
def compound_v2_comptroller(
    accounts: ape.managers.accounts.AccountManager,
    CompoundV2Comptroller: ape.contracts.ContractContainer,
    compound_v2_price_oracle: ape.contracts.ContractInstance,
) -> ape.contracts.ContractInstance:
    """The Compound V2 comptroller contract."""
    return deploy_comptroller(accounts, CompoundV2Comptroller, compound_v2_price_oracle)


@pytest.fixture(scope="function")
def compound_v2_interest_rate_model(
    accounts: ape.managers.accounts.AccountManager,
    CompoundV2InterestRateModel: ape.contracts.ContractContainer,
) -> ape.contracts.ContractInstance:
    """The Compound V2 interest rate model contract.  Parameters taken from
    the Ethereum contract (0xc64C4cBA055eFA614CE01F4BAD8A9F519C4f8FaB)"""
    return deploy_interest_rate_model(
        accounts,
        CompoundV2InterestRateModel,
        base_rate=0,
        multiplier=int(0.2 * 10**18),
    )


@pytest.fixture(scope="function")
def compound_v2_ceth(
    accounts: ape.managers.accounts.AccountManager,
    CompoundV2Ether: ape.contracts.ContractContainer,
    compound_v2_comptroller: ape.contracts.ContractInstance,
    compound_v2_interest_rate_model: ape.contracts.ContractInstance,
) -> ape.contracts.ContractInstance:
    """The contract for the Compound V2 cETH money market"""
    return deploy_cether(
        accounts,
        CompoundV2Ether,
        compound_v2_comptroller,
        compound_v2_interest_rate_model,
    )


@pytest.fixture(scope="function")
def compound_v2_ctst(
    accounts: ape.managers.accounts.AccountManager,
    CompoundV2Erc20: ape.contracts.ContractContainer,
    compound_v2_comptroller: ape.contracts.ContractInstance,
    compound_v2_interest_rate_model: ape.contracts.ContractInstance,
    TST: ape.contracts.ContractInstance,
) -> ape.contracts.ContractInstance:
    """The contract for the Compound V2 cTST money market, where
    TST is the underlying asset"""
    return deploy_cerc20(
        accounts,
        CompoundV2Erc20,
        TST,
        compound_v2_comptroller,
        compound_v2_interest_rate_model,
    )
