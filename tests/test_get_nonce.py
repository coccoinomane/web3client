from web3client.Web3Client import Web3Client


def test_get_nonce(web3client: Web3Client) -> None:
    nonce = web3client.getNonce()
    assert type(nonce) is int
    assert nonce >= 0
