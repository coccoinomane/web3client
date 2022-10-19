class Web3ClientException(BaseException):
    pass


class MissingParameter(Web3ClientException):
    pass


class TransactionTooExpensive(Web3ClientException):
    pass


class NetworkNotFound(Web3ClientException):
    pass


class Erc20TokenNotFound(Web3ClientException):
    pass


class Erc20TokenNotUnique(Web3ClientException):
    pass
