# @version ^0.3.7

"""
@title Stability Pool to provide liquidity for liquidations
"""

from vyper.interfaces import ERC20

wand: public(address)
stablecoin: public(ERC20)
collateral: public(ERC20)

total_stablecoin: public(uint256)

struct Deposit:
    depositer: address
    active: bool
    index: uint256
    stablecoin_value: uint256
    collateral_value: uint256

deposit_list: public(DynArray[Deposit, 10 ** 18])
deposits: public(HashMap[address, Deposit])

start_index: public(uint256)
min_deposit_value: public(uint256)

deployer: public(address)


@external
def __init__(_stablecoin_address: address, _collateral_address: address, _min_deposit_value: uint256):
    self.wand = msg.sender
    self.stablecoin = ERC20(_stablecoin_address)
    self.collateral = ERC20(_collateral_address)
    self.deposit_list = []
    self.min_deposit_value = _min_deposit_value
    self.deployer = msg.sender


# Open/Close Deposits


@external
def open_deposit(_value: uint256) -> bool:
    """
    @notice Creates a deposit by depositing stablecoins
    @param _value The amount of stablecoins to deposit
    @return Success boolean
    """
    # Run Checks
    assert _value >= self.min_deposit_value
    assert self.deposits[msg.sender].active == False
    assert self.stablecoin.balanceOf(msg.sender) >= _value
    assert self.stablecoin.allowance(msg.sender, self) >= _value
    # Transfer Stablecoins
    self.stablecoin.transferFrom(msg.sender, self, _value)
    # Update Values
    self.total_stablecoin += _value
    # Create Deposit
    new_Deposit: Deposit = Deposit({depositer: msg.sender, active: True, index: len(self.deposit_list), stablecoin_value: _value, collateral_value: 0})
    self.deposits[msg.sender] = new_Deposit
    self.deposit_list.append(new_Deposit)
    # Return Success
    return True


@external
def close_deposit() -> bool:
    """
    @notice Closes a deposit and transfers remaining stablecoins and gained collateral
    @return Success boolean
    """
    # Run Checks
    assert self.deposits[msg.sender].active == True
    # Transfer Stablecoins, If Any
    if self.deposits[msg.sender].stablecoin_value > 0:
        self.stablecoin.transfer(msg.sender, self.deposits[msg.sender].stablecoin_value)
    # Transfer Collateral, If Any
    if self.deposits[msg.sender].collateral_value > 0:
        self.collateral.transfer(msg.sender, self.deposits[msg.sender].collateral_value)
    # Update Values
    self.total_stablecoin -= self.deposits[msg.sender].stablecoin_value
    # Reset Deposit
    old_index: uint256 = self.deposits[msg.sender].index
    new_Deposit: Deposit = Deposit({depositer: empty(address), active: False, index: old_index, stablecoin_value: 0, collateral_value: 0})
    self.deposits[msg.sender] = new_Deposit
    self.deposit_list[old_index] = new_Deposit
    # Return Success
    return True


# Update Values of Deposits During A Liquidation


@external
def update_values(_debt_value: uint256, _collateral_value: uint256) -> bool:
    """
    @notice Updates values of used deposits during a liquidation
    @param _debt_value The amount of debt needed from deposits
    @param _collateral_value The amount of collateral gained from paying off debt
    @return Success boolean
    """
    # Run Checks
    assert msg.sender == self.wand
    # Initialize Variables
    debt_payed: uint256 = 0
    deposits_emptied: uint256 = 0
    # Start Updating Deposits To Clear Debt
    for i in range(self.start_index, self.start_index + 10 ** 18):
        deposit: Deposit = self.deposit_list[i]
        # If Deposit Has No Stablecoins, Then Move On To Next Deposit
        if deposit.stablecoin_value == 0:
            deposits_emptied += 1
            continue
        # Calculate Remaining Debt
        remaining_debt: uint256 = _debt_value - debt_payed
        # If Deposit Has Less Than Or Equal To Stablecoins Needed
        if remaining_debt >= deposit.stablecoin_value:
            # Update Values
            debt_payed += deposit.stablecoin_value
            deposits_emptied += 1
            # Update Deposit List
            self.deposit_list[i].stablecoin_value = 0
            # Update Gained Collateral
            self.deposit_list[i].collateral_value = deposit.stablecoin_value * _collateral_value / _debt_value
            # Update Deposit
            self.deposits[deposit.depositer].stablecoin_value = 0
            # Update Gained Collateral
            self.deposits[deposit.depositer].collateral_value = deposit.stablecoin_value * _collateral_value / _debt_value
            # If Deposit Is Emptied And Clears Remaining Debt, Then Stop For Loop
            if remaining_debt == deposit.stablecoin_value:
                break
        # If Deposit Has More Stablecoins Than Needed
        else:
            # Update Deposit List
            self.deposit_list[i].stablecoin_value -= remaining_debt
            # Update Gained Collateral
            self.deposit_list[i].collateral_value = remaining_debt * _collateral_value / _debt_value
            # Update Deposit
            self.deposits[deposit.depositer].stablecoin_value -= remaining_debt
            # Update Gained Collateral
            self.deposits[deposit.depositer].collateral_value = remaining_debt * _collateral_value / _debt_value
            # Stop For Loop, Since Debt Is Cleared
            break
    # Increase Start Index Pass Emptied Deposits
    self.start_index += deposits_emptied
    # Update Stablecoin Total
    self.total_stablecoin -= _debt_value
    # Return Success
    return True


# Deployer


@external
def set_wand(_to: address):
    """
    @notice Changes the wand's address to another address
    @param _to The address to set as wand
    """
    # Run Checks
    assert self.deployer == msg.sender
    # Update Wand
    self.wand = _to