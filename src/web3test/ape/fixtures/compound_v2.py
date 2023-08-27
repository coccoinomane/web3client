"""
PyTest Fixtures.
"""

import pytest

import ape
from web3test.ape.helpers.compound_v2 import (
    deploy_cerc20,
    deploy_cether,
    deploy_comptroller,
    deploy_interest_rate_model,
)


@pytest.fixture(scope="function")
def CompoundV2Comptroller() -> ape.contracts.ContractContainer:
    """Use this to deploy a Compound V2 comptroller contract."""
    return ape.project.get_contract("Comptroller")


@pytest.fixture(scope="function")
def CompoundV2InterestRateModel() -> ape.contracts.ContractContainer:
    """Use this to deploy the Compound V2 white paper interest rate model contract."""
    return ape.project.get_contract("WhitePaperInterestRateModel")


@pytest.fixture(scope="function")
def CompoundV2FixedPriceOracle() -> ape.contracts.ContractContainer:
    """Use this to deploy a test fixed price oracle contract for Compound V2."""
    return ape.project.get_contract("FixedPriceOracle")


@pytest.fixture(scope="function")
def CompoundV2Erc20() -> ape.contracts.ContractContainer:
    """Use this to deploy a Compound V2 ERC20 market contract."""
    return ape.project.get_contract("CErc20Immutable")


@pytest.fixture(scope="function")
def CompoundV2Ether() -> ape.contracts.ContractContainer:
    """Use this to deploy a Compound V2 Ether market contract."""
    return ape.project.get_contract("CEther")


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
