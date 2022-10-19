Easy to use Python client to interact with multiple EVM blockchain.

# Features

- Easily create a client to interact with EVM-compatible chains.
- Preconfigured for the most popular chains: Ethereum, Binance, Avalanche, Cronos, etc.
- Exposes the underlying web3.py client to allow for more flexibility

# Examples

Get the latest block on both Ethereum and Avalanche:

```python
from web3factory.factory import make_client

print(make_client('ethereum').getLatestBlock())
print(make_client('avalanche').getLatestBlock())
```

Use your RPC for better performance:

```python
print(make_client('ethereum', 'https://mainnet.infura.io/v3/<api-key>').getLatestBlock())
```

# Install

```bash
pip3 install -U web3client
```

# It doesn't work 😡

Don't panic! Instead...

1. Please check if your issue is listed in the [Issues tab](https://github.com/coccoinomane/web3client/issues).
2. If not, consider [writing a new issue](https://github.com/coccoinomane/web3client/issues/new) 🙂

# Testing

```bash
pytest tests
```

# TO DO

- Test ERC20 read functions
- Harmonize between camel case and snake case
- Easy accessors for token and network props
- Add BNB chain
- Add write examples and tests
- Add Uniswap V2 LP contracts