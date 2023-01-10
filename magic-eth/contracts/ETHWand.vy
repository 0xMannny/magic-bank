# @version ^0.3.7

"""
@title Minter for ETH stablecoin using ETH as collateral
"""

interface Token:
    def balanceOf(_owner: address) -> uint256: view
    def mintTo(_to: address, _value: uint256) -> bool: nonpayable
    def burnFrom(_from: address, _value: uint256) -> bool: nonpayable

stablecoin: public(Token)

collateral_value: public(uint256)

rewards: public(address)
deployer: public(address)


@external
def __init__(_stablecoin_address: address):
    self.stablecoin = Token(_stablecoin_address)
    self.rewards = self
    self.deployer = msg.sender


@external
@payable
def mint() -> bool:
    """
    @notice Mints a quantity of stablecoins for a quantity of ETH
    @return Success boolean
    """
    # Run Checks
    assert msg.value > 0
    # If Fees Are Enabled
    if self.rewards != self:
        # Mint Stablecoins
        self.stablecoin.mintTo(msg.sender, msg.value * 199 / 200)
        self.stablecoin.mintTo(self.rewards, msg.value / 200)
    # If Fees Are Disabled
    else:
        # Mint Stablecoins
        self.stablecoin.mintTo(msg.sender, msg.value)
    # Update Values
    self.collateral_value += msg.value
    # Return Success
    return True


@external
def redeem(_value: uint256) -> bool:
    """
    @notice Redeems a quantity of ETH for a quantity of stablecoins
    @param _value The amount of tokens to redeem
    @return Success boolean
    """
    # Run Checks
    assert _value > 0
    assert self.stablecoin.balanceOf(msg.sender) >= _value
    # Burn Stablecoins
    self.stablecoin.burnFrom(msg.sender, _value)
    # Send Equal Amount Of ETH
    send(msg.sender, _value)
    # Update Values
    self.collateral_value -= _value
    # Return Success
    return True


@external
def set_rewards(_to: address):
    """
    @notice Changes the reward's address to another address
    @param _to The address to set as rewards
    """
    # Run Checks
    assert self.deployer == msg.sender
    # Update Values
    self.rewards = _to