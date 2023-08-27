from decimal import Decimal
from functools import cached_property

from eth_typing import HexStr
from web3 import Web3
from web3.types import Nonce

from web3client.base_client import BaseClient


class Erc20Client(BaseClient):
    """
    Client that comes with the ERC20 ABI preloaded.

    It allows you to call the contract functions as class methods:
    transfer, balanceOf, name, etc.

    If you pass  a private key, it will allow you to call the
    write functions (transfer, approve, etc.)

    The token properties (name, symbol, total_supply, decimals) can be
    accessed as attributes, and are cached.

    AMOUNTS
    =======

    Whenever we will refer to an "amount" of the token, we really mean an
    amount in the smallest subdivision of the token (e.g. wei). For example:
    - If the token has 6 decimals (like most stablecoins) an amount of 1
      corresponds to one millionth of the token.
    - For tokens with 18 decimals (like most non-stablecoins) an amount
      of 1 is equal to 1/10^18 of the token (a single wei).
    """

    abi = BaseClient.get_abi_json("erc20.json")

    ####################
    # Read
    ####################

    def balance(self, address: str = None) -> Decimal:
        """
        Return the amount of the ERC20 token held by the given
        address; if no address is specified, return the amount
        held by the client's account
        """
        balance_in_wei = self.balance_in_wei(address)
        return self.from_wei(balance_in_wei, self.decimals)

    def balance_in_wei(self, address: str = None) -> int:
        """
        Return the amount of the ERC20 token held by the given address,
        in wei; if no address is specified, return the amount held by
        the client's account
        """
        if not address:
            address = self.account.address
        return self.functions.balanceOf(Web3.to_checksum_address(address)).call()

    def total_supply(self) -> int:
        """
        Return the total supply of the token
        """
        return self.functions.totalSupply().call()

    @cached_property
    def name(self) -> str:
        """
        Return the name/label of the token
        """
        return self.functions.name().call()

    @cached_property
    def symbol(self) -> str:
        """
        Return the symbol/ticker of the token
        """
        return self.functions.symbol().call()

    @cached_property
    def decimals(self) -> int:
        """
        Return the number of digits of the token
        """
        return self.functions.decimals().call()

    ####################
    # Write
    ####################

    def transfer(
        self,
        to: str,
        amount: int,
        value_in_wei: int = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Transfer some amount of the token to an address; does not
        require approval.
        """
        return self.transact(
            self.functions.transfer(Web3.to_checksum_address(to), amount),
            value_in_wei,
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )

    def approve(
        self,
        spender: str,
        amount: int,
        value_in_wei: int = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Approve the given address to spend some amount of the token
        on behalf of the sender.
        """
        return self.transact(
            self.functions.approve(Web3.to_checksum_address(spender), amount),
            value_in_wei,
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )

    @staticmethod
    def from_wei(amount: int, decimals: int) -> Decimal:
        """
        Given an amount in wei, return the equivalent amount in
        token units.  Here by wei we mean the smallest subdivision
        of the token (e.g. 1/10**6 for USDC, 1/10**18 for UNI).
        """
        return amount / Decimal(10**decimals)
