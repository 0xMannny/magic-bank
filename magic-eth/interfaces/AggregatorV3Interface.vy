# @version ^0.3.3


@view
@external
def decimals() -> uint8:
    return 0


@view
@external
def description() -> String[1000]:
    return ""


@view
@external
def version() -> uint256:
    return 0


@view
@external
def getRoundData(_roundId: uint80) -> (uint80, int256, uint256, uint256, uint80):
    return (0, 0, 0, 0, 0)


@view
@external
def latestRoundData() -> (uint80, int256, uint256, uint256, uint80):
    return (0, 0, 0, 0, 0)