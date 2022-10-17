from typing import Any, Type, cast
from eth_typing import Address
from web3client.Erc20Web3Client import Erc20Web3Client
from web3client.Web3Client import Web3Client
from factory.networks import getNetworkConfig


def makeWeb3Client(
    networkName: str,
    nodeUri: str,
    base: Type[Web3Client] = Web3Client,
    **clientArgs: Any
) -> Web3Client:
    """
    Return a brand new client configured for the given blockchain
    """
    networkConfig = getNetworkConfig(networkName)
    client = base(nodeUri=nodeUri, **clientArgs)
    client.chainId = networkConfig["chainId"]
    client.txType = networkConfig["txType"]
    client.setMiddlewares(networkConfig["middlewares"])

    return client


def makeErc20Client(
    networkName: str, nodeUri: str, tokenAddress: Address, **clientArgs: Any
) -> Erc20Web3Client:
    """
    Return a brand new client configured for the given blockchain
    and preloaded with the ERC20 token ABI
    """
    client = makeWeb3Client(
        networkName,
        nodeUri,
        Erc20Web3Client,
        contractAddress=tokenAddress,
        **clientArgs
    )
    return cast(Erc20Web3Client, client)
