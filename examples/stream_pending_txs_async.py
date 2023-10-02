"""
Print pending transactions obtained real-time from a websocket connection,
using eth_subscribe
"""
import asyncio

from web3.types import TxData

from web3factory.factory import make_client
from web3factory.networks import supported_networks

network_names = ",".join([n["name"] for n in supported_networks])
network = input(f"Network ({network_names}): ") or None
ws_rpc = input("WS RPC: ") or None

client = make_client(network, node_uri=ws_rpc)


async def callback(tx: str, subscription_type: str, tx_data: TxData) -> None:
    print(f"Pending tx: {tx}")
    # Process transaction as you see fit...
    await asyncio.sleep(3)
    print(f" > Finished processing tx {tx}")


asyncio.run(client.async_subscribe(callback, once=False))
