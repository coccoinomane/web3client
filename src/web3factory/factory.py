from typing import Any, Type, cast
from eth_typing import Address
from web3client.erc20_client import Erc20Client
from web3client.base_client import BaseClient
from web3factory.networks import get_network_config, pick_rpc


def make_client(
    networkName: str,
    nodeUri: str = None,
    base: Type[BaseClient] = BaseClient,
    **clientArgs: Any
) -> BaseClient:
    """
    Return a brand new client configured for the given blockchain
    """
    networkConfig = get_network_config(networkName)
    if nodeUri is None:
        nodeUri = pick_rpc(networkName)
    client = base(nodeUri=nodeUri, **clientArgs)
    client.chainId = networkConfig["chainId"]
    client.txType = networkConfig["txType"]
    client.setMiddlewares(networkConfig.get("middlewares", []))

    return client


def make_erc20_client(
    networkName: str, nodeUri: str, tokenAddress: Address, **clientArgs: Any
) -> Erc20Client:
    """
    Return a brand new client configured for the given blockchain
    and preloaded with the ERC20 token ABI
    """
    client = make_client(
        networkName, nodeUri, Erc20Client, contractAddress=tokenAddress, **clientArgs
    )
    return cast(Erc20Client, client)
