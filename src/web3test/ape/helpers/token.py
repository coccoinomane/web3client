import ape


def deploy_token(
    accounts: ape.managers.accounts.AccountManager,
    token_container: ape.contracts.ContractContainer,
    name: str = "Test Token",
    symbol: str = "TST",
    decimals: int = 18,
    initial_supply: int = 10000,
    distribute: bool = True,
) -> ape.contracts.ContractInstance:
    """Deploy a test token, and distribute it to all accounts. The token
    will be deployed by alice (accounts[0]) and optionally distributed
    to all other accounts."""
    token = token_container.deploy(
        name, symbol, decimals, initial_supply * 10**decimals, sender=accounts[0]
    )
    if distribute:
        for account in accounts[1:]:
            token.transfer(
                account,
                int(initial_supply / len(accounts)) * 10**decimals,
                sender=accounts[0],
            )
    return token
