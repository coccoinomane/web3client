Easy to use Python client to interact with multiple EVM blockchain.

# Features

- Easily create a client to interact with EVM-compatible chains.
- Preconfigured for the most popular chains: Ethereum, Binance, Avalanche, Cronos, etc.
- Support for ERC20 operations, using the token name (e.g. USDC) instead of address.
- Exposes the underlying web3.py client to allow for more flexibility

# Examples

Get the latest block on both Ethereum, BNB Chain and Avalanche:

```python
from web3factory.factory import make_client

eth_block = make_client('ethereum').getLatestBlock()
bnb_block = make_client('binance').getLatestBlock()
avax_block = make_client('avalanche').getLatestBlock()
```

Get the USDC balance of the Ethereum foundation, and the BUSD balance of Binance's hot wallet:

```python
from web3factory.factory import make_erc20_client

ef_address = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"
ef_usdc = make_erc20_client("USDC", "ethereum").balanceOf(ef_address) / 10**6

bw_address = "0x8894e0a0c962cb723c1976a4421c95949be2d4e3"
bw_busd = make_erc20_client("BUSD", "binance").balanceOf(bw_address) / 10**18
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
- Add write examples and tests
- Add Uniswap V2 LP contracts