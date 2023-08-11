from typing import List

import pytest

import ape
from web3client.base_client import BaseClient
from web3client.compound_v2_client import (
    CompoundV2CErc20Client,
    CompoundV2CEtherClient,
    CompoundV2ComptrollerClient,
)
from web3client.erc20_client import Erc20Client

# Base client


@pytest.fixture()
def base_client(ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri)


@pytest.fixture()
def alice_base_client(accounts_keys: List[str], ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri, private_key=accounts_keys[0])


@pytest.fixture()
def bob_base_client(accounts_keys: List[str], ape_chain_uri: str) -> BaseClient:
    return BaseClient(node_uri=ape_chain_uri, private_key=accounts_keys[1])


# ERC20 client


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


# CEther client (cETH)


@pytest.fixture()
def compound_v2_ceth_client(
    compound_v2_ceth: ape.contracts.ContractInstance, ape_chain_uri: str
) -> CompoundV2CEtherClient:
    return CompoundV2CEtherClient(
        node_uri=ape_chain_uri, contract_address=compound_v2_ceth.address
    )


@pytest.fixture()
def alice_compound_v2_ceth_client(
    compound_v2_ceth: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2CEtherClient:
    return CompoundV2CEtherClient(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_ceth.address,
        private_key=accounts_keys[0],
    )


@pytest.fixture()
def bob_compound_v2_ceth_client(
    compound_v2_ceth: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2CEtherClient:
    return CompoundV2CEtherClient(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_ceth.address,
        private_key=accounts_keys[1],
    )


# CErc20 client (cTST)


@pytest.fixture()
def compound_v2_ctst_client(
    compound_v2_ctst: ape.contracts.ContractInstance, ape_chain_uri: str
) -> CompoundV2CErc20Client:
    return CompoundV2CErc20Client(
        node_uri=ape_chain_uri, contract_address=compound_v2_ctst.address
    )


@pytest.fixture()
def alice_compound_v2_ctst_client(
    compound_v2_ctst: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2CErc20Client:
    return CompoundV2CErc20Client(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_ctst.address,
        private_key=accounts_keys[0],
    )


@pytest.fixture()
def bob_compound_v2_ctst_client(
    compound_v2_ctst: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2CErc20Client:
    return CompoundV2CErc20Client(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_ctst.address,
        private_key=accounts_keys[1],
    )


# Comptroller client


@pytest.fixture()
def compound_v2_comptroller_client(
    compound_v2_comptroller: ape.contracts.ContractInstance, ape_chain_uri: str
) -> CompoundV2ComptrollerClient:
    return CompoundV2ComptrollerClient(
        node_uri=ape_chain_uri, contract_address=compound_v2_comptroller.address
    )


@pytest.fixture()
def alice_compound_v2_comptroller_client(
    compound_v2_comptroller: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2ComptrollerClient:
    return CompoundV2ComptrollerClient(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_comptroller.address,
        private_key=accounts_keys[0],
    )


@pytest.fixture()
def bob_compound_v2_comptroller_client(
    compound_v2_comptroller: ape.contracts.ContractInstance,
    accounts_keys: List[str],
    ape_chain_uri: str,
) -> CompoundV2ComptrollerClient:
    return CompoundV2ComptrollerClient(
        node_uri=ape_chain_uri,
        contract_address=compound_v2_comptroller.address,
        private_key=accounts_keys[1],
    )
