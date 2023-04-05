"""
Print the latest block
"""
from sys import argv

from web3client.helpers.debug import pprintAttributeDict
from web3client.helpers.general import secondOrNone
from web3factory.factory import make_client

network = secondOrNone(argv) or "eth"

client = make_client(network)

block = client.get_latest_block()

print(f">>> Latest block")
pprintAttributeDict(block)
