# @version ^0.3.7

"""
@title Debt minter for USD stablecoins using an ERC20 as collateral
"""

from vyper.interfaces import ERC20

collateral: public(ERC20)

interface Token:
    def balanceOf(_owner: address) -> uint256: view
    def allowance(_owner : address, _spender : address) -> uint256: view
    def mintTo(_to: address, _value: uint256) -> bool: nonpayable
    def burnFrom(_from: address, _value: uint256) -> bool: nonpayable

stablecoin: public(Token)

interface StabilityPool:
    def update_values(_debt_value: uint256, _collateral_value: uint256) -> bool: nonpayable

stability_pool: public(StabilityPool)
stability_pool_address: public(address)

import interfaces.AggregatorV3Interface as AggregatorV3Interface

collateral_price_feed: public(AggregatorV3Interface)

# bps
max_ltv_ratio: public(uint256)
borrow_fee: public(uint256)

lq_reserve_fee: public(uint256)
min_debt_value: public(uint256)

total_collateral: public(uint256)
total_debt: public(uint256)

rewards: public(address)
deployer: public(address)

struct Loan:
    collateral_value: uint256
    debt_value: uint256
    active: bool

user_loans: public(HashMap[address, Loan])


@external
def __init__(
    _stablecoin_address: address,
    _collateral_address: address,
    _stability_pool_address: address,
    _collateral_price_feed_address: address,
    _max_ltv_ratio: uint256,
    _borrow_fee: uint256,
    _lq_reserve_fee: uint256,
    _min_debt_value: uint256
    ):
    self.stablecoin = Token(_stablecoin_address)
    self.collateral = ERC20(_collateral_address)
    self.stability_pool = StabilityPool(_stability_pool_address)
    self.stability_pool_address = _stability_pool_address
    self.collateral_price_feed = AggregatorV3Interface(_collateral_price_feed_address)
    self.max_ltv_ratio = _max_ltv_ratio
    self.borrow_fee = _borrow_fee
    self.lq_reserve_fee = _lq_reserve_fee
    self.min_debt_value = _min_debt_value
    self.rewards = msg.sender
    self.deployer = msg.sender


@internal
def get_collateral_latest_price() -> uint256:
    """
    @notice Returns the current price of ETH on the price oracle
    @return Returns the current price of ETH
    """
    # temporary
    a: uint80 = 0
    price: int256 = 0
    b: uint256 = 0
    c: uint256 = 0
    d: uint80 = 0
    (a, price, b, c, d) = self.collateral_price_feed.latestRoundData()
    return convert(price, uint256)


@internal
def get_lq_price(_collateralValue: uint256, _debtValue: uint256) -> uint256:
    """
    @notice Returns liquidation price depending on collateral and debt given
    @param _collateral_value The amount of collateral
    @param _debt_value The amount of debt
    @return Returns liquidation price
    """
    # Compute USD Value of Collateral
    collateralUsdValue: uint256 = _collateralValue * self.get_collateral_latest_price() / 10 ** 18
    # Compute Collaterization ratio
    collatRatio: uint256 = 10 ** 18 * collateralUsdValue / _debtValue
    # Return Liquidate Price
    return 10 ** 18 * self.get_collateral_latest_price() / collatRatio * 11 / 10


# Open/Close Loans


@external
def open_loan(_collateral_value: uint256, _debt_value: uint256) -> bool:
    """
    @notice Creates a loan that holds collateral and mints stablecoins as debt
    @param _collateral_value The initial amount of collateral for loan
    @param _debt_value The initial amount of debt taken from loan
    @return Success boolean
    """
    _borrow_fee_value: uint256 = _debt_value * self.borrow_fee / 10000
    # Run Checks
    assert self.user_loans[msg.sender].active == False
    assert _debt_value >= self.min_debt_value
    assert self.collateral.balanceOf(msg.sender) >= _collateral_value
    assert self.collateral.allowance(msg.sender, self) >= _collateral_value
    assert self.get_collateral_latest_price() > self.get_lq_price(_collateral_value, _debt_value + _borrow_fee_value + self.lq_reserve_fee)
    # Transfer Collateral
    self.collateral.transferFrom(msg.sender, self, _collateral_value)
    # Mint Stablecoins
    self.stablecoin.mintTo(msg.sender, _debt_value)
    self.stablecoin.mintTo(self.rewards, _borrow_fee_value)
    # Update Values
    self.total_collateral += _collateral_value
    self.total_debt += _debt_value + _borrow_fee_value + self.lq_reserve_fee
    # Initiate Loan
    self.user_loans[msg.sender] = Loan({collateral_value: _collateral_value, debt_value: _debt_value + _borrow_fee_value + self.lq_reserve_fee, active: True})
    # Return Success
    return True


