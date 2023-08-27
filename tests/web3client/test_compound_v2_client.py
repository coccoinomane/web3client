import pytest

import ape
from web3client.compound_v2_client import (
    CompoundV2CErc20Client,
    CompoundV2CEtherClient,
    CompoundV2ComptrollerClient,
)


@pytest.mark.local
def test_compound_v2_ctst_read(compound_v2_ctst_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ctst_client.symbol == "cTST"


@pytest.mark.local
def test_compound_v2_ceth_read(compound_v2_ceth_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ceth_client.symbol == "cETH"


@pytest.mark.local
def test_compound_v2_ctst_underlying_balance(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
    alice: ape.api.AccountAPI,
    TST: ape.contracts.ContractInstance,
) -> None:
    client = alice_compound_v2_ctst_client
    assert TST.balanceOf(alice) == client.underlying_balance()


@pytest.mark.local
def test_compound_v2_ceth_underlying_balance(
    alice_compound_v2_ceth_client: CompoundV2CErc20Client,
    alice: ape.api.AccountAPI,
) -> None:
    client = alice_compound_v2_ceth_client
    assert alice.balance == client.underlying_balance()


@pytest.mark.local
def test_compound_v2_ctst_supply(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
) -> None:
    client = alice_compound_v2_ctst_client
    alice_balance = client.get_underlying_client().balance_in_wei()
    amount = 3 * 10**18
    client.approve_and_supply(amount)
    assert client.supplied() == amount
    assert client.get_underlying_client().balance_in_wei() == alice_balance - amount
    assert client.total_supply() * client.exchange_rate() == amount * 10**18
    assert client.liquidity() == amount
    assert client.solvency() == float("inf")


@pytest.mark.local
def test_compound_v2_ceth_supply(
    alice_compound_v2_ceth_client: CompoundV2CEtherClient,
) -> None:
    client = alice_compound_v2_ceth_client
    exchange_rate = client.exchange_rate()
    amount = 10**18
    client.supply(amount)
    assert client.supplied() == amount
    assert client.total_supply() * exchange_rate == amount * 10**18
    assert client.liquidity() == amount
    assert client.solvency() == float("inf")


@pytest.mark.local
def test_compound_v2_ctst_borrow(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
    alice_compound_v2_comptroller_client: CompoundV2ComptrollerClient,
) -> None:
    client = alice_compound_v2_ctst_client
    alice_balance = client.get_underlying_client().balance_in_wei()
    # Supply
    supply_amount = 3 * 10**18
    client.approve_and_supply(supply_amount)
    # Enable collateral
    alice_compound_v2_comptroller_client.enter_market(client.contract_address)
    # Borrow
    borrow_amount = supply_amount // 3
    client.borrow(borrow_amount)
    # Check balance
    assert client.borrowed() == borrow_amount
    assert client.total_borrowed() == borrow_amount
    assert client.liquidity() == supply_amount - borrow_amount
    assert (
        client.get_underlying_client().balance_in_wei()
        == alice_balance + borrow_amount - supply_amount
    )


@pytest.mark.local
def test_compound_v2_ceth_borrow(
    alice_compound_v2_ceth_client: CompoundV2CEtherClient,
    alice_compound_v2_comptroller_client: CompoundV2ComptrollerClient,
) -> None:
    client = alice_compound_v2_ceth_client
    alice_balance = client.get_balance_in_wei()
    # Supply
    supply_amount = 3 * 10**18
    tx1 = client.supply(supply_amount)
    rcpt1 = client.get_tx_receipt(tx1)
    # Enable collateral
    tx2 = alice_compound_v2_comptroller_client.enter_market(client.contract_address)
    rcpt2 = client.get_tx_receipt(tx2)
    # Borrow
    borrow_amount = supply_amount // 3
    tx3 = client.borrow(borrow_amount)
    rcpt3 = client.get_tx_receipt(tx3)
    # Check balance
    assert client.borrowed() == borrow_amount
    assert client.total_borrowed() == borrow_amount
    assert client.liquidity() == supply_amount - borrow_amount
    assert (
        client.get_balance_in_wei()
        == alice_balance
        + borrow_amount
        - supply_amount
        - rcpt1["gasUsed"] * rcpt1["effectiveGasPrice"]
        - rcpt2["gasUsed"] * rcpt2["effectiveGasPrice"]
        - rcpt3["gasUsed"] * rcpt3["effectiveGasPrice"]
    )


@pytest.mark.local
def test_compound_v2_ctst_withdraw(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
) -> None:
    client = alice_compound_v2_ctst_client
    alice_balance = client.get_underlying_client().balance_in_wei()
    # Supply
    supply_amount = 3 * 10**18
    client.approve_and_supply(supply_amount)
    # Withdraw half
    withdraw_amount = supply_amount // 2
    client.withdraw(withdraw_amount)
    # Check balance
    assert (
        client.get_underlying_client().balance_in_wei()
        == alice_balance + withdraw_amount - supply_amount
    )
    # Witdhraw the rest
    client.withdraw_all()
    assert client.get_underlying_client().balance_in_wei() == alice_balance
    assert client.liquidity() == 0
    assert client.solvency() == 0


@pytest.mark.local
def test_compound_v2_ceth_withdraw(
    alice_compound_v2_ceth_client: CompoundV2CErc20Client,
) -> None:
    client = alice_compound_v2_ceth_client
    alice_balance = client.get_balance_in_wei()
    # Supply
    supply_amount = 3 * 10**18
    tx1 = client.supply(supply_amount)
    rcpt1 = client.get_tx_receipt(tx1)
    # Withdraw half
    withdraw_amount = supply_amount // 2
    tx2 = client.withdraw(withdraw_amount)
    rcpt2 = client.get_tx_receipt(tx2)
    # Check balance
    assert (
        client.get_balance_in_wei()
        == alice_balance
        + withdraw_amount
        - supply_amount
        - rcpt1["gasUsed"] * rcpt1["effectiveGasPrice"]
        - rcpt2["gasUsed"] * rcpt2["effectiveGasPrice"]
    )
    # Witdhraw the rest
    tx3 = client.withdraw_all()
    rcpt3 = client.get_tx_receipt(tx3)
    assert (
        client.get_balance_in_wei()
        == alice_balance
        - rcpt1["gasUsed"] * rcpt1["effectiveGasPrice"]
        - rcpt2["gasUsed"] * rcpt2["effectiveGasPrice"]
        - rcpt3["gasUsed"] * rcpt3["effectiveGasPrice"]
    )
    assert client.liquidity() == 0
    assert client.solvency() == 0


@pytest.mark.local
def test_compound_v2_ctst_repay(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
    alice_compound_v2_comptroller_client: CompoundV2ComptrollerClient,
) -> None:
    client = alice_compound_v2_ctst_client
    # Supply
    supply_amount = 3 * 10**18
    client.approve_and_supply(supply_amount)
    # Borrow
    alice_compound_v2_comptroller_client.enter_market(client.contract_address)
    borrow_amount = supply_amount // 3
    client.borrow(borrow_amount)
    # Repay a small amount
    repay_amount = borrow_amount // 10
    client.approve_and_repay(repay_amount)
    # Make sure that the amount borrowed has decreased
    # The comparison is approximate because of the interest
    tolerance = 1e-4
    assert abs(borrow_amount - client.borrowed()) / repay_amount - 1 < tolerance
    assert client.liquidity() == supply_amount - borrow_amount + repay_amount
    assert (
        abs(client.solvency() - client.liquidity() / client.total_borrowed())
        < tolerance
    )
    # Repay the remaining amount
    client.approve_and_repay_all()
    assert (
        client.borrowed() == 0
    )  # repay-all reduces borrowed amount to zero for ec20 tokens
    assert (
        abs(client.liquidity() - supply_amount)
        < tolerance * 10 ** client.get_underlying_client().decimals
    )


@pytest.mark.local
def test_compound_v2_ceth_repay(
    alice_compound_v2_ceth_client: CompoundV2CErc20Client,
    alice_compound_v2_comptroller_client: CompoundV2ComptrollerClient,
) -> None:
    client = alice_compound_v2_ceth_client
    # Supply
    supply_amount = 3 * 10**18
    client.supply(supply_amount)
    # Borrow
    alice_compound_v2_comptroller_client.enter_market(client.contract_address)
    borrow_amount = supply_amount // 3
    client.borrow(borrow_amount)
    # Repay a small amount
    repay_amount = borrow_amount // 10
    client.repay(repay_amount)
    # Make sure that the amount borrowed has decreased
    # The comparison is approximate because of the interest
    tolerance = 1e-4
    assert abs(borrow_amount - client.borrowed()) / repay_amount - 1 < tolerance
    assert client.liquidity() == supply_amount - borrow_amount + repay_amount
    assert (
        abs(client.solvency() - client.liquidity() / client.total_borrowed())
        < tolerance
    )
    # Repay the remaining amount
    client.repay_all()
    assert (
        client.borrowed() < tolerance * borrow_amount
    )  # repay-all always leaves some dust in borrowed amount for ETH
    assert abs(client.liquidity() - supply_amount) < tolerance * 10**18
