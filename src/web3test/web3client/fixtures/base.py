from typing import List

import pytest

from web3client.base_client import BaseClient

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
