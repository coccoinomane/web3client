from web3client.base_client import BaseClient
from web3client.erc20_client import Erc20Client


class CompoundV2CEtherClient(Erc20Client):
    """
    Client that comes with the contract of a Compound V2 pool
    of type ETH preloaded (https://docs.compound.finance/v2/).
    """

    abi = BaseClient.get_abi_json("compound_v2_ceth.json")

    ####################
    # Read
    ####################

    ####################
    # Write
    ####################


class CompoundV2CErc20Client(CompoundV2CEtherClient):
    """
    Client that comes with the contract of a Compound V2 pool
    of type ETH preloaded (https://docs.compound.finance/v2/).
    """

    abi = BaseClient.get_abi_json("compound_v2_cerc20.json")

    ####################
    # Read
    ####################

    ####################
    # Write
    ####################
