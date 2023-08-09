"""
Define shared state for all tests
"""

pytest_plugins = [
    "tests.ape.tests.fixtures",
    "tests.web3client.fixtures",
    "tests.web3factory.fixtures",
]
