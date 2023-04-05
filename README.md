Batteries-included client to interact with blockchains and smart contracts; used by [`web3cli`](https://github.com/coccoinomane/web3cli) and [crabada.py](https://github.com/coccoinomane/crabada.py).

# Features

- Easily create a client to interact with EVM-compatible chains
- Perform ERC20 operations, using the token name (e.g. USDC) instead of address.
- Interact with the most popular chains: Ethereum, Binance, Avalanche, Arbitrum One, zkSync Era, and more to come!
- Save gas by setting an upper limit on the base fee.
- Need more flexibility? Use directly the underlying web3.py client.

# Install

```bash
pip3 install -U web3client
```

# Examples

Get the latest block on both Ethereum, BNB Chain and Avalanche:

```python
from web3factory.factory import make_client

eth_block = make_client("eth").get_latest_block()
bnb_block = make_client("bnb").get_latest_block()
avax_block = make_client("avax").get_latest_block()
arb_block = make_client("arb").get_latest_block()
era_block = make_client("era").get_latest_block()
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

### More examples

Please have a look at the [tests folder](./tests) or at the [examples folder](./examples) 🙂

# Custom chains & contracts

The factory module only allows to interact with a small list of chains and
contracts.

To interact with an arbitrary EVM chain or smart contract, instantiate a custom
client using the [`BaseClient`](./src/web3client/base_client.py) class.

For a more structured approach, use `web3core`, a sub-package
of [`web3cli`](./src/web3cli/) that comes with many preloaded chains, and allows
to import chains and smart contracts dynamically.

# It doesn't work 😡

Don't panic! Instead...

1. Please check if your issue is listed in the [Issues tab](https://github.com/coccoinomane/web3client/issues).
2. If not, consider [writing a new issue](https://github.com/coccoinomane/web3client/issues/new) 🙂

# Contributing

All contributions are welcome! To start improving `web3client`, please refer to our [__contribution guide__](./CONTRIBUTING.md).
