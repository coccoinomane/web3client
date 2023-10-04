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

- Stream pending transactions on the zkSync Era network:

   ```python
   from web3client.base_client import BaseClient
   
   client = BaseClient("wss://mainnet.era.zksync.io/ws")
   client.subscribe(lambda tx, _, __: print(f"Pending tx: {tx}"))
   ```

- Send 1 ETH and 100 USDC to Unicef, using a dual client:
   ```python
   from web3client.erc20_client import DualClient
   
   rpc = "https://cloudflare-eth.com"
   private_key = "0x..."
   unicef = "0xA59B29d7dbC9794d1e7f45123C48b2b8d0a34636"
   USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"

   usdc_client = DualClient(rpc, private_key=private_key, contract_address=USDC)
   usdc_client.send_eth(unicef, 1)
   usdc_client.transfer(unicef, 100)
   ```

# More examples

Please find more examples

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
