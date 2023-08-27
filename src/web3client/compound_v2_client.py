from typing import List, cast

from eth_typing import HexStr

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

    def underlying_balance(self, address: str = None) -> int:
        """Get the balance of the given address in the underlying
        token; will default to the current authenticated account"""
        return self.get_underlying_client().balance_in_wei(address)

    def exchange_rate(self) -> int:
        """Get the stored exchange rate from cToken to underlying"""
        return self.functions.exchangeRateStored().call()

    def solvency(self) -> float:
        """Get the ratio between the market liquidity and its total
        borrows.  If this number is above 1, the market is solvent,
        and all borrowers could in principle withdraw at the same time."""
        liquidity = self.liquidity()
        if liquidity == 0:
            return 0
        total_borrowed = self.total_borrowed()
        if total_borrowed == 0:
            return float("inf")
        return liquidity / total_borrowed

    def liquidity(self) -> int:
        """Get the amount of underlying tokens in the market.  This should
        be equal to the supplied collateral minus the total borrows, but
        it can be smaller if the market has been drained by an exploit"""
        return self.functions.getCash().call()

    def borrowed(self, address: str = None) -> int:
        """Get the amount borrowed by the given account;
        will default to the current authenticated account"""
        if not address:
            address = self.user_address
        return self.functions.borrowBalanceCurrent(address).call()

    def total_borrowed(self) -> int:
        """Get the total amount of underlying loaned out by
        the market"""
        return self.functions.totalBorrows().call()

    def supplied(self, address: str = None) -> int:
        """Get the amount supplied to the market by the given
        account, in the underlying token; will default to the
        current authenticated account.

        This function gets the stored exchange rate and converts
        the supplied cTokens in underlying tokens.  An alternative
        would be to call self.functions.balanceOfUnderlying, but that
        would require actually sending a signed transaction."""
        return self.supplied_in_ctokens(address) * self.exchange_rate() // 10**18

    def total_supplied(self) -> int:
        """Get the total amount of underlying tokens supplied to the market.
        This is different than the available tokens (i.e. cash), which are
        returned by self.liquidity()

        NOT TESTED YET!"""
        c_tokens_supply = self.total_supply()
        return c_tokens_supply * self.exchange_rate() // 10**18

    def supplied_in_ctokens(self, address: str = None) -> int:
        """Get the amount of cTokens owned by the given account;
        will default to the current authenticated account"""
        if not address:
            address = self.user_address
        return self.functions.balanceOf(address).call()

    ####################
    # Write
    ####################

    def supply(self, amount: int) -> HexStr:
        """Supply tokens to the Compound V2 market"""
        return self.transact(self.functions.mint(amount))

    def approve_and_supply(self, amount: int) -> HexStr:
        """Supply tokens to the Compound V2 market, first approving"""
        self.get_tx_receipt(
            self.get_underlying_client().approve(self.contract_address, amount)
        )
        return self.supply(amount)

    def borrow(self, amount: int) -> HexStr:
        """Borrow tokens to the Compound V2 market"""
        return self.transact(self.functions.borrow(amount))

    def withdraw(self, amount: int) -> HexStr:
        """Withdraw (redeem) tokens from the Compound V2 market
        IMPORTANT: Never withdraw too much, lest you risk liquidation"""
        return self.transact(self.functions.redeemUnderlying(amount))

    def withdraw_in_ctokens(self, amount: int) -> HexStr:
        """Return (redeem) cTokens to the Compound V2 market
        IMPORTANT: Never withdraw too much, lest you risk liquidation"""
        return self.transact(self.functions.redeem(amount))

    def withdraw_all(self) -> HexStr:
        """Withdraw (redeem) all tokens from the Compound V2 market.
        IMPORTANT: Never withdraw too much, lest you risk liquidation"""
        return self.withdraw_in_ctokens(self.supplied_in_ctokens())

    def repay(self, amount: int) -> HexStr:
        """Repay tokens to the Compound V2 market, to reduce the
        amount borrowed"""
        return self.transact(self.functions.repayBorrow(amount))

    def approve_and_repay(self, amount: int) -> HexStr:
        """Repay tokens to the Compound V2 market, to reduce the
        amount borrowed, first approving"""
        self.get_tx_receipt(
            self.get_underlying_client().approve(self.contract_address, amount)
        )
        return self.repay(amount)

    def repay_all(self) -> HexStr:
        """Repay all tokens to the Compound V2 market, to reduce the
        amount borrowed to zero"""
        return self.repay(2**256 - 1)

    def approve_and_repay_all(self, extra_approve: float = 0.01) -> HexStr:
        """Repay all tokens to the Compound V2 market, to reduce the
        amount borrowed to zero, first approving.

        By default, the function will approve 1% more tokens than the
        borrowed amount, to account for the negative interest that will
        be accrued while the transaction resolves."""
        borrowed = self.borrowed()
        self.get_tx_receipt(
            self.get_underlying_client().approve(
                self.contract_address, int(borrowed * (1 + extra_approve))
            )
        )
        return self.repay_all()

    ####################
    # Utils
    ####################

    def is_eth(self) -> bool:
        """Whether this market is for the chain's native coin
        (True) or for an ERC20 token (False)"""
        return False

    def get_underlying_client(self) -> Erc20Client:
        """Get the underlying token client"""
        return cast(
            Erc20Client,
            self.clone(Erc20Client).set_contract(self.underlying()),
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

    def underlying_balance(self, address: str = None) -> int:
        """Get the balance of the given address in ETH; will default
        to the current authenticated account"""
        return self.get_balance_in_wei(address)

    ####################
    # Write
    ####################

    def approve_and_supply(self, amount: int) -> HexStr:
        """Approving does not make sense for ETH, so just supply
        ETH to the Compound V2 market"""
        return self.supply(amount)

    def approve_and_repay(self, amount: int) -> HexStr:
        """Approving does not make sense for ETH, so just repay
        ETH to the Compound V2 market"""
        return self.repay(amount)

    def approve_and_repay_all(self, extra_approve: float = None) -> HexStr:
        """Approving does not make sense for ETH, so just repay
        ETH to the Compound V2 market"""
        return self.repay_all()

    def supply(self, amount: int) -> HexStr:
        """Supply ETH to the Compound V2 market"""
        return self.transact(self.functions.mint(), value_in_wei=amount)

    def repay(self, amount: int) -> HexStr:
        """Repay ETH to the Compound V2 market, to reduce the
        amount borrowed"""
        return self.transact(self.functions.repayBorrow(), value_in_wei=amount)

    def repay_all(self) -> HexStr:
        """Repay all ETH to the Compound V2 market.

        Alas, this function won't reduce the borrowed amount to zero.
        By the time the transaction is resolved, your position will have
        accrued negative interest, and you will still be in debt by a
        tiny amount.  While for ERC20 tokens this is not a problem, for
        ETH this is a problem.

        Sources:
        - https://discord.com/channels/402910780124561410/402912055448961034/855058058393026600
        - https://discord.com/channels/402910780124561410/402910780670083094/1086345005884514374

        """
        return self.repay(self.borrowed())

    ####################
    # Utils
    ####################

    def is_eth(self) -> bool:
        """Whether this market is for the chain's native coin
        (True) or for an ERC20 token (False)"""
        return True

    def get_underlying_client(self) -> Erc20Client:
        raise Web3ClientException("CEther market does not have an underlying token")


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

    def enter_market(self, c_token_address: str) -> HexStr:
        """Enable collateral for a market"""
        return self.transact(self.functions.enterMarkets([c_token_address]))

    def exit_market(self, c_token_address: str) -> HexStr:
        """Disable collateral for a market"""
        return self.transact(self.functions.exitMarket(c_token_address))

    def list_market(self, c_token_address: str) -> HexStr:
        """Enable a market (admin function)"""
        return self.transact(self.functions._supportMarket(c_token_address))
