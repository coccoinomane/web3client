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
