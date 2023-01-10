# @version ^0.3.3

price: public(int256)
deployer: public(address)


@external
def __init__():
    self.deployer = msg.sender


@view
@external
def decimals() -> uint8:
    return 18


@view
@external
def description() -> String[1000]:
    return "Test ETH Oracle"


@view
@external
def version() -> uint256:
    return 1


@view
@external
def getRoundData(_roundId: uint80) -> (uint80, int256, uint256, uint256, uint80):
    return (0, self.price, 0, 0, 0)


@view
@external
def latestRoundData() -> (uint80, int256, uint256, uint256, uint80):
    return (0, self.price, 0, 0, 0)


@external
def setCurrentPrice(_price: int256):
    assert self.deployer == msg.sender
    self.price = _price
