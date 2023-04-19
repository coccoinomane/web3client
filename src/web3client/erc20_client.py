import os
from functools import cached_property

from eth_typing import Address, HexStr
from web3 import Web3
from web3.types import Nonce, Wei

from web3client.base_client import BaseClient


class Erc20Client(BaseClient):
    """
    Client that comes with the ERC20 ABI preloaded.

    It allows you to call the contract functions as class methods:
    transfer, balanceOf, name, etc.

    If you pass  a private key, it will allow you to call the
    write functions (transfer, approve, etc.)

    The token properties (name, symbol, total_supply, decimals) can be
    accessed as attributes, and will be fetched from the blockchain only
    once.

    AMOUNTS
    =======

    Whenever we will refer to an "amount" of the token, we really mean an
    amount in the smallest subdivision of the token (e.g. wei). For example:
    - If the token has 6 decimals (like most stablecoins) an amount of 1
      corresponds to one millionth of the token.
    - For tokens with 18 decimals (like most non-stablecoins) an amount
      of 1 is equal to 1/10^18 of the token (a single wei).
    """

    abiDir = os.path.dirname(os.path.realpath(__file__)) + "/abi"
    abi = BaseClient.get_contract_abi_from_file(abiDir + "/erc20.json")

    def __init__(
        self,
        node_uri: str,
        chain_id: int = None,
        tx_type: int = 2,
        private_key: str = None,
        max_priority_fee_in_gwei: float = 1,
        upper_limit_for_base_fee_in_gwei: float = float("inf"),
        contract_address: Address = None,
    ) -> None:
        if not contract_address:
            raise ValueError("You must specify a contract address")
        super().__init__(
            node_uri,
            chain_id,
            tx_type,
            private_key,
            max_priority_fee_in_gwei,
            upper_limit_for_base_fee_in_gwei,
            contract_address,
            self.abi,
        )

    ####################
    # Read
    ####################

    def balanceOf(self, address: Address) -> int:
        """
        Return the amount held by the given address
        """
        return self.contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()

    @cached_property
    def name(self) -> str:
        """
        Return the name/label of the token
        """
        return self.contract.functions.name().call()

    @cached_property
    def symbol(self) -> str:
        """
        Return the symbol/ticker of the token
        """
        return self.contract.functions.symbol().call()

    @cached_property
    def totalSupply(self) -> int:
        """
        Return the total supply of the token
        """
        return self.contract.functions.totalSupply().call()

    @cached_property
    def decimals(self) -> int:
        """
        Return the number of digits of the token
        """
        return self.contract.functions.decimals().call()

    ####################
    # Write
    ####################

    def transfer(
        self,
        to: Address,
        amount: int,
        value_in_wei: Wei = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Transfer some amount of the token to an address; does not
        require approval.
        """
        return self.transact(
            self.contract.functions.transfer(Web3.to_checksum_address(to), amount),
            value_in_wei,
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )

    def approve(
        self,
        spender: Address,
        amount: int,
        value_in_wei: Wei = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Approve the given address to spend some amount of the token
        on behalf of the sender.
        """
        return self.transact(
            self.contract.functions.approve(Web3.to_checksum_address(spender), amount),
            value_in_wei,
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )

    ####################
    # Static
    ####################

    @staticmethod
    def from_wei(amount: int, decimals: int) -> float:
        """
        Given an amount in Wei, return the equivalent amount in
        ETH units
        """
        return amount / 10**decimals
