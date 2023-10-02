Batteries-included client to interact with blockchains and smart contracts; used by [`web3cli`](https://github.com/coccoinomane/web3cli) and [crabada.py](https://github.com/coccoinomane/crabada.py).

# Features

- Easily create a client to interact with EVM-compatible chains
- Works with Ethereum, Binance, Avalanche, Arbitrum One, zkSync Era, etc.
- Subscribe to pending transactions in the mempool and new blocks
- Flexible logging of RPC calls and transactions
- Interact with tokens and ETH with the same dual interface
- Includes a client for Compound V2 operations, and its clones
- Save gas by setting an upper limit on the base fee
- Need more flexibility? Use directly the underlying web3.py client


# Install

```bash
pip3 install -U web3client
```

# Examples

I am working on a tutorial, but in the meantime, you can find some examples

- in the [examples folder](./examples), and
- in the [tests folder](./tests).


# Test suite `web3test`

`web3client` comes with several pytest plugins you can use to test your scripts:

- `web3test-ape`: fixtures of accounts and smart contracts (erc20, compound, etc)
- `web3test-web3client`: fixtures of clients for various smart contracts 
- `web3test-web3factory`: fixtures of clients for various chains

To use one or more plugins in your script, add the following lines at the top of your `conftest.py``:

```python
pytest_plugins = [
    "web3test-ape", "web3test-web3client", "web3test-web3factory"
]
```

The order of the plugins in the aray is important.

# It doesn't work 😡

Don't panic! Instead...

1. Please check if your issue is listed in the [Issues tab](https://github.com/coccoinomane/web3client/issues).
2. If not, consider [writing a new issue](https://github.com/coccoinomane/web3client/issues/new) 🙂

# Contributing

All contributions are welcome! To start improving `web3client`, please refer to our [__contribution guide__](./CONTRIBUTING.md).
