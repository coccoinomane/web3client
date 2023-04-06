import asyncio
import json
from typing import Any, Callable, List, Tuple, Union, cast

from eth_account import Account
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_typing import Address
from eth_typing.encoding import HexStr
from hexbytes import HexBytes
from web3 import Web3
from web3.contract.contract import Contract, ContractFunction
from web3.gas_strategies import rpc
from web3.types import (
    BlockData,
    BlockIdentifier,
    CallOverride,
    Middleware,
    Nonce,
    TxData,
    TxParams,
    TxReceipt,
    Wei,
)
from websockets.client import connect

from web3client.exceptions import TransactionTooExpensive, Web3ClientException


class BaseClient:
    """
    Client to interact with a blockchain, with smart contract
    support.

    The client is a wrapper intended to make the Web3 library
    easier to use.

    There are three ways to use the base client class:
    1. Instantiate an object representing a blockchain and, optionally,
       a smart contract.
    2. Specialize it by making a subclass. Override the parameters
       to match the desired blockchain and, optionally, contract.
    3. If the blockchain and contract you need to use is supported,
       just use one of the 'make' methods in factory.py.

    Attributes
    ----------------------
    node_uri: str | RPC node to use
    chain_id: int = None | ID of the chain
    tx_type: int = 2 | Type of transaction
    private_key: str = None | Private key to use (optional)
    max_priority_fee_in_gwei: float = 1 | Miner's tip, relevant only for type-2 transactions (optional, default is 1)
    upper_limit_for_base_fee_in_gwei: float = inf | Raise an exception if baseFee is larger than this (optional, default is no limit)
    contract_address: Address = None | Address of smart contract (optional)
    abi: dict[str, Any] = None | ABI of smart contract; to generate from a JSON file, use static method get_contract_abi_from_file() (optional)
    middlewares: List[Middleware] = [] | Ordered list of web3.py middlewares to use (optional, default is no middlewares)


    Derived attributes
    ------------------
    w3: Web3 = None | Web3.py client
    account: LocalAccount = None | Account object for the user
    user_address: Address = None | Address of the user
    contract: Contract = None | Contract object of web3.py
    functions: ContractFunctions = None | ContractFunctions object of web3.py
    """

    def __init__(
        self,
        node_uri: str,
        chain_id: int = None,
        tx_type: int = 2,
        private_key: str = None,
        max_priority_fee_in_gwei: float = 1,
        upper_limit_for_base_fee_in_gwei: float = float("inf"),
        contract_address: Address = None,
        abi: dict[str, Any] = None,
        middlewares: List[Middleware] = [],
    ) -> None:
        # Set attributes
        self.chain_id: int = chain_id
        self.tx_type: int = tx_type
        self.max_priority_fee_in_gwei: float = max_priority_fee_in_gwei
        self.upper_limit_for_base_fee_in_gwei: float = upper_limit_for_base_fee_in_gwei
        # Initialize web3.py provider
        if node_uri:
            self.set_provider(node_uri)
        # User account
        if private_key:
            self.set_account(private_key)
        # Initialize the contract
        # TODO: we should be able to load an ABI without a specific address.
        # This might be useful to access the ABI decoding functions of web3.
        # For example, to read events from a tx only the ABI is needed, you
        # do not need the token address.
        if contract_address and abi:
            self.set_contract(contract_address, abi)
        # Add web3.py middlewares
        if middlewares:
            self.set_middlewares(middlewares)

    ####################
    # Setters
    ####################

    def set_provider(self, node_uri: str) -> None:
        self.node_uri: str = node_uri
        self.w3 = self.get_provider(node_uri)

    def set_account(self, private_key: str) -> None:
        self.private_key: str = private_key
        self.account: LocalAccount = Account.from_key(private_key)
        self.user_address: Address = self.account.address

    def set_contract(self, contract_address: Address, abi: dict[str, Any]) -> None:
        self.contract_address: Address = cast(
            Address, Web3.to_checksum_address(contract_address)
        )
        self.abi: dict[str, Any] = abi
        self.contract = self.getContract(contract_address, self.w3, abi=abi)
        self.functions = self.contract.functions

    def set_middlewares(self, middlewares: List[Middleware]) -> None:
        self.middlewares: List[Middleware] = middlewares
        for i, m in enumerate(middlewares):
            self.w3.middleware_onion.inject(m, layer=i)

    ####################
    # Build Tx
    ####################

    def build_base_tx(
        self,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: float = None,
    ) -> TxParams:
        """
        Build a basic transaction with type, nonce, chain ID and gas

        - If not given, the nonce will be computed on chain
        - If not given, the gas limit will be estimated on chain using gas_estimate()
        - For type-2 transactions, if not given, the miner's tip (maxPriorityFeePerGas)
          will be set to self.max_priority_fee_in_gwei
        - For type-2 transactions, the max gas fee is estimated according to the usual
          formula maxMaxFeePerGas = 2 * baseFee + maxPriorityFeePerGas.
        - For type-1 transactions, the gasPrice is estimated on-chain using eth_gasPrice.
        """

        # Properties that you are not likely to change
        tx: TxParams = {
            "chainId": self.chain_id,
            "from": self.user_address,
        }

        # Compute gas fee based on the transaction type
        gas_fee_in_gwei: float = None

        # Pre EIP-1599, we only have gasPrice
        if self.tx_type == 1:
            self.w3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)
            tx["gasPrice"] = self.w3.eth.generate_gas_price()
            gas_fee_in_gwei = float(Web3.from_wei(tx["gasPrice"], "gwei"))

        # Post EIP-1599, we have both the miner's tip and the max fee.
        elif self.tx_type == 2:
            tx["type"] = self.tx_type

            # The miner tip is user-provided
            max_priority_fee_in_gwei = (
                max_priority_fee_in_gwei or self.max_priority_fee_in_gwei
            )
            tx["maxPriorityFeePerGas"] = Web3.to_wei(max_priority_fee_in_gwei, "gwei")

            # The max fee is estimated from the miner tip & block base fee
            (maxFeePerGasInGwei, gas_fee_in_gwei) = self.estimate_max_fee_in_gwei(
                max_priority_fee_in_gwei
            )
            tx["maxFeePerGas"] = Web3.to_wei(maxFeePerGasInGwei, "gwei")

        # Raise an exception if the fee is too high
        self.raise_if_gas_fee_too_high(gas_fee_in_gwei)

        # If not explicitly given, fetch the nonce on chain
        tx["nonce"] = self.get_nonce() if nonce is None else nonce

        # If needed, let web3 compute the gas-limit on chain.
        # For more details, see docs of ContractFunction.transact in
        # https://web3py.readthedocs.io/en/stable/contracts.html
        if gas_limit is not None:
            tx["gas"] = gas_limit

        return tx

    def build_tx_with_value(
        self,
        to: Address,
        value_in_eth: float,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> TxParams:
        """
        Build a transaction involving a transfer of value (in ETH) to an address,
        where the value is expressed in the blockchain token (e.g. ETH or AVAX).
        """
        value_in_wei = self.w3.to_wei(value_in_eth, "ether")
        return self.build_tx_with_value_in_wei(
            to, value_in_wei, nonce, gas_limit, max_priority_fee_in_gwei
        )

    def build_tx_with_value_in_wei(
        self,
        to: Address,
        value_in_wei: Wei,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> TxParams:
        """
        Build a transaction involving a transfer of value (in Wei) to an address,
        where the value is expressed in the blockchain token (e.g. ETH or AVAX).
        """
        tx = self.build_base_tx(
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )
        extra_params: TxParams = {
            "to": to,
            "value": value_in_wei,
            "gas": self.estimate_gas_for_transfer(to, value_in_wei),
        }
        return tx | extra_params

    def build_contract_tx(
        self,
        contract_function: ContractFunction,
        value_in_wei: Wei = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> TxParams:
        """
        Build a transaction that involves a contract interation.

        Requires passing the contract function as detailed in the docs:
        https://web3py.readthedocs.io/en/stable/web3.eth.account.html#sign-a-contract-transaction
        """
        base_tx = self.build_base_tx(
            nonce,
            gas_limit,
            max_priority_fee_in_gwei,
        )
        if value_in_wei:
            base_tx["value"] = value_in_wei
        return contract_function.build_transaction(base_tx)

    ####################
    # Sign & send Tx
    ####################

    def sign_tx(self, tx: TxParams) -> SignedTransaction:
        """
        Sign the give transaction; the private key must have
        been set with setCredential().
        """
        return self.w3.eth.account.sign_transaction(tx, self.private_key)

    def send_signed_tx(self, signed_tx: SignedTransaction) -> HexStr:
        """
        Send a signed transaction and return the tx hash
        """
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.w3.to_hex(tx_hash)

    def sign_and_send_tx(self, tx: TxParams) -> HexStr:
        """
        Sign a transaction and send it
        """
        signed_tx = self.sign_tx(tx)
        return self.send_signed_tx(signed_tx)

    def get_tx_receipt(self, txHash: HexStr) -> TxReceipt:
        """
        Given a transaction hash, wait for the blockchain to confirm
        it and return the tx receipt.
        """
        return self.w3.eth.wait_for_transaction_receipt(txHash)

    def get_tx(self, txHash: Union[HexStr, HexBytes]) -> TxData:
        """
        Given a transaction hash, get the transaction; will raise error
        if the transaction has not been mined yet.
        """
        return self.w3.eth.get_transaction(txHash)

    def send_eth(
        self,
        to: Address,
        value_in_eth: float,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Send ETH to the given address
        """
        tx = self.build_tx_with_value(
            to, value_in_eth, nonce, gas_limit, max_priority_fee_in_gwei
        )
        return self.sign_and_send_tx(tx)

    def send_eth_in_wei(
        self,
        to: Address,
        value_in_wei: Wei,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Send ETH (in Wei) to the given address
        """
        tx = self.build_tx_with_value_in_wei(
            to, value_in_wei, nonce, gas_limit, max_priority_fee_in_gwei
        )
        return self.sign_and_send_tx(tx)

    ####################
    # Messages
    ####################

    def sign_message(self, msg: str) -> SignedMessage:
        """Sign the given message and return the signed message.
        NB: The method uses the 'defunct' encoding for the message, see
        https://eth-account.readthedocs.io/en/stable/eth_account.html
        for more details"""
        msg_hash = encode_defunct(text=msg)
        return self.w3.eth.account.sign_message(msg_hash, self.private_key)

    def is_message_signed_by_me(self, msg: str, signedMessage: SignedMessage) -> bool:
        """Return true if the given defunct-encoded message was signed by me"""
        msg_hash = encode_defunct(text=msg)
        signer_address = self.w3.eth.account.recover_message(
            msg_hash, signature=signedMessage.signature
        )
        return signer_address == self.user_address

    ####################
    # Scan
    ####################

    def subscribe_pending_txs(
        self,
        on_tx: Callable[[str], None],
        on_subscribe: Callable[[str], None] = None,
        once: bool = False,
        subscription_type: str = "newPendingTransactions",
    ) -> None:
        """Asynchronously scan pending transactions with eth_subscribe and call the
        given callback when one is found.

        Details:
         - The callback is called with the transaction hash as argument.
         - The subscription type is 'newPendingTransactions' by default.
         - Provid once=True to stop the subscription after the first transaction is found.

        Caveats:
         - The client must be configured with a websocket RPC endpoint (ws:// or wss://)
         - Not all chains support the 'newPendingTransactions' subscription type.
         - Not all chains have a mempool, e.g. Arbitrum. For these chains, the function will
           just hang.
         - Some chains require a validator node with staked L1 funds to be able to
           access to pending transactions in the mempool (e.g. Avalanche).
         - If you use Alchemy, you might want to use 'alchemy_newPendingTransactions'
           (https://docs.alchemy.com/reference/newpendingtransactions)
        """
        # Raise if not a websocket uri
        rpc_url = self.node_uri
        if not rpc_url.startswith("ws"):
            raise ValueError(
                "Websocket RPC needed to subscribe to pending transactions"
            )

        async def get_event() -> None:
            # Connect to websocket
            async with connect(self.node_uri) as ws:
                # Subscribe to pending transactions
                await ws.send(
                    '{"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["'
                    + subscription_type
                    + '"]}'
                )
                subscription_response = await ws.recv()
                try:
                    subscription_id = json.loads(subscription_response)["result"]
                except Exception as e:
                    raise Web3ClientException(
                        f"Failed to subscribe to pending transactions: {e}"
                    )
                # Call on_subscribe callback
                if on_subscribe:
                    on_subscribe(json.loads(subscription_response))
                while True:
                    # Wait for new transactions
                    tx_response = await asyncio.wait_for(ws.recv(), timeout=15)
                    try:
                        tx_response_json = json.loads(tx_response)
                        tx_subscription = tx_response_json["params"]["subscription"]
                        tx_hash = tx_response_json["params"]["result"]
                    except Exception as e:
                        raise Web3ClientException(
                            f"Failed to parse pending transaction: {e}"
                        )
                    # Call on_tx callback
                    if tx_subscription == subscription_id:
                        on_tx(tx_hash)
                        if once:
                            raise StopAsyncIteration

        # Run loop asynchronously
        loop = asyncio.get_event_loop()
        while True:
            try:
                loop.run_until_complete(get_event())
            except StopAsyncIteration:
                loop.close()
                break

    ####################
    # Gas
    ####################

    def estimate_max_fee_in_gwei(
        self, max_priority_fee_in_gwei: float
    ) -> Tuple[float, float]:
        """
        For Type-2 transactions (post EIP-1559), estimate the maxFeePerGas
        parameter using the formula 2 * baseFee + maxPriorityFeePerGas.

        This is the same formula used by web3 and here
        https://ethereum.stackexchange.com/a/113373/89782

        The baseFee is fetched on chain from the latest block.

        Returns both the estimate (in gwei) and the baseFee
        (also in gwei).
        """
        latest_block = self.w3.eth.get_block("latest")
        base_fee_in_wei = latest_block["baseFeePerGas"]
        base_fee_in_gwei = float(Web3.from_wei(base_fee_in_wei, "gwei"))
        return (2 * base_fee_in_gwei + max_priority_fee_in_gwei, base_fee_in_gwei)

    def estimate_gas_price_in_gwei(self) -> float:
        """
        For Type-1 transactions (pre EIP-1559), estimate the gasPrice
        parameter by asking it directly to the node.

        Docs: https://web3py.readthedocs.io/en/stable/gas_price.html
        """
        self.w3.eth.set_gas_price_strategy(rpc.rpc_gas_price_strategy)
        return float(Web3.from_wei(self.w3.eth.generate_gas_price(), "gwei"))

    def raise_if_gas_fee_too_high(self, gas_fee_in_gwei: float) -> None:
        """
        Raise an exception if the given gas fee in Gwei is too high.

        For Type-1 transactions, pass the gasPrice; for Type-2,
        pass the baseFee.
        """
        if (
            self.upper_limit_for_base_fee_in_gwei is not None
            and gas_fee_in_gwei > self.upper_limit_for_base_fee_in_gwei
        ):
            raise TransactionTooExpensive(
                f"Gas too expensive [fee={gas_fee_in_gwei} gwei, max={self.upper_limit_for_base_fee_in_gwei} gwei]"
            )

    ####################
    # Read
    ####################

    def get_nonce(self, address: Address = None) -> Nonce:
        if not address:
            address = self.user_address
        return self.w3.eth.get_transaction_count(address)

    def get_latest_block(self) -> BlockData:
        """
        Return the latest block
        """
        return self.w3.eth.get_block("latest")

    def get_pending_block(self) -> BlockData:
        """
        Return the pending block
        """
        return self.w3.eth.get_block("pending")

    def estimate_gas_for_transfer(self, to: Address, value_in_wei: Wei) -> int:
        """
        Return the gas that would be required to send some ETH
        (expressed in Wei) to an address
        """
        return self.w3.eth.estimate_gas(
            {
                "from": self.user_address,
                "to": to,
                "value": value_in_wei,
            }
        )

    def get_balance_in_wei(self, address: Address = None) -> Wei:
        return self.w3.eth.get_balance(Web3.to_checksum_address(address))

    def get_balance_in_eth(self, address: Address = None) -> float:
        return float(Web3.from_wei(self.get_balance_in_wei(address), "ether"))

    ####################
    # Contract
    ####################

    def call(
        self,
        function: ContractFunction,
        tx: TxParams = None,
        block_identifier: BlockIdentifier = "latest",
        state_override: CallOverride = None,
    ) -> Any:
        """
        Execute a contract function call using the eth_call interface.
        This won't write to the blockchain.

        Example: get the balance of an address for an ERC20 token:
            client.call(
                client.functions.balanceOf(address)
            )
        """
        return function.call(tx, block_identifier, state_override)

    def transact(
        self,
        function: ContractFunction,
        value_in_wei: Wei = None,
        nonce: Nonce = None,
        gas_limit: int = None,
        max_priority_fee_in_gwei: int = None,
    ) -> HexStr:
        """
        Execute a contract function.
        This will write to the blockchain.

        Example: transfer some tokens to the given address:
            client.transact(
                client.functions.transfer(address, amount)
            )
        """
        tx: TxParams = self.build_contract_tx(
            function, value_in_wei, nonce, gas_limit, max_priority_fee_in_gwei
        )
        return self.sign_and_send_tx(tx)

    ####################
    # Utils
    ####################

    @staticmethod
    def getContract(
        address: Address,
        provider: Web3,
        abi_file: str = None,
        abi: dict[str, Any] = None,
    ) -> Contract:
        """
        Load the smart contract, required before running
        build_contract_tx().
        """
        checksum = Web3.to_checksum_address(address)
        if abi_file:
            abi = BaseClient.get_contract_abi_from_file(abi_file)
        return provider.eth.contract(address=checksum, abi=abi)

    @staticmethod
    def get_contract_abi_from_file(file_name: str) -> Any:
        with open(file_name, encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def get_provider(node_uri: str) -> Web3:
        """
        Initialize provider (HTTPS & WS supported).

        TODO: Support autodetection with empty node_uri
        docs here https://web3py.readthedocs.io/en/stable/providers.html#how-automated-detection-works
        """
        if node_uri[0:4] == "http":
            return Web3(Web3.HTTPProvider(node_uri))
        elif node_uri[0:2] == "ws":
            return Web3(Web3.WebsocketProvider(node_uri))
        else:
            return Web3()

    @staticmethod
    def get_gas_spent_in_eth(txReceipt: TxReceipt) -> float:
        """
        Given the transaction receipt, return the ETH that
        was spent in gas to process the transaction
        """
        return float(
            Web3.from_wei(
                txReceipt["effectiveGasPrice"] * txReceipt["gasUsed"], "ether"
            )
        )
