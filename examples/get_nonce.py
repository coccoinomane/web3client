"""
Return the number of transactions sent by the given address
"""

from web3client.Web3Client import Web3Client

node_uri = "https://eth-mainnet.gateway.pokt.network/v1/5f3453978e354ab992c4da79"
address = input("Ethereum address? ")

if len(address.replace("0x", "")) != 40:
    raise Exception("Please provide a valid Ethereum address")

client = Web3Client(nodeUri=node_uri)
nonce = client.getNonce(address)

print(f">>> Transactions sent by {address}")
print(nonce)
