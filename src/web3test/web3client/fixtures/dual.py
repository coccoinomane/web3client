from typing import List

import pytest

import ape
from web3client.erc20_client import DualClient


@pytest.fixture()
def dual_client_token(
    TST: ape.contracts.ContractInstance, ape_chain_uri: str
) -> DualClient:
    return DualClient(node_uri=ape_chain_uri, contract_address=TST.address)


@pytest.fixture()
def dual_client_native(ape_chain_uri: str) -> DualClient:
    return DualClient(node_uri=ape_chain_uri, contract_address="native")


@pytest.fixture()
def alice_dual_client_token(
    TST: ape.contracts.ContractInstance, accounts_keys: List[str], ape_chain_uri: str
) -> DualClient:
    return DualClient(
        node_uri=ape_chain_uri,
        contract_address=TST.address,
        private_key=accounts_keys[0],
    )


@pytest.fixture()
def alice_dual_client_native(
    accounts_keys: List[str], ape_chain_uri: str
) -> DualClient:
    return DualClient(
        node_uri=ape_chain_uri,
        contract_address="native",
        private_key=accounts_keys[0],
    )
