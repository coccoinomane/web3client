from typing import cast

import pytest

import ape
from web3client.erc20_client import Erc20Client


@pytest.mark.local
def test_erc20_client_balance_in_wei(
    TST: ape.contracts.ContractInstance,
    erc20_client: Erc20Client,
    alice: ape.api.AccountAPI,
) -> None:
    alice_balance_in_wei = erc20_client.balance_in_wei(alice.address)
    assert TST.balanceOf(alice) == alice_balance_in_wei


@pytest.mark.local
def test_erc20_client_transfer(
    TST: ape.contracts.ContractInstance,
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = TST.balanceOf(bob)
    alice_erc20_client.transfer(bob.address, 10**18)
    assert TST.balanceOf(bob) == bob_balance + 10**18


@pytest.mark.local
def test_erc20_client_transfer_non_checksum_address(
    TST: ape.contracts.ContractInstance,
    alice_erc20_client: Erc20Client,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = TST.balanceOf(bob)
    alice_erc20_client.transfer(str(bob.address).lower(), 10**18)
    assert TST.balanceOf(bob) == bob_balance + 10**18


def test_erc20_client_clone(
    alice_erc20_client: Erc20Client,
    TST_0: ape.contracts.ContractInstance,
) -> None:
    clone = cast(Erc20Client, alice_erc20_client.clone(base=Erc20Client))
    # The clone's contract must be the same as the original's
    assert clone.contract_address == alice_erc20_client.contract_address
    assert clone.abi == alice_erc20_client.abi
    # Setting a property on the clone must not change the original
    old_contract_address = alice_erc20_client.contract_address
    clone.set_contract(TST_0.address)
    assert alice_erc20_client.contract_address == old_contract_address
    assert clone.contract_address == TST_0.address
