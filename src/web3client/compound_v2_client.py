from typing import List, cast

from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client
from web3client.exceptions import Web3ClientException


class CompoundV2CErc20Client(Erc20Client):
    """
    Client loaded with the contract of a Compound V2 market
    of type ERC20 preloaded (https://docs.compound.finance/v2/ctokens/).
    """

    abi = BaseClient.get_abi_json("compound_v2_cerc20.json")

    ####################
    # Read
    ####################

    def underlying(self) -> str:
        """Get the address of the underlying asset"""
        return self.functions.underlying().call()

    def exchange_rate_stored(self) -> int:
        """Get the stored exchange rate from cToken to underlying"""
        return self.functions.exchangeRateStored().call()

    ####################
    # Write
    ####################

    def approve_and_supply(self, amount: int) -> None:
        """Supply tokens to the Compound V2 pool, first approving"""
        underlying_client = cast(
            Erc20Client,
            self.clone(Erc20Client).set_contract(self.functions.underlying().call()),
        )
        self.get_tx_receipt(underlying_client.approve(self.contract_address, amount))
        self.transact(self.functions.mint(amount))

    def supply(self, amount: int) -> None:
        """Supply tokens to the Compound V2 pool"""
        self.transact(self.functions.mint(amount))

    ####################
    # Utils
    ####################

    def get_underlying_client(self) -> Erc20Client:
        """Get the underlying token client"""
        return cast(
            Erc20Client,
            self.clone().set_contract(self.functions.underlying().call()),
        )


class CompoundV2CEtherClient(CompoundV2CErc20Client):
    """Client loaded with the contract of a Compound V2 market
    of type ETH (https://docs.compound.finance/v2/ctokens/)."""

    abi = BaseClient.get_abi_json("compound_v2_ceth.json")

    ####################
    # Read
    ####################

    def underlying(self) -> str:
        raise Web3ClientException("CEther market does not have an underlying token")

    ####################
    # Write
    ####################

    def supply(self, amount: int) -> None:
        """Supply ETH to the Compound V2 pool"""
        self.transact(self.functions.mint(), value_in_wei=amount)


class CompoundV2ComptrollerClient(BaseClient):
    """
    Client loaded with the contract of a Compound V2 comptroller
    (https://docs.compound.finance/v2/comptroller/).
    """

    abi = BaseClient.get_abi_json("compound_v2_comptroller.json")

    ####################
    # Read
    ####################

    def get_all_markets(self) -> List[str]:
        """Get the list of all listed (enabled) markets"""
        return self.call(self.functions.getAllMarkets())

    def is_listed(self, c_token_address: str) -> bool:
        """Check if a market is listed (enabled)"""
        return self.call(self.functions.markets(c_token_address))[0]

    def collateral_factor(self, c_token_address: str) -> int:
        """Get the collateral factor of the given market.
        The returned value is the collateralFactorMantissa, scaled
        by 1e18, and multiplied by a supply balance to determine
        how much value can be borrowed."""
        return self.call(self.functions.markets(c_token_address))[1]

    def get_assets_in(self, address: str) -> List[str]:
        """Get the list of markets an account is currently entered into.
        In order to supply collateral or borrow in a market, it must
        be entered first"""
        return self.call(self.functions.getAssetsIn(address))

    ####################
    # Write
    ####################

    def enter_market(self, c_token_address: str) -> None:
        """Enable collateral for a market"""
        self.transact(self.functions.enterMarkets([c_token_address]))

    def exit_market(self, c_token_address: str) -> None:
        """Disable collateral for a market"""
        self.transact(self.functions.exitMarket(c_token_address))

    def list_market(self, c_token_address: str) -> None:
        """Enable a market (admin function)"""
        self.transact(self.functions._supportMarket(c_token_address))
