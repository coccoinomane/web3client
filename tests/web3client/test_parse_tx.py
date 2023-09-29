from hexbytes import HexBytes

from web3client.helpers.tx import parse_raw_tx


def test_parse_tx_type2_eth_transfer() -> None:
    # ETH transfer on Optimism (tx 0x8631361df65445a40fc46cff4625a2c070e618733d9ebdf31a31535276225b85)
    raw_tx = "0x02f86a0a75843b9aca0084412e386682520894240abf8acb28205b92d39181e2dab0b0d8ea6e5d6480c080a0a942241378fafc80670c6dde3c39ba5b1c4f992cd26fa263e7bbc253696c9035a008cf3399808cb511f0171be2ba766ea5c9d424a97dae3fb24685c440eeefc4fa"
    expected = {
        "accessList": (),
        "blockHash": None,
        "blockNumber": None,
        "chainId": 10,
        "data": HexBytes("0x"),
        "from": "0x240AbF8ACB28205B92D39181e2Dab0B0D8eA6e5D",
        "gas": 21000,
        "gasPrice": None,
        "maxFeePerGas": 1093548134,
        "maxPriorityFeePerGas": 1000000000,
        "hash": HexBytes(
            "0x8631361df65445a40fc46cff4625a2c070e618733d9ebdf31a31535276225b85"
        ),
        "input": None,
        "nonce": 117,
        "r": HexBytes(
            "0xa942241378fafc80670c6dde3c39ba5b1c4f992cd26fa263e7bbc253696c9035"
        ),
        "s": HexBytes(
            "0x08cf3399808cb511f0171be2ba766ea5c9d424a97dae3fb24685c440eeefc4fa"
        ),
        "to": "0x240AbF8ACB28205B92D39181e2Dab0B0D8eA6e5D",
        "transactionIndex": None,
        "type": 2,
        "v": None,
        "value": 100,
    }
    assert parse_raw_tx(raw_tx) == expected


def test_parse_tx_type2_token_transfer() -> None:
    # USDC transfer (tx 0x444d05672fd04d99d417ce2105f34414758bcfb0579b686197cbf829458e3477)
    raw_tx = "0x02f8b00101847735940085060db8840082e4b794a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4880b844a9059cbb00000000000000000000000028c6c06298d514db089934071355e5743bf21d6000000000000000000000000000000000000000000000000000000000042c1d80c001a02e18a3a75c10ba1be4ecb314e37c3a3eb5630be7e26692da3f3145f8b1efb54aa0458adf97080dc4955ea4e0f6d628cdcd278af74e9c65a2f15b7c20e0005d2fd9"
    expected = {
        "accessList": (),
        "blockHash": None,
        "blockNumber": None,
        "chainId": 1,
        "data": HexBytes(
            "0xa9059cbb00000000000000000000000028c6c06298d514db089934071355e5743bf21d6000000000000000000000000000000000000000000000000000000000042c1d80"
        ),
        "from": "0xF693EC528B3837eAd9B82D16bEc5d2fD4E430006",
        "gas": 58551,
        "gasPrice": None,
        "maxFeePerGas": 26000000000,
        "maxPriorityFeePerGas": 2000000000,
        "hash": HexBytes(
            "0x444d05672fd04d99d417ce2105f34414758bcfb0579b686197cbf829458e3477"
        ),
        "input": None,
        "nonce": 1,
        "r": HexBytes(
            "0x2e18a3a75c10ba1be4ecb314e37c3a3eb5630be7e26692da3f3145f8b1efb54a"
        ),
        "s": HexBytes(
            "0x458adf97080dc4955ea4e0f6d628cdcd278af74e9c65a2f15b7c20e0005d2fd9"
        ),
        "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "transactionIndex": None,
        "type": 2,
        "v": None,
        "value": 0,
    }
    assert parse_raw_tx(raw_tx) == expected


def test_parse_tx_legacy_token_transfer() -> None:
    # Token transfer on Ethereum (tx 0xb808400bd5a1dd9c37960c515d2493c380b829c5a592e499ed0d5d9913a6a446)
    raw_tx = "0xf8a910850684ee180082e48694a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4880b844a9059cbb000000000000000000000000b8b59a7bc828e6074a4dd00fa422ee6b92703f9200000000000000000000000000000000000000000000000000000000010366401ba0e2a4093875682ac6a1da94cdcc0a783fe61a7273d98e1ebfe77ace9cab91a120a00f553e48f3496b7329a7c0008b3531dd29490c517ad28b0e6c1fba03b79a1dee"
    expected = {
        "accessList": [],
        "blockHash": None,
        "blockNumber": None,
        "chainId": None,
        "data": HexBytes(
            "0xa9059cbb000000000000000000000000b8b59a7bc828e6074a4dd00fa422ee6b92703f920000000000000000000000000000000000000000000000000000000001036640"
        ),
        "from": "0xD8cE57B469962b6Ea944d28b741312Fb7E78cfaF",
        "gas": 58502,
        "gasPrice": 28000000000,
        "maxFeePerGas": 28000000000,
        "maxPriorityFeePerGas": 28000000000,
        "hash": HexBytes(
            "0xb808400bd5a1dd9c37960c515d2493c380b829c5a592e499ed0d5d9913a6a446"
        ),
        "input": None,
        "nonce": 16,
        "r": HexBytes(
            "0xe2a4093875682ac6a1da94cdcc0a783fe61a7273d98e1ebfe77ace9cab91a120"
        ),
        "s": HexBytes(
            "0x0f553e48f3496b7329a7c0008b3531dd29490c517ad28b0e6c1fba03b79a1dee"
        ),
        "to": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "transactionIndex": None,
        "type": None,
        "v": None,
        "value": 0,
    }
    assert parse_raw_tx(raw_tx) == expected
