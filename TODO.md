# Top priority

# To do

# Backlog

- Make chain_id, tx_type (and maybe more) cached properties of BaseClient
- Cache supports_eip1559() and/or infer_eip1559() in BaseClient
- Merge with [web3core](https://github.com/coccoinomane/web3cli/tree/master/src/web3core)?
- Add Uniswap V2 LP contracts
- Retry until a certain condition is met (via callback)
- Retry: Implement 'retry until gas is low enough'
- Subscribe: There can be many logs per transaction.  Make sure you cache the tx data to avoid fetching it multiple times.
