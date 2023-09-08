from __future__ import annotations

import asyncio
import json
import time
from os.path import dirname, isfile, realpath
from pathlib import Path
from typing import Any, Callable, List, Tuple, Type, Union, cast

import websockets
from eth_account import Account
from eth_account.datastructures import SignedMessage, SignedTransaction
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_typing.encoding import HexStr
from hexbytes import HexBytes
from typing_extensions import Self
from web3 import Web3
from web3.contract.contract import Contract, ContractFunction, ContractFunctions
from web3.exceptions import TransactionNotFound
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
from web3client.helpers.subscribe import parse_notification, subscribe_to_notification
from web3client.types import (
    AsyncSubscriptionCallback,
    SubscriptionCallback,
    SubscriptionType,
)


class BaseClient:
    """
    Client to interact with a blockchain, with smart contract
    support.

    The client is a wrapper intended to make the Web3 library
    easier to use.

    Attributes
    ----------------------
    node_uri: str | RPC node to use.  Set it to None for a uninitialized client.
    chain_id: int = None | ID of the chain.  If not given, it will be inferred from the node.
    tx_type: int = 2 | Type of transaction: 1 for pre-EIP-1599, 2 for EIP-1599. More details here > https://docs.infura.io/infura/networks/ethereum/concepts/transaction-types
    private_key: str = None | Private key to use (optional)
    max_priority_fee_in_gwei: float = 1 | Miner's tip, relevant only for type-2 transactions (optional, default is 1)
    upper_limit_for_base_fee_in_gwei: float = inf | Raise an exception if baseFee is larger than this (optional, default is no limit)
    contract_address: str = None | Address of smart contract (optional)
    abi: dict[str, Any] = None | ABI of smart contract; to read from a JSON file, use class method get_abi_json() (optional)
    middlewares: List[Middleware] = [] | Ordered list of web3.py middlewares to use (optional, default is no middlewares)


    Derived attributes
    ------------------
    w3: Web3 = None | Web3.py client
    account: LocalAccount = None | Account object for the user
    user_address: str = None | Address of the user
    contract: Contract = None | Contract object of web3.py
    functions: ContractFunctions = None | ContractFunctions object of web3.py
    """

    # Attributes that can be set in the constructor or
    # overridden by subclasses
    node_uri: str = None
    chain_id: int = None
    tx_type: int = None
    private_key: str = None
    max_priority_fee_in_gwei: float = None
    upper_limit_for_base_fee_in_gwei: float = None
    abi: dict[str, Any] = None
    contract_address: str = None
    middlewares: List[Middleware] = None

    # Derived attributes
    w3: Web3
    account: LocalAccount
    user_address: str
    contract: Contract
    functions: ContractFunctions

    # Class attributes
    abi_dir: Union[Path, str] = Path(dirname(realpath(__file__))) / "abi"

    def __init__(
        self,
        node_uri: str,
        chain_id: int = None,
        tx_type: int = 2,
        private_key: str = None,
        max_priority_fee_in_gwei: float = 1,
        upper_limit_for_base_fee_in_gwei: float = float("inf"),
        contract_address: str = None,
        abi: dict[str, Any] = None,
        middlewares: List[Middleware] = [],
    ) -> None:
        # Set the w3 client
        self.set_provider(node_uri)

        # Set attributes.  The 'if' part is to allow subclasses to override
        # the parameters.
        if chain_id:
            self.chain_id = chain_id
        if tx_type:
            self.tx_type = tx_type
        if private_key:
            self.set_account(private_key)
        if max_priority_fee_in_gwei:
            self.max_priority_fee_in_gwei = max_priority_fee_in_gwei
        if upper_limit_for_base_fee_in_gwei:
            self.upper_limit_for_base_fee_in_gwei = upper_limit_for_base_fee_in_gwei
        if abi:
            self.abi = abi
        if contract_address:
            self.set_contract(contract_address)
        if middlewares:
            self.set_middlewares(middlewares)

        # Further initialization
        self.init()

    def init(self) -> None:
        """Further initialization.  Run after __init__.  Useful for subclasses
        who do not want to override __init__()"""
        pass

    ####################
    # Setters
    ####################

    def set_provider(self, node_uri: str) -> Self:
        self.node_uri = node_uri
        self.w3 = self.get_provider(node_uri)
        return self

    def set_account(self, private_key: str) -> Self:
        """Make it possible for the client to sign transactions with the
        given private key"""
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.user_address = self.account.address
        self.w3.eth.default_account = self.account.address
        return self

    def unset_account(self) -> Self:
        """Unset the previously added account, thus making it impossible
        for the client to sign transactions"""
        self.private_key = None
        self.account = None
        self.user_address = None
        self.w3.eth.default_account = None
        return self

    def set_contract(self, contract_address: str, abi: dict[str, Any] = None) -> Self:
        abi = abi or self.abi
        if not abi:
            raise Web3ClientException("ABI not set")
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.get_contract(contract_address, self.w3, abi=abi)
        self.functions = self.contract.functions
        return self

    def set_middlewares(self, middlewares: List[Middleware]) -> Self:
        self.middlewares = middlewares
        for i, m in enumerate(middlewares):
            self.w3.middleware_onion.inject(m, layer=i)
        return self

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
            "chainId": self.chain_id or self.w3.eth.chain_id,
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
            tx["type"] = Web3.to_hex(self.tx_type)

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
        else:
            raise Web3ClientException(
                f"Transaction with tx_type={self.tx_type} not supported, use either 1 or 2"
            )

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
        to: str,
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
        to: str,
        value_in_wei: int,
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
            "value": cast(Wei, value_in_wei),
            "gas": self.estimate_gas_for_transfer(to, value_in_wei),
        }
        return tx | extra_params

    def build_contract_tx(
        self,
        contract_function: ContractFunction,
        value_in_wei: int = None,
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
            base_tx["value"] = cast(Wei, value_in_wei)
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

    def send_eth(
        self,
        to: str,
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
        to: str,
        value_in_wei: int,
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
    # Get Txs
    ####################

    def get_tx_receipt(self, tx_hash: HexStr) -> TxReceipt:
        """
        Given a transaction hash, wait for the blockchain to confirm
        it and fetch the tx receipt.
        """
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def get_tx(self, tx_hash: Union[HexStr, HexBytes]) -> TxData:
        """
        Given a transaction hash, fetch the transaction data from
        the blockchain; will raise error if the transaction has not
        been mined yet.
        """
        return self.w3.eth.get_transaction(tx_hash)

    def poll_tx(self, tx_hash: HexStr, interval: int = 1, timeout: int = 10) -> TxData:
        """Fetch a transaction from the blockchain. If the transaction is not
        found, poll until it is found. If it is not found after poll_timeout
        seconds, raises web3.exceptions.TransactionNotFound.

        ARGUMENTS
        ---------
        - tx_hash (str): The transaction hash.
        - poll_interval (int): The number of seconds to wait between polls. Set
        to None to disable polling.
        - poll_timeout (int): The number of seconds to wait before timing out.
        Set to None to wait indefinitely. Set to zero to disable polling.
        """
        if interval is None:
            return self.get_tx(tx_hash)

        start_time = time.time()
        while True:
            try:
                return self.get_tx(tx_hash)
            except TransactionNotFound as e:
                time.sleep(interval)
                if time.time() - start_time > timeout:
                    raise e

    def get_tx_from_notification(
        self,
        subscription_type: SubscriptionType,
        data: Any,
        poll_interval: int = 1,
        poll_timeout: int = 10,
    ) -> TxData:
        """Given an eth_subscribe notification, extract the transaction hash from it,
        fetch the corresponding transaction, then return the transaction data."""
        if subscription_type == "newPendingTransactions":
            tx_hash = data
        elif subscription_type == "logs":
            tx_hash = data["transactionHash"]
        else:
            raise Web3ClientException(
                f"Cannot extract transaction from notifications of type '{subscription_type}'"
            )
        return self.poll_tx(tx_hash, interval=poll_interval, timeout=poll_timeout)

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

    def subscribe(
        self,
        on_notification: SubscriptionCallback,
        on_subscribe: Callable[[Any, SubscriptionType], None] = None,
        on_connection_closed: Callable[[Exception, SubscriptionType], None] = None,
        once: bool = False,
        subscription_type: SubscriptionType = "newPendingTransactions",
        logs_addresses: List[str] = None,
        logs_topics: List[str] = None,
        tx_from: List[str] = None,
        tx_to: List[str] = None,
        tx_value: Tuple[float, float] = None,
        tx_on_fetch: Callable[[TxData, Any], None] = None,
        tx_on_fetch_error: Callable[[Exception, Any], None] = None,
        tx_fetch_timeout: int = 10,
        ws_timeout: int = None,
    ) -> None:
        """Look for new pending transactions, blocks or events; when one is found,
        call the 'on_notification' callback.

        Notifications are processed one at a time; if you need concurrent execution,
        use async_subscribe() instead.

        Subscription types (same as eth_subscribe RPC method):

         - Use 'newHeads' to listen to new blocks. The callback receives a dict with
           the block parameters as first argument.
         - Use 'newPendingTransactions' to listen to pending transactions. The callback
           receives the transaction hash as first argument.
         - Use 'logs' to listen to contract event logs. The callback receives a dict
           with the smart contract address, the 'data' input field, the 'topics' fields
           plus info on the block and the transaction. If you want to filter by contract
           address and/or topics, pass them as arguments.
         - Regardless of the subscription type, the callback receives the subscription
           type as second argument.  If using transaction filters (see below) then the
           callback receives the fetched transaction data as third argument.
         - For a full reference, see https://geth.ethereum.org/docs/interacting-with-geth/rpc/pubsub

        Details:

         - Provid once=True to stop the subscription after the first occurrency.
         - If you use Alchemy, you might want to use 'alchemy_newPendingTransactions'
           (https://docs.alchemy.com/reference/newpendingtransactions)
         - Subscription is good to react fast to changes on the blockchain, but you might
           miss some events. If you are ok with a slower but more reliable approach, use
           filters (eth_filter).
         - To raise an error when no notification is received for a while, set ws_timeout
           to a value in seconds.
         - The function will automatically try to reconnect if the connection is closed.
           This can happen when the network is unstable or when the node is restarted.
           To exit instead, raise an exception in the callback on_connection_closed
           (e, subscription_type).

        Transaction filters:
         - Use tx_from, tx_to and tx_value to filter transactions by sender, receiver
           and value.  The value is a tuple (min, max) in ETH.
         - Transaction filters are meant as a convenience to avoid fetching and filtering
           transactions manually in the callback.  Finer-grained filters should be
           implemented directly at the callback level.
         - When using tx filters, the on_notification callback will receive the transaction
           data as third argument.
         - If any of the tx filters is used, the client will fetch every single transaction
           it receives.  Be aware that this might put stress in the node especially if you
           use the pending transactions subscription.
         - If you use tx_from, tx_to or tx_value, you can optionally pass a callback
           tx_on_fetch(tx, data) that will be called after fetching the transaction,
           and a callback tx_on_fetch_error(e, data) that will be called if the
           transaction cannot be fetched.

        Caveats:

         - The client must be configured with a websocket RPC endpoint (ws:// or wss://)
           or a local IPC endpoint (ending in .ipc).
         - Not all chains support the 'newPendingTransactions' subscription type.
         - Not all chains have a mempool, e.g. Arbitrum. For these chains, the function will
           just hang if asking for 'newPendingTransactions'.
         - Some chains require a validator node with staked L1 funds to be able to
           access to pending transactions while they are in the mempool (e.g. Avalanche).
           On these chains, you might still receive pending transactions, but they will
           likely be already mined.
        """
        # Raise if not a websocket uri
        rpc_url = self.node_uri
        if not rpc_url.startswith("ws") and not rpc_url.endswith(".ipc"):
            raise ValueError("Websocket RPC needed to subscribe to node notifications")

        def process_notification(
            notification: Union[str, bytes], subscription_id: str
        ) -> None:
            id, data = parse_notification(notification, subscription_type)
            if id != subscription_id:
                return

            # Simple case: no filtering based on tx
            if not tx_from and not tx_to and not tx_value:
                on_notification(data, subscription_type, None)

            # Complex case: filter based on tx
            # TODO: There can be many logs per transaction.  Make sure
            # you cache the tx data to avoid fetching it multiple times.
            else:
                try:
                    tx = self.get_tx_from_notification(
                        subscription_type, data, poll_timeout=tx_fetch_timeout
                    )
                    if tx_on_fetch:
                        tx_on_fetch(tx, data)
                except Exception as e:
                    if tx_on_fetch_error:
                        tx_on_fetch_error(e, data)
                    return

                if self.filter_tx(tx, tx_from, tx_to, tx_value):
                    on_notification(data, subscription_type, tx)

        async def main() -> None:
            # Connect to websocket
            async for ws in connect(self.node_uri):
                try:
                    # Subscribe to the notification type
                    subscription_id = await subscribe_to_notification(
                        ws, subscription_type, on_subscribe, logs_addresses, logs_topics
                    )
                    # Main loop
                    while True:
                        # Wait for new notifications
                        notification = await asyncio.wait_for(
                            ws.recv(), timeout=ws_timeout
                        )
                        process_notification(notification, subscription_id)
                        if once:
                            return
                except (
                    websockets.exceptions.ConnectionClosedError,
                    websockets.exceptions.ConnectionClosedOK,
                ) as e:
                    if on_connection_closed:
                        on_connection_closed(e, subscription_type)
                    continue

        asyncio.run(main())

    async def async_subscribe(
        self,
        on_notification: AsyncSubscriptionCallback,
        on_subscribe: Callable[[Any, SubscriptionType], None] = None,
        on_connection_closed: Callable[[Exception, SubscriptionType], None] = None,
        once: bool = False,
        subscription_type: SubscriptionType = "newPendingTransactions",
        logs_addresses: List[str] = None,
        logs_topics: List[str] = None,
        tx_from: List[str] = None,
        tx_to: List[str] = None,
        tx_value: Tuple[float, float] = None,
        tx_on_fetch: Callable[[TxData, Any], None] = None,
        tx_on_fetch_error: Callable[[Exception, Any], None] = None,
        tx_fetch_timeout: int = 10,
        ws_timeout: int = None,
    ) -> None:
        """Look for new pending transactions, blocks or events; when one is found,
        call the 'on_notification' callback concurrently.

        Call this function with asyncio.run(client.async_subscribe(callback)), where the
        callback must be an async function.  For more details, see subscribe().

        Please find the detailed description of the arguments in subscribe().
        """
        # Raise if not a websocket uri
        rpc_url = self.node_uri
        if not rpc_url.startswith("ws") and not rpc_url.endswith(".ipc"):
            raise ValueError("Websocket RPC needed to subscribe to node notifications")

        async def process_notification(
            notification: Union[str, bytes], subscription_id: str
        ) -> None:
            id, data = parse_notification(notification, subscription_type)
            if id != subscription_id:
                return

            # Simple case: no filtering based on tx
            if not tx_from and not tx_to and not tx_value:
                asyncio.create_task(on_notification(data, subscription_type, None))  # type: ignore

            # Complex case: filter based on tx
            else:

                async def on_notification_wrapper(data: Any) -> None:
                    try:
                        tx = self.get_tx_from_notification(
                            subscription_type, data, poll_timeout=tx_fetch_timeout
                        )
                        if tx_on_fetch:
                            tx_on_fetch(tx, data)
                    except Exception as e:
                        if tx_on_fetch_error:
                            tx_on_fetch_error(e, data)
                        return
                    if self.filter_tx(tx, tx_from, tx_to, tx_value):
                        await on_notification(data, subscription_type, tx)

                asyncio.create_task(on_notification_wrapper(data))

        # Connect to websocket
        async for ws in connect(self.node_uri):
            try:
                # Subscribe to the notification type
                subscription_id = await subscribe_to_notification(
                    ws, subscription_type, on_subscribe, logs_addresses, logs_topics
                )
                # Main loop
                while True:
                    # Wait for new notifications
                    notification = await asyncio.wait_for(ws.recv(), timeout=ws_timeout)
                    await process_notification(notification, subscription_id)
                    if once:
                        return
            except (
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosedOK,
            ) as e:
                if on_connection_closed:
                    on_connection_closed(e, subscription_type)
                continue

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

    ######################
    # Misc read functions
    ######################

    def get_nonce(self, address: str = None) -> Nonce:
        if not address:
            address = self.user_address
        return self.w3.eth.get_transaction_count(Web3.to_checksum_address(address))

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

    def estimate_gas_for_transfer(self, to: str, value_in_wei: int) -> int:
        """
        Return the gas that would be required to send some ETH
        (expressed in Wei) to an address
        """
        return self.w3.eth.estimate_gas(
            {
                "from": self.user_address,
                "to": to,
                "value": cast(Wei, value_in_wei),
            }
        )

    def get_balance_in_wei(self, address: str = None) -> Wei:
        if not address:
            address = self.user_address
        return self.w3.eth.get_balance(Web3.to_checksum_address(address))

    def get_balance_in_eth(self, address: str = None) -> float:
        if not address:
            address = self.user_address
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
        value_in_wei: int = None,
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

    def clone(self, base: Type[BaseClient] = None) -> BaseClient:
        """
        Return a clone of this client.  Useful to change
        contract address or ABI without having to create
        a new client from scratch.

        You can specify a base class to use for the clone.
        If you do, cast the result to please mypy.
        """
        if base is None:
            base = type(self)

        return base(
            node_uri=self.node_uri,
            chain_id=self.chain_id,
            tx_type=self.tx_type,
            private_key=self.private_key,
            max_priority_fee_in_gwei=self.max_priority_fee_in_gwei,
            upper_limit_for_base_fee_in_gwei=self.upper_limit_for_base_fee_in_gwei,
            contract_address=self.contract_address,
            abi=self.abi,
            middlewares=self.middlewares,
        )

    @staticmethod
    def get_contract(
        address: str,
        provider: Web3,
        abi_file: str = None,
        abi: dict[str, Any] = None,
    ) -> Contract:
        """
        Return a web3 smart contract from address and ABI.
        """
        checksum = Web3.to_checksum_address(address)
        if abi_file:
            abi = BaseClient.get_abi_json(abi_file)
        return provider.eth.contract(address=checksum, abi=abi)

    @classmethod
    def get_abi_json(cls, file_name: str, abi_dir: Union[str, Path] = None) -> Any:
        """Read the ABI from a JSON file.  The file will be searched
        in abi_dir, in self.abi_dir and in the current directory."""

        # Search the file
        file_path = None
        search_paths = []
        if abi_dir:
            search_paths.append(Path(abi_dir) / file_name)
        search_paths.append(Path(cls.abi_dir) / file_name)
        search_paths.append(Path(file_name))

        for path in search_paths:
            if isfile(path):
                file_path = path
                break
        if not file_path:
            raise FileNotFoundError(f"ABI file {file_name} not found")

        # Read the file
        with open(file_path, encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def get_provider(node_uri: str) -> Web3:
        """
        Initialize provider (HTTPS & WS supported).

        TODO: Support autodetection with empty node_uri
        docs here https://web3py.readthedocs.io/en/stable/providers.html#how-automated-detection-works
        """
        if node_uri is None:
            return Web3()
        elif node_uri[0:4] == "http":
            return Web3(Web3.HTTPProvider(node_uri))
        elif node_uri[0:2] == "ws":
            return Web3(Web3.WebsocketProvider(node_uri))
        elif node_uri[-4:] == ".ipc":
            return Web3(Web3.IPCProvider(node_uri))
        else:
            raise ValueError(
                "Node URI not recognized, must start with http, ws or end with .ipc"
            )

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

    @staticmethod
    def filter_tx(
        tx: TxData,
        from_: List[str] = None,
        to: List[str] = None,
        value: Tuple[float, float] = None,
    ) -> bool:
        """Given a transaction, return True if the transaction
        matches the given criteria.

        The criteria can be:
        - from_: list of addresses that the transaction must be sent from
        - to: list of addresses that the transaction must be sent to
        - value: tuple of minimum and maximum value of the transaction (NOT TESTED)

        If a criteria is not specified, it is not checked.
        """
        # Check sender
        if from_ and tx["from"] not in [Web3.to_checksum_address(s) for s in from_]:
            return False
        # Check receiver
        if to and tx["to"] not in [Web3.to_checksum_address(r) for r in to]:
            return False
        # Check value
        if value:
            value_in_eth = Web3.from_wei(tx["value"], "ether")
            if value_in_eth < value[0] or value_in_eth > value[1]:
                return False
        return True
