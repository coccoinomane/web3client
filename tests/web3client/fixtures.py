from typing import Dict, List

import pytest

from web3client.base_client import BaseClient
from web3factory.factory import make_client
from web3factory.networks import supported_networks


@pytest.fixture()
def rpcs() -> Dict[str, str]:
    """
    Let's use difrerent RPCs for tests, in case the regular ones
    are throttled
    """
    return {
        "eth": "https://mainnet.infura.io/v3/db0e363aad2f43ee8a2f259733721512",
    }


@pytest.fixture()
def address() -> str:
    return "0x3A8c8833Abe2e8454F59574A2A18b9bA8A28Ea4F"


@pytest.fixture()
def private_key() -> str:
    return "53caa63985c6089c84be07e3f42d5d7ebd47a8a097835ede937d4c5e1f1021dd"


@pytest.fixture()
def networks_clients(rpcs: Dict[str, str]) -> Dict[str, BaseClient]:
    """
    Ready-to-use clients, indexed by network name, no signer
    """
    clients = {}
    for network in supported_networks:
        name = network["name"]
        node_uri = rpcs.get(name)
        clients[name] = make_client(name, node_uri)
    return clients


@pytest.fixture()
def eth_client() -> BaseClient:
    return make_client("eth")


@pytest.fixture()
def bnb_client() -> BaseClient:
    return make_client("bnb")


@pytest.fixture()
def bnb_ws_client() -> BaseClient:
    return make_client("bnb", node_uri="wss://dex.binance.org/api/ws")


@pytest.fixture(scope="session")
def signers() -> List[Dict[str, str]]:
    return [
        {
            "name": "vanity_1",
            "address": "0x0c2010dc4736bab060740D3968cf1dDF86196D81",
            "private_key": "d94e4166f0b3c85ffebed3e0eaa7f7680ae296cf8a7229d637472b7452c8602c",
            "keyfile": '{"address": "0c2010dc4736bab060740d3968cf1ddf86196d81", "crypto": {"cipher": "aes-128-ctr", "cipherparams": {"iv": "44bb6afb52fa1eb4e273f2dc972aa9c9"}, "ciphertext": "ca4bd4f91bfc51a34e5fd72340cfe058ae77108c51fdad8413c1a7c1eb54ea5c", "kdf": "scrypt", "kdfparams": {"dklen": 32, "n": 262144, "r": 1, "p": 8, "salt": "34eb69126e4c28c3b96ff2bbafc30fd6"}, "mac": "e30f84c256b85ad757527a9963da856a3dc0c8ff7691eaa30dce8a6025db0044"}, "id": "5dcac562-ed62-42be-85af-458082ae5621", "version": 3}',
            "keyfile_password": "secret_1",
        },
        {
            "name": "vanity_2",
            "address": "0x206D4d644c22dDFc343b3AD23bBc7A42c8B201fc",
            "private_key": "3bc2f9b05ac28389fd65fd40068a10f730ec66b6293f9cfd8fe804d212ce06bb",
            "keyfile": '{"address": "206d4d644c22ddfc343b3ad23bbc7a42c8b201fc", "crypto": {"cipher": "aes-128-ctr", "cipherparams": {"iv": "8eb93057b97baef092028a49d729fadb"}, "ciphertext": "5bcb8cc45abc29098e6157953218f90ce992c410fefa5cd6ccba5f90301abbfc", "kdf": "scrypt", "kdfparams": {"dklen": 32, "n": 262144, "r": 1, "p": 8, "salt": "9a9bae4fbef319b359dbc1a19757898c"}, "mac": "a890fbe5e0472cecff264b50ed7be3d56c22082a45e836712604a117ccc2ea24"}, "id": "c77dd2d2-d657-4d4a-ab7c-b491c4be0eb9", "version": 3}',
            "keyfile_password": "secret_2",
        },
        {
            "name": "vanity_3",
            "address": "0x9fF0c40eDe4585a5E9f0F00009ce79b6344cB663",
            "private_key": "f76c67c2dd62222a5ec747116a66c573f3795c53276c0cdeafbcb5f597e2f8d4",
            "keyfile": '{"address": "9ff0c40ede4585a5e9f0f00009ce79b6344cb663", "crypto": {"cipher": "aes-128-ctr", "cipherparams": {"iv": "efddd96d2ce2f840af8b58d681d1330c"}, "ciphertext": "95d4fc9dde914a8cdb679fda7b0ead7312fcc3053bfeb82bd5f6ffa5db22da4b", "kdf": "scrypt", "kdfparams": {"dklen": 32, "n": 262144, "r": 1, "p": 8, "salt": "1dc311b9bd5c76ed686ef39003716294"}, "mac": "63cdddd9e8f3987dff63a88ef838cc24ecfeb7b568916f581deb061844850f5e"}, "id": "c78bb6ff-fb12-474a-bf84-5a6d6e8e8bcc", "version": 3}',
            "keyfile_password": "secret_3",
        },
    ]
