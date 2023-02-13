"""
Print the number of transactions sent by the given address
"""
from sys import argv

from web3client.helpers.general import secondOrNone
from web3factory.factory import make_client

network = secondOrNone(argv) or "ethereum"

client = make_client(network)

address = input("Ethereum address? ")

if len(address.replace("0x", "")) != 40:
    raise Exception("Please provide a valid Ethereum address")

nonce = client.get_nonce(address)

print(f">>> Transactions sent by {address}")
print(nonce)
