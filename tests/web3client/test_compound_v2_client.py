import pytest

from web3client.compound_v2_client import CompoundV2CErc20Client


@pytest.mark.local
def test_compound_v2_ctst_read(compound_v2_ctst_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ctst_client.symbol == "cTST"


@pytest.mark.local
def test_compound_v2_ceth_read(compound_v2_ceth_client: CompoundV2CErc20Client) -> None:
    assert compound_v2_ceth_client.symbol == "cETH"
