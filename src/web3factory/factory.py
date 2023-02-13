from typing import Any, Type, cast

from eth_typing import Address

from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client
from web3factory.erc20_tokens import get_token_config
from web3factory.networks import get_network_config, pick_first_rpc
from web3factory.types import NetworkName, TokenName


def make_client(
    networkName: NetworkName,
    node_uri: str = None,
    base: Type[BaseClient] = BaseClient,
    **clientArgs: Any,
) -> BaseClient:
    """
    Return a brand new client configured for the given blockchain
    """
    networkConfig = get_network_config(networkName)
    if node_uri is None:
        node_uri = pick_first_rpc(networkName)
    client = base(node_uri=node_uri, **clientArgs)
    client.chain_id = networkConfig["chain_id"]
    client.tx_type = networkConfig["tx_type"]
    client.set_middlewares(networkConfig.get("middlewares", []))

    return client


def make_erc20_client(
    tokenName: TokenName,
    networkName: NetworkName,
    node_uri: str = None,
    **clientArgs: Any,
) -> Erc20Client:
    """
    Return a brand new client configured for the given blockchain
    and preloaded with the ERC20 token ABI
    """
    token_address = get_token_config(tokenName, networkName)["address"]
    client = make_client(
        networkName, node_uri, Erc20Client, contract_address=token_address, **clientArgs
    )
    return cast(Erc20Client, client)
