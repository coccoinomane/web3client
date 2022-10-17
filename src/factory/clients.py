"""
Initialize crabada clients so that they can be used
by the scripts
"""

from typing import cast
from eth_typing import Address
from web3client.Erc20Web3Client import Erc20Web3Client
from web3client.Web3Client import Web3Client
from factory.Web3ClientFactory import makeErc20Client, makeWeb3Client


def makeAvalancheClient(nodeUri: str, privateKey: str) -> Web3Client:
    """
    Return a generic client to interact with the Avalanche C Chain
    network
    """
    return makeWeb3Client(
        "Avalanche",
        nodeUri,
        privateKey=privateKey,
    )


def makeSwimmerNetworkClient(nodeUri: str, privateKey: str) -> Web3Client:
    """
    Return a generic client to interact with the Swimmer Network
    Avalanche subnet
    """
    return makeWeb3Client(
        "SwimmerNetwork",
        nodeUri,
        privateKey=privateKey,
    )


def makeAvalancheTusClient(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the TUS
    token contract on the Avalanche C-Chain
    """
    tusContract = cast(Address, "0xf693248F96Fe03422FEa95aC0aFbBBc4a8FdD172")
    return makeErc20Client(
        "Avalanche",
        nodeUri,
        tusContract,
        privateKey=privateKey,
    )


def makeAvalancheCraClient(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the CRA
    token contract on the Avalanche C-Chain
    """
    craContract = cast(Address, "0xa32608e873f9ddef944b24798db69d80bbb4d1ed")
    return makeErc20Client(
        "Avalanche",
        nodeUri,
        craContract,
        privateKey=privateKey,
    )


def makeSwimmerWtusClient(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the WTUS
    token contract on the Swimmer Network Avalanche subnet.

    On Swimmer, WTUS is the wrapped version of TUS. Please note
    that to send 'regular' TUS, you just need to use the sendEth
    method in Web3Client.
    """
    wtusContract = cast(Address, "0x9c765eEE6Eff9CF1337A1846c0D93370785F6C92")
    return makeErc20Client(
        "SwimmerNetwork",
        nodeUri,
        wtusContract,
        privateKey=privateKey,
    )


def makeSwimmerCraClient(nodeUri: str, privateKey: str) -> Erc20Web3Client:
    """
    Return an initialized client to interact with the CRA
    token contract on the Swimmer Network Avalanche subnet
    """
    craContract = cast(Address, "0xC1a1F40D558a3E82C3981189f61EF21e17d6EB48")
    return makeErc20Client(
        "SwimmerNetwork",
        nodeUri,
        craContract,
        privateKey=privateKey,
    )
