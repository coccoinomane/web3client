"""
Return the token balance of the given address
"""
from sys import argv
from web3factory.erc20_tokens import get_token_config
from web3factory.factory import make_erc20_client
from web3client.helpers.general import fourthOrNone, secondOrNone, thirdOrNone

address = secondOrNone(argv)
if not address:
    raise Exception("Please give me a user address")

token = thirdOrNone(argv) or "USDC"

network = fourthOrNone(argv) or "ethereum"

client = make_erc20_client(token, network)

balance = client.balanceOf(address)
balance_in_eth = client.fromWei(balance, get_token_config(token, network)["decimals"])

print(f">>> Balance of {address} on {network}")
print(f"{balance_in_eth} {token}")
