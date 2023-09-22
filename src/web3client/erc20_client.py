from decimal import Decimal
from functools import cached_property
from typing import Any

from eth_typing import HexStr
from typing_extensions import Self
from web3 import Web3
from web3.types import Nonce

from web3client.base_client import BaseClient
from web3client.exceptions import Web3ClientException


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


class DualClient(Erc20Client):
    """A client that works with either ERC20 tokens or native
    coins such as ETH, BNB, etc.

    Set the contract address to an ERC20 token, and the client will
    behave exactly like an Erc20Client.

    Set the contract address to "native" and you will be able to use
    the same method of the Erc20Client, but the "token" will be the
    blockchain native coin.
    """

    def set_contract(self, contract_address: str, abi: dict[str, Any] = None) -> Self:
        if contract_address == "native":
            self.contract_address = "native"
            return self
        return super().set_contract(contract_address, abi)

    ####################
    # Read
    ####################

    def is_native(self) -> bool:
        return self.contract_address == "native"

    def is_erc20(self) -> bool:
        return bool(self.contract_address) and self.contract_address != "native"

    def balance(self, address: str = None) -> Decimal:
        if self.is_native():
            return Decimal(self.get_balance_in_eth(address))
        return super().balance(address)

    def balance_in_wei(self, address: str = None) -> int:
        if self.is_native():
            return self.get_balance_in_wei(address)
        return super().balance_in_wei(address)

    def total_supply(self) -> int:
        if self.is_native():
            raise Web3ClientException(f"Cannot get total supply of native coin")
        return super().total_supply()

    @cached_property
    def name(self) -> str:
        if self.is_native():
            return "Native coin"
        return super().name

    @cached_property
    def symbol(self) -> str:
        if self.is_native():
            return "Native coin"
        return super().symbol

    @cached_property
    def decimals(self) -> int:
        if self.is_native():
            return 18
        return super().decimals

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
        if self.is_native():
            if value_in_wei:
                raise Web3ClientException(
                    "Cannot specify 'value_in_wei' when transferring native coins, use 'amount' instead"
                )
            return self.send_eth_in_wei(
                to=to,
                value_in_wei=amount,
                nonce=nonce,
                gas_limit=gas_limit,
                max_priority_fee_in_gwei=max_priority_fee_in_gwei,
            )
        return super().transfer(
            to, amount, value_in_wei, nonce, gas_limit, max_priority_fee_in_gwei
        )

    def approve(
        self,
        spender: str,
        amount: int,
        value_in_wei: int = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
        strict: bool = True,
    ) -> HexStr:
        """
        Approve the given address to spend some amount of the token
        on behalf of the sender.

        For native coins, if strict is True, it will raise an exception
        when you try to approve native coins.  Otherwise, nothing will happen
        and the function will return None.
        """
        if self.is_native():
            if strict:
                raise Web3ClientException("Cannot approve native coins")
            else:
                return None
        return self.transact(
            self.functions.approve(Web3.to_checksum_address(spender), amount),
            value_in_wei,
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )
