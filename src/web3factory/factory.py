from typing import Any, Type, cast

from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client
from web3factory.erc20_tokens import get_token_config
from web3factory.networks import get_network_config, pick_first_rpc
from web3factory.types import NetworkName, TokenName


def make_client(
    network_name: NetworkName,
    node_uri: str = None,
    base: Type[BaseClient] = BaseClient,
    **clientArgs: Any,
) -> BaseClient:
    """
    Return a brand new client configured for the given blockchain
    """
    networkConfig = get_network_config(network_name)
    if node_uri is None:
        node_uri = pick_first_rpc(network_name)
    client = base(node_uri=node_uri, **clientArgs)
    client.chain_id = networkConfig["chain_id"]
    client.tx_type = networkConfig["tx_type"]
    client.set_middlewares(networkConfig.get("middlewares", []))
    return client


def make_erc20_client(
    networkName: NetworkName,
    node_uri: str = None,
    token_address: str = None,
    token_name: TokenName = None,
    **clientArgs: Any,
) -> Erc20Client:
    """
    Return a brand new client configured for the given blockchain
    and preloaded with the ERC20 token ABI.

    You can specify the token address or the token name. In the latter case,
    the address will be fetched from the token list in erc20_tokens.py.
    """
    if token_address is None and token_name is None:
        raise ValueError("You must specify either token_address or token_name")
    if token_address is None:
        token_address = get_token_config(token_name, networkName)["address"]
    client = make_client(
        networkName, node_uri, Erc20Client, contract_address=token_address, **clientArgs
    )
    return cast(Erc20Client, client)
