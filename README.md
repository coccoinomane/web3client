Batteries-included client to interact with blockchains and smart contracts.

# Features

- Easily create a client to interact with EVM-compatible chains.
- Support for ERC20 operations, using the token name (e.g. USDC) instead of address.
- Preconfigured for the most popular chains: Ethereum, Binance, Avalanche and more to come!
- Exposes the underlying web3.py client to allow for more flexibility

# Examples

Get the latest block on both Ethereum, BNB Chain and Avalanche:

```python
from web3factory.factory import make_client

eth_block = make_client('ethereum').getLatestBlock()
bnb_block = make_client('binance').getLatestBlock()
avax_block = make_client('avalanche').getLatestBlock()
```

Get the ETH and USDC balances of the Ethereum foundation:

```python
from web3factory.factory import make_client, make_erc20_client

address = "0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae"
eth = make_client("ethereum").getBalanceInEth(address)
usdc = make_erc20_client("USDC", "ethereum").balanceOf(address) / 10**6
```

Get the BNB and BUSD balances of Binance's hot wallet:

```python
from web3factory.factory import make_client, make_erc20_client

address = "0x8894e0a0c962cb723c1976a4421c95949be2d4e3"
bnb = make_client("binance").getBalanceInEth(address)
busd = make_erc20_client("BUSD", "binance").balanceOf(address) / 10**18
```

### More examples

Please have a look at the [examples folder](./examples) 🙂

# Install

```bash
pip3 install -U web3client
```

# It doesn't work 😡

Don't panic! Instead...

1. Please check if your issue is listed in the [Issues tab](https://github.com/coccoinomane/web3client/issues).
2. If not, consider [writing a new issue](https://github.com/coccoinomane/web3client/issues/new) 🙂

# Contribute ❤️

Pull requests are welcome!

1. Install and configure [PDM](https://github.com/pdm-project/pdm/):
   ```bash
   curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
   ```
2. Install dependencies: 
   ```bash
   pdm install
   ```
3. To run the CLI against your changes: 
   ```bash
   pdm web3client
   ```
4. To run tests:
   ```bash
   pdm test
   ```

# TO DO

- Test ERC20 read functions
- Automatically convert addresses to checksum
- Harmonize between camel case and snake case
- Easy accessors for token and network props
- Add write examples and tests
- Add Uniswap V2 LP contracts