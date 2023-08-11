import pytest

from web3client.compound_v2_client import CompoundV2CErc20Client


@pytest.mark.local
def test_compound_v2_ctst_read(compound_v2_ctst_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ctst_client.symbol == "cTST"


@pytest.mark.local
def test_compound_v2_ceth_read(compound_v2_ceth_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ceth_client.symbol == "cETH"


@pytest.mark.local
def test_compound_v2_ctst_supply(
    alice_compound_v2_ctst_client: CompoundV2CErc20Client,
) -> None:
    client = alice_compound_v2_ctst_client
    exchange_rate = client.exchange_rate_stored()
    amount = 10**18
    client.approve_and_supply(amount)
    assert client.total_supply() * exchange_rate == amount * 10**18


@pytest.mark.local
def test_compound_v2_ceth_supply(
    alice_compound_v2_ceth_client: CompoundV2CErc20Client,
) -> None:
    client = alice_compound_v2_ceth_client
    exchange_rate = client.exchange_rate_stored()
    amount = 10**18
    client.supply(amount)
    assert client.total_supply() * exchange_rate == amount * 10**18
