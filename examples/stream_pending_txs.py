"""
Print the latest block
"""
from web3factory.factory import make_client
from web3factory.networks import supported_networks

network_names = ",".join([n["name"] for n in supported_networks])
network = input(f"Network ({network_names}): ") or None
ws_rpc = input("WS RPC: ") or None

client = make_client(network, node_uri=ws_rpc)

client.subscribe_pending_txs(lambda tx: print(f"Pending tx: {tx}"), once=False)
