"""
Print the latest block
"""
from sys import argv
from web3factory.factory import make_client
from web3client.helpers.general import secondOrNone
from web3client.helpers.debug import pprintAttributeDict

network = secondOrNone(argv) or "ethereum"

client = make_client(network)

block = client.getLatestBlock()

print(f">>> Latest block")
pprintAttributeDict(block)
