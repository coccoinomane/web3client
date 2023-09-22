from typing import cast

import pytest

import ape
from web3client.erc20_client import DualClient
from web3client.exceptions import Web3ClientException

#   ___              ___    __
#  | __|  _ _   __  |_  )  /  \
#  | _|  | '_| / _|  / /  | () |
#  |___| |_|   \__| /___|  \__/


@pytest.mark.local
def test_dual_client_token_balance_in_wei(
    TST: ape.contracts.ContractInstance,
    dual_client_token: DualClient,
    alice: ape.api.AccountAPI,
) -> None:
    alice_balance_in_wei = dual_client_token.balance_in_wei(alice.address)
    assert TST.balanceOf(alice) == alice_balance_in_wei


@pytest.mark.local
def test_dual_client_token_transfer(
    TST: ape.contracts.ContractInstance,
    alice_dual_client_token: DualClient,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = TST.balanceOf(bob)
    alice_dual_client_token.transfer(bob.address, 10**18)
    assert TST.balanceOf(bob) == bob_balance + 10**18


def test_dual_client_token_clone(
    alice_dual_client_token: DualClient,
    TST_0: ape.contracts.ContractInstance,
) -> None:
    clone = cast(DualClient, alice_dual_client_token.clone(base=DualClient))
    # The clone's contract must be the same as the original's
    assert clone.contract_address == alice_dual_client_token.contract_address
    assert clone.abi == alice_dual_client_token.abi
    # Setting a property on the clone must not change the original
    old_contract_address = alice_dual_client_token.contract_address
    clone.set_contract(TST_0.address)
    assert alice_dual_client_token.contract_address == old_contract_address
    assert clone.contract_address == TST_0.address


#   _  _          _     _
#  | \| |  __ _  | |_  (_) __ __  ___
#  | .` | / _` | |  _| | | \ V / / -_)
#  |_|\_| \__,_|  \__| |_|  \_/  \___|


@pytest.mark.local
def test_dual_token_native_balance_in_wei(
    dual_client_native: DualClient,
    alice: ape.api.AccountAPI,
) -> None:
    alice_balance_in_wei = dual_client_native.balance_in_wei(alice.address)
    assert alice.balance == alice_balance_in_wei


@pytest.mark.local
def test_dual_token_native_transfer(
    alice_dual_client_native: DualClient,
    bob: ape.api.AccountAPI,
) -> None:
    bob_balance = bob.balance
    alice_dual_client_native.transfer(bob.address, 10**18)
    assert bob.balance == bob_balance + 10**18


def test_dual_token_native_clone(alice_dual_client_native: DualClient) -> None:
    clone = alice_dual_client_native.clone()
    assert clone.node_uri == alice_dual_client_native.node_uri
    assert clone.private_key == alice_dual_client_native.private_key


def test_dual_token_native_exceptions(
    alice_dual_client_native: DualClient,
    bob: ape.api.AccountAPI,
) -> None:
    with pytest.raises(Web3ClientException, match="value_in_wei"):
        alice_dual_client_native.transfer(bob.address, 10**18, value_in_wei=10**18)
    with pytest.raises(Web3ClientException, match="total supply"):
        alice_dual_client_native.total_supply()
    with pytest.raises(Web3ClientException, match="approve"):
        alice_dual_client_native.approve(bob.address, 10**18)
