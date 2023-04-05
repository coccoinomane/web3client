import os

from eth_typing import Address, HexStr
from web3 import Web3
from web3.types import Nonce, TxParams, Wei

from web3client.base_client import BaseClient


class Erc20Client(BaseClient):
    """
    Client that comes with the ERC20 ABI preloaded.

    Call the contract functions directly: transfer, balanceOf, name,
    etc.

    AMOUNTS
    =======

    Whenever we will refer to an "amount" of the token, we really mean an
    "amount in token units". A token unit is the smallest subdivision of
    the token. For example:
    - If the token has 6 digits (like most stablecoins) an amount of 1
      corresponds to one millionth of the token.
    - For tokens with 18 digits (like most non-stablecoins) an amount
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

    def name(self) -> str:
        """
        Return the name/label of the token
        """
        return self.contract.functions.name().call()

    def symbol(self) -> str:
        """
        Return the symbol/ticker of the token
        """
        return self.contract.functions.symbol().call()

    def totalSupply(self) -> int:
        """
        Return the total supply of the token
        """
        return self.contract.functions.totalSupply().call()

    def decimals(self) -> int:
        """
        Return the number of digits of the token
        """
        return self.contract.functions.decimals().call()

    ####################
    # Write
    ####################

    def transfer(
        self, to: Address, amount: int, nonce: Nonce = None, value_in_wei: Wei = Wei(0)
    ) -> HexStr:
        """
        Transfer some amount of the token to an address; does not
        require approval.
        """

        tx: TxParams = self.build_contract_tx(
            self.contract.functions.transfer(Web3.to_checksum_address(to), amount)
        )

        if nonce:
            tx["nonce"] = nonce

        if value_in_wei:
            tx["value"] = value_in_wei

        return self.sign_and_send_tx(tx)

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
