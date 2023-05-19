from typing import Any, Dict, List

import pytest

from web3client.base_client import BaseClient


@pytest.mark.parametrize(
    "msg",
    [
        "Hello world!",
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam pulvinar lacus erat, et sollicitudin purus rutrum sed. Aliquam pulvinar nunc nec sagittis sagittis. Nunc efficitur lacus urna, sed dapibus lacus varius id. Nam laoreet convallis nisl, ut lacinia sem congue eu. Phasellus eu nisi in lectus lobortis viverra a at diam. Nulla dolor nisl, mollis efficitur venenatis in, elementum consequat quam. Sed a euismod justo, quis maximus velit. Maecenas varius augue dolor, sit amet elementum lacus pretium vitae. Fusce egestas condimentum quam eget elementum. Suspendisse vulputate ut urna a pretium. Nunc semper a sem fermentum dapibus.",
        "I will copiously donate to coccoinomane",
    ],
)
def test_sign(msg: str, signers: List[Dict[str, Any]]) -> None:
    for signer in signers:
        client = BaseClient(node_uri=None, private_key=signer["private_key"])
        signed_message = client.sign_message(msg)
        assert client.is_message_signed_by_me(msg, signed_message)
        assert "messageHash" in signed_message._asdict()
        assert "r" in signed_message._asdict()
        assert "s" in signed_message._asdict()
        assert "v" in signed_message._asdict()
        assert "signature" in signed_message._asdict()
