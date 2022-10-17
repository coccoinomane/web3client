"""
Define shared state for all tests
"""
import pytest
from web3client.Web3Client import Web3Client


@pytest.fixture()
def node_uri() -> str:
    return "https://goerli.infura.io/v3/db0e363aad2f43ee8a2f259733721512"


@pytest.fixture()
def private_key() -> str:
    return "53caa63985c6089c84be07e3f42d5d7ebd47a8a097835ede937d4c5e1f1021dd"


@pytest.fixture()
def web3client(node_uri: str, private_key: str) -> Web3Client:
    return Web3Client(
        nodeUri=node_uri,
        privateKey=private_key,
    )
