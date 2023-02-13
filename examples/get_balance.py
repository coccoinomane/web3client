"""
Return the balance in ETH (or AVAX, BNB, etc, depending on
the network) of the given address
"""
from sys import argv

from web3client.helpers.general import secondOrNone, thirdOrNone
from web3factory.factory import make_client
from web3factory.networks import get_network_config

address = secondOrNone(argv)
if not address:
    raise Exception("Please give me a user address")

network = thirdOrNone(argv) or "ethereum"

client = make_client(network)

balance_in_eth = client.get_balance_in_eth(address)

print(f">>> Balance of {address} on {network}")
print(f"{balance_in_eth} {get_network_config(network)['coin']}")
