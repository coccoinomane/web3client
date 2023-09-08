from typing import List, TypedDict

from web3client.base_client import BaseClient
from web3client.exceptions import OrbiterClientException


class OrbiterClient(BaseClient):
    """
    Client that can be used to bridge funds with the Orbiter bridge
    (https://www.orbiter.finance/).

    The Orbiter bridge is a cross-rollup bridge.  It allows to move
    funds from Ethereum to a rollup (e.g. Arbitrum) and back.  It also
    allows to move funds from one rollup to another.

    To bridge, one has to send funds to an addresses operated by Orbiter.
    There is one such address per token.  Orbiter will then send the funds
    to your address on the destination chain.  You can specify the
    destination chain by using a special code in the last 4 digits of
    the amount.

    IMPORTANT:
     - Before sending any funds to Orbiter, make sure that you respect
       the limits per each chain. You can find the limits in the
       Orbiter docs at https://docs.orbiter.finance/
     - Orbiter charges both a fixed fee (called witholding fee) and a
       percentage fee.  The fixed fee depends on gas cost. For example,
       to move USDC from Optimism to Era, the percentage fee is 0.3%
       and the fixed fee (for normal gas fee) is 1.8 USDC.  These fees
       are deducted from the amount you send to Orbiter. So make sure
       to always send a bit more than the amount you want to bridge.
     - The list of maker (i.e. deposit) addresses is not dynamic. It
       can be found on Orbiter's Github:
       https://github.com/Orbiter-Finance/orbiter-sdk/blob/main/src/bridge/maker_list.mainnet.ts
       Here, we use the local copy in the abi folder.
    """

    class MakerConfig(TypedDict):
        """Config for an Orbiter maker (i.e. deposit address)"""

        makerAddress: str
        c1ID: int
        c2ID: int
        c1Name: str
        c2Name: str
        t1Address: str
        t2Address: str
        tName: str
        c1MinPrice: float
        c1MaxPrice: float
        c2MinPrice: float
        c2MaxPrice: float
        precision: int
        c1TradingFee: float
        c2TradingFee: float
        c1GasFee: float
        c2GasFee: float

    class OrbiterChain(TypedDict):
        """A chains supported by web3client for bridging with Orbiter."""

        name: str
        network_id: int
        """Network IDs will be taken from the Orbiter docs.
        Screenshot: https://d.pr/i/KYKLcp"""

        rpc: str
        """The RPC specified here will be used to check whether Orbiter
        has enough liquidity on the receiving chain"""

    orbiter_supported_chains: List[OrbiterChain] = [
        {
            "name": "mainnet",
            "network_id": 9001,
            "rpc": "https://cloudflare-eth.com",
        },
        {
            "name": "arbitrum",
            "network_id": 9002,
            "rpc": "https://arb1.arbitrum.io/rpc",
        },
        {
            "name": "zksync",
            "network_id": 9014,
            "rpc": "https://mainnet.era.zksync.io",
        },
        {
            "name": "optimism",
            "network_id": 9007,
            "rpc": "https://mainnet.optimism.io",
        },
    ]

    maker_list: List[MakerConfig]
    """The list of Orbiter makers (i.e. deposit addresses) to use for bridging.
    Loaded from  abi/orbiter_maker_list.json"""

    def init(self) -> None:
        super().init()
        self.maker_list = self.get_maker_list()

    def get_maker_list(self) -> List[MakerConfig]:
        """Return a dict with the maker list"""
        return self.get_abi_json("orbiter_maker_list.json")

    def validate_chains(self, from_chain: str, to_chain: str) -> None:
        """Validate that the given chains are supported by Orbiter"""
        from_chain = from_chain.lower()
        to_chain = to_chain.lower()
        chain_names = [c["name"].lower() for c in self.orbiter_supported_chains]
        if from_chain not in chain_names:
            raise OrbiterClientException(
                f"Chain '{from_chain}' not supported by web3client"
            )
        if to_chain not in chain_names:
            raise OrbiterClientException(
                f"Chain '{to_chain}' not supported by web3client"
            )

    def find_makers(
        self,
        from_chain: str,
        to_chain: str,
        token_address: str,
        amount: float,
    ) -> List[MakerConfig]:
        """Find the makers (i.e. deposit addresses) that can be used to bridge the
        given amount of the given token.  For native tokens (e.g. ETH on ethereum or
        arbitrum) the token_address should be 0x0000000000000000000000000000000000000000.
        """
        self.validate_chains(from_chain, to_chain)
        # Find all makers that support the given token and chains
        makers = [
            m
            for m in self.maker_list
            if m["tName"] == token_address
            and m["c1Name"] == from_chain
            and m["c2Name"] == to_chain
        ]