@external
def close_loan() -> bool:
    """
    @notice Closes a loan by burning the debt and transfering back the collateral
    @return Success boolean
    """
    # Run Checks
    assert self.user_loans[msg.sender].active == True
    assert self.stablecoin.balanceOf(msg.sender) >= self.user_loans[msg.sender].debt_value - self.lq_reserve_fee
    # Burn Stablecoins
    self.stablecoin.burnFrom(msg.sender, self.user_loans[msg.sender].debt_value - self.lq_reserve_fee)
    # Transfer Collateral
    self.collateral.transfer(msg.sender, self.user_loans[msg.sender].collateral_value)
    # Update Values
    self.total_collateral -= self.user_loans[msg.sender].collateral_value
    self.total_debt -= self.user_loans[msg.sender].debt_value
    # Reset Loan
    self.user_loans[msg.sender] = Loan({collateral_value: 0, debt_value: 0, active: False})
    # Return Success
    return True


# Collateral


@external
def deposit_collateral(_value: uint256) -> bool:
    """
    @notice Deposit Collateral into a loan
    @param _value The amount of collateral to deposit
    @return Success boolean
    """
    # Run Checks
    assert _value > 0
    assert self.user_loans[msg.sender].active == True
    assert self.collateral.balanceOf(msg.sender) >= _value
    assert self.collateral.allowance(msg.sender, self) >= _value
    # Transfer Collateral
    self.collateral.transferFrom(msg.sender, self, _value)
    # Update Values
    self.user_loans[msg.sender].collateral_value += _value
    self.total_collateral += _value
    # Return Success
    return True


@external
def withdraw_collateral(_value: uint256) -> bool:
    """
    @notice Withdraw Collateral from loan
    @param _value The amount of collateral to withdraw
    @return Success boolean
    """
    # Run Checks
    assert _value > 0
    assert self.user_loans[msg.sender].active == True
    assert self.get_collateral_latest_price() > self.get_lq_price(self.user_loans[msg.sender].collateral_value - _value, self.user_loans[msg.sender].debt_value)
    # Transfer Collateral
    self.collateral.transfer(msg.sender, _value)
    # Update Values
    self.user_loans[msg.sender].collateral_value -= _value
    self.total_collateral -= _value
    # Return Success
    return True


# Debt


@external
def borrow_stablecoin(_value: uint256) -> bool:
    """
    @notice Mints debt from loan as stablecoins
    @param _value The amount of stablecoins to borrow
    @return Success boolean
    """
    # Run Checks
    assert _value > 0
    assert self.user_loans[msg.sender].active == True
    assert self.get_collateral_latest_price() > self.get_lq_price(self.user_loans[msg.sender].collateral_value, self.user_loans[msg.sender].debt_value - _value)
    # Mint Stablecoins
    _borrow_fee_value: uint256 = _value * self.borrow_fee / 10000
    self.stablecoin.mintTo(msg.sender, _value)
    self.stablecoin.mintTo(self.rewards, _borrow_fee_value)
    # Update Values
    self.user_loans[msg.sender].debt_value += _value + _borrow_fee_value
    self.total_debt += _value + _borrow_fee_value
    # Return Success
    return True


@external
def repay_stablecoin(_value: uint256) -> bool:
    """
    @notice Repay debt from loan as stablecoins
    @param _value The amount of stablecoins to repay debt
    @return Success boolean
    """
    # Run Checks
    assert _value > 0
    assert self.user_loans[msg.sender].active == True
    assert self.stablecoin.balanceOf(msg.sender) >= _value
    assert self.user_loans[msg.sender].debt_value - _value >= self.min_debt_value + self.lq_reserve_fee
    # Burn Stablecoins
    self.stablecoin.burnFrom(msg.sender, _value)
    # Update Values
    self.user_loans[msg.sender].debt_value -= _value
    self.total_debt -= _value
    # Return Success
    return True


# Liquidation


@external
def liquidate(_user: address) -> bool:
    """
    @notice Liquidate a user that has a risky loan
    @param _user The address with loan to liquidate
    @return Success boolean
    """
    # Run Checks
    assert self.user_loans[_user].active == True
    assert self.stablecoin.balanceOf(self.stability_pool_address) >= self.user_loans[_user].debt_value
    assert self.get_lq_price(self.user_loans[_user].collateral_value, self.user_loans[_user].debt_value) >= self.get_collateral_latest_price()
    # Burn Stablecoins
    self.stablecoin.burnFrom(self.stability_pool_address, self.user_loans[_user].debt_value)
    # Transfer Collateral
    self.collateral.transfer(self.stability_pool_address, self.user_loans[_user].collateral_value * 199 / 200)
    self.collateral.transfer(msg.sender, self.user_loans[_user].collateral_value / 200)
    # Mint Stablecoins
    self.stablecoin.mintTo(msg.sender, self.lq_reserve_fee)
    # Update Values
    self.total_collateral -= self.user_loans[_user].collateral_value
    self.total_debt -= self.user_loans[_user].debt_value
    # Update Stability Pool Values
    self.stability_pool.update_values(self.user_loans[_user].debt_value, self.user_loans[_user].collateral_value * 199 / 200)
    # Reset Loan
    self.user_loans[_user] = Loan({collateral_value: 0, debt_value: 0, active: False})
    # Return Success
    return True


# Deployer


@external
def set_rewards(_to: address):
    """
    @notice Changes the reward's address to another address
    @param _to The address to set as rewards
    """
    # Run Checks
    assert self.deployer == msg.sender
    # Update Rewards
    self.rewards = _to