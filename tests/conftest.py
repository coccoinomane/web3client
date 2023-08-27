"""
Define shared state for all tests
"""

pytest_plugins = [
    "web3test.ape.fixtures",
    "web3test.web3client.fixtures",
    "web3test.web3factory.fixtures",
]
