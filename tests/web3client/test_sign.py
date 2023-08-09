import pytest

from web3client.base_client import BaseClient

signers = [
    {
        "name": "vanity_1",
        "address": "0x0c2010dc4736bab060740D3968cf1dDF86196D81",
        "private_key": "d94e4166f0b3c85ffebed3e0eaa7f7680ae296cf8a7229d637472b7452c8602c",
    },
    {
        "name": "vanity_2",
        "address": "0x206D4d644c22dDFc343b3AD23bBc7A42c8B201fc",
        "private_key": "3bc2f9b05ac28389fd65fd40068a10f730ec66b6293f9cfd8fe804d212ce06bb",
    },
    {
        "name": "vanity_3",
        "address": "0x9fF0c40eDe4585a5E9f0F00009ce79b6344cB663",
        "private_key": "f76c67c2dd62222a5ec747116a66c573f3795c53276c0cdeafbcb5f597e2f8d4",
    },
]


@pytest.mark.parametrize(
    "msg",
    [
        "Hello world!",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam pulvinar lacus erat, et sollicitudin purus rutrum sed. Aliquam pulvinar nunc nec sagittis sagittis. Nunc efficitur lacus urna, sed dapibus lacus varius id. Nam laoreet convallis nisl, ut lacinia sem congue eu. Phasellus eu nisi in lectus lobortis viverra a at diam. Nulla dolor nisl, mollis efficitur venenatis in, elementum consequat quam. Sed a euismod justo, quis maximus velit. Maecenas varius augue dolor, sit amet elementum lacus pretium vitae. Fusce egestas condimentum quam eget elementum. Suspendisse vulputate ut urna a pretium. Nunc semper a sem fermentum dapibus.",
        "I will copiously donate to coccoinomane",
    ],
)
def test_sign(msg: str) -> None:
    for signer in signers:
        client = BaseClient(node_uri=None, private_key=signer["private_key"])
        signed_message = client.sign_message(msg)
        assert client.is_message_signed_by_me(msg, signed_message)
        assert "messageHash" in signed_message._asdict()
        assert "r" in signed_message._asdict()
        assert "s" in signed_message._asdict()
        assert "v" in signed_message._asdict()
        assert "signature" in signed_message._asdict()
