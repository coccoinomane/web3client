from typing import List

import pytest

import ape
from web3client.compound_v2_client import (
    CompoundV2CErc20Client,
    CompoundV2CEtherClient,
    CompoundV2ComptrollerClient,
)


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
