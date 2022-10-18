"""
Initialize popular clients so that they can be used
by the scripts

TODO: do we really need this? Why not just use the
string selector in make_client()?
"""

from typing import cast
from eth_typing import Address
from web3client.Erc20Web3Client import Erc20Web3Client
from web3client.Web3Client import Web3Client
from web3factory.factory import make_erc20_client, make_client


def make_avalanche_client(nodeUri: str, privateKey: str) -> Web3Client:
    """
    Return a generic client to interact with the Avalanche C Chain
    network
    """
    return make_client(
        "Avalanche",
        nodeUri,
        privateKey=privateKey,
    )


def make_swimmer_network_client(nodeUri: str, privateKey: str) -> Web3Client:
    """
    Return a generic client to interact with the Swimmer Network
    Avalanche subnet
    """
    return make_client(
        "Swimmer Network",
        nodeUri,
        privateKey=privateKey,
    )


def make_avalanche_tus_client(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the TUS
    token contract on the Avalanche C-Chain
    """
    tusContract = cast(Address, "0xf693248F96Fe03422FEa95aC0aFbBBc4a8FdD172")
    return make_erc20_client(
        "Avalanche",
        nodeUri,
        tusContract,
        privateKey=privateKey,
    )


def make_avalanche_cra_client(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the CRA
    token contract on the Avalanche C-Chain
    """
    craContract = cast(Address, "0xa32608e873f9ddef944b24798db69d80bbb4d1ed")
    return make_erc20_client(
        "Avalanche",
        nodeUri,
        craContract,
        privateKey=privateKey,
    )


def make_swimmer_wtus_client(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the WTUS
    token contract on the Swimmer Network Avalanche subnet.

    On Swimmer, WTUS is the wrapped version of TUS. Please note
    that to send 'regular' TUS, you just need to use the sendEth
    method in Web3Client.
    """
    wtusContract = cast(Address, "0x9c765eEE6Eff9CF1337A1846c0D93370785F6C92")
    return make_erc20_client(
        "Swimmer Network",
        nodeUri,
        wtusContract,
        privateKey=privateKey,
    )


def make_swimmer_cra_client(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the CRA
    token contract on the Swimmer Network Avalanche subnet
    """
    craContract = cast(Address, "0xC1a1F40D558a3E82C3981189f61EF21e17d6EB48")
    return make_erc20_client(
        "Swimmer Network",
        nodeUri,
        craContract,
        privateKey=privateKey,
    )
