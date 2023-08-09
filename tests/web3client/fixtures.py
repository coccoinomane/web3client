from typing import List

import pytest

import ape
from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client


@pytest.fixture()
def base_client(ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri)


@pytest.fixture()
def alice_base_client(accounts_keys: List[str], ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri, private_key=accounts_keys[0])


@pytest.fixture()
def bob_base_client(accounts_keys: List[str], ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri, private_key=accounts_keys[1])


@pytest.fixture()
def erc20_client(
    TST: ape.contracts.ContractInstance, ape_chain_uri: str
) -> Erc20Client:
    return Erc20Client(node_uri=ape_chain_uri, contract_address=TST.address)


@pytest.fixture()
def alice_erc20_client(
    TST: ape.contracts.ContractInstance, accounts_keys: List[str], ape_chain_uri: str
) -> Erc20Client:
    return Erc20Client(
        node_uri=ape_chain_uri,
        contract_address=TST.address,
        private_key=accounts_keys[0],
    )


@pytest.fixture()
def bob_erc20_client(
    TST: ape.contracts.ContractInstance, accounts_keys: List[str], ape_chain_uri: str
) -> Erc20Client:
    return Erc20Client(
        node_uri=ape_chain_uri,
        contract_address=TST.address,
        private_key=accounts_keys[1],
    )
