# Top priority

- Make a distinction between type 1 and legacy transactions (https://docs.infura.io/networks/ethereum/concepts/transaction-types)
- Autodetect whether the given network supports type-2 transactions

# To do

# Backlog

- Subscribe: There can be many logs per transaction.  Make sure you cache the tx data to avoid fetching it multiple times.
- Merge with [web3core](https://github.com/coccoinomane/web3cli/tree/master/src/web3core)?
- Add Uniswap V2 LP contracts
- Retry until a certain condition is met (via callback)
- Retry: Implement 'retry until gas is low enough'
- BaseClient examples in README.md