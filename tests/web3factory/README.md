Factory sub-module of `web3client`.

# Examples

Get the latest block on supported blockchains:

```python
from web3factory.factory import make_client

eth_block = make_client("eth").get_latest_block() # Ethereum
bnb_block = make_client("bnb").get_latest_block() # BNB chain
avax_block = make_client("avax").get_latest_block() # Avalanche
arb_block = make_client("arb").get_latest_block() # Arbitrum
era_block = make_client("era").get_latest_block() # zkSync Era
```

Get the ETH and USDC balances of the Ethereum foundation:

```python
from web3factory.factory import make_client, make_erc20_client

address = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"
eth = make_client("eth").get_balance_in_eth(address)
usdc = make_erc20_client("USDC", "eth").balanceOf(address) / 10**6
```

Get the BNB and BUSD balances of Binance's hot wallet:

```python
from web3factory.factory import make_client, make_erc20_client

address = "0x8894e0a0c962cb723c1976a4421c95949be2d4e3"
bnb = make_client("bnb").get_balance_in_eth(address)
busd = make_erc20_client("BUSD", "bnb").balanceOf(address) / 10**18
```

# Custom chains & contracts

The factory module only allows to interact with a small list of chains and
contracts.

To interact with an arbitrary EVM chain or smart contract, instantiate a custom
client using the [`BaseClient`](./src/web3client/base_client.py) class.

For a more structured approach, use `web3core`, a sub-package
of [`web3cli`](./src/web3cli/) that comes with many preloaded chains, and allows
to import chains and smart contracts dynamically.

