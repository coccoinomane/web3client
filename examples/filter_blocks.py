"""
Print new blocks obtained with a polling mechanism, using eth_newBlockFilter
"""
from time import sleep

from web3factory.factory import make_client
from web3factory.networks import supported_networks

network_names = ",".join([n["name"] for n in supported_networks])
network = input(f"Network ({network_names}): ") or None
ws_rpc = input("Optionally specify RPC: ") or None

client = make_client(network, node_uri=ws_rpc)

filter = client.w3.eth.filter("latest")

while True:
    for block in filter.get_new_entries():
        print(f"New block: {block}")
    sleep(1)
