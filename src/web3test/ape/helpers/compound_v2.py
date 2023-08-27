import ape


def deploy_comptroller(
    accounts: ape.managers.accounts.AccountManager,
    comptroller_container: ape.contracts.ContractContainer,
    price_oracle_instance: ape.contracts.ContractInstance,
) -> ape.contracts.ContractInstance:
    """Deploy the Compound comptroller (https://docs.compound.finance/v2/comptroller/).
    On Ethereum:
    - implementation: https://etherscan.io/address/0xBafE01ff935C7305907c33BF824352eE5979B526#code
    - proxy: https://etherscan.io/address/0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B#code
    To call Comptroller functions, use the Comptroller ABI on the Unitroller address.
    """
    comptroller = comptroller_container.deploy(sender=accounts[0])
    comptroller._setPriceOracle(price_oracle_instance, sender=accounts[0])
    return comptroller


def deploy_interest_rate_model(
    accounts: ape.managers.accounts.AccountManager,
    interest_rate_model_container: ape.contracts.ContractContainer,
    base_rate: int,
    multiplier: int,
) -> ape.contracts.ContractInstance:
    """Deploy the Compound interest rate model.  On Ethereum:
    https://etherscan.io/address/0xc64C4cBA055eFA614CE01F4BAD8A9F519C4f8FaB#code
    """
    return interest_rate_model_container.deploy(
        base_rate, multiplier, sender=accounts[0]
    )


def deploy_cerc20(
    accounts: ape.managers.accounts.AccountManager,
    cerc20_container: ape.contracts.ContractContainer,
    underlying_token_instance: ape.contracts.ContractInstance,
    comptroller_instance: ape.contracts.ContractInstance,
    interest_rate_model_instance: ape.contracts.ContractInstance,
    initial_exchange_rate_mantissa: int = 200000000000000,  # 0.02 * 10 ** (6 - 8) * 10**18
    name: str = "CompoundTestToken",
    symbol: str = "cTST",
    decimals: int = 8,
    collateral_factor: int = 9 * 10**17,
) -> ape.contracts.ContractInstance:
    """Deploy a Compound pool with an underlying test token.
    See constructor arguments here:
    https://etherscan.io/address/0x39AA39c021dfbaE8faC545936693aC917d5E7563#code
    """
    cerc20 = cerc20_container.deploy(
        underlying_token_instance,
        comptroller_instance,
        interest_rate_model_instance,
        initial_exchange_rate_mantissa,
        name,
        symbol,
        decimals,
        accounts[0],
        sender=accounts[0],
    )
    # List cTST on the comptroller
    comptroller_instance._supportMarket(cerc20, sender=accounts[0])
    # Set collateral factor
    comptroller_instance._setCollateralFactor(
        cerc20, collateral_factor, sender=accounts[0]
    )
    return cerc20


def deploy_cether(
    accounts: ape.managers.accounts.AccountManager,
    ceth_container: ape.contracts.ContractContainer,
    comptroller_instance: ape.contracts.ContractInstance,
    interest_rate_model_instance: ape.contracts.ContractInstance,
    initial_exchange_rate_mantissa: int = 200000000000000000000000000,  # 0.02 * 10 ** (18 - 8) * 10**18
    name: str = "CompoundETH",
    symbol: str = "cETH",
    decimals: int = 8,
    collateral_factor: int = 9 * 10**17,
) -> ape.contracts.ContractInstance:
    """Deploy a Compound pool with ETH.  The difference is that
    there is no underlying token.  See constructor arguments here:
    https://etherscan.io/address/0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5#code
    """
    ceth = ceth_container.deploy(
        comptroller_instance,
        interest_rate_model_instance,
        initial_exchange_rate_mantissa,
        name,
        symbol,
        decimals,
        accounts[0],
        sender=accounts[0],
    )
    # List cETH as a supported market
    comptroller_instance._supportMarket(ceth, sender=accounts[0])
    # Set collateral factor
    comptroller_instance._setCollateralFactor(
        ceth, collateral_factor, sender=accounts[0]
    )
    return ceth
