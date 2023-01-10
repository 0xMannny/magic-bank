import brownie
from brownie import *


def test_wand_deployed(usd_wand):
    assert hasattr(usd_wand, "open_loan")


# open_loan Function


def test_collateral_balance_updates_on_open_loan(token, usd_wand, accounts):
    amount = 1e20
    init_bal = token.balanceOf(accounts[0])
    init_bal2 = token.balanceOf(usd_wand)

    token.approve(usd_wand, amount, {"from": accounts[0]})
    usd_wand.open_loan(amount, 2e21, {"from": accounts[0]})
    assert token.balanceOf(accounts[0]) == init_bal - amount
    assert token.balanceOf(usd_wand) == init_bal2 + amount


def test_stablecoin_balance_updates_on_open_loan(token, usd_token, usd_wand, accounts):
    amount = 2e21
    init_bal = usd_token.balanceOf(accounts[0])

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, amount, {"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal + amount


def test_total_supply_of_stablecoin_updates_on_open_loan(token, usd_token, usd_wand, accounts):
    amount = 2e21

    init_supply = usd_token.totalSupply()

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, amount, {"from": accounts[0]})
    assert usd_token.totalSupply() == init_supply + (amount * 201 / 200)


def test_contract_values_update_on_open_loan(token, usd_token, usd_wand, eth_oracle, accounts):
    # Not Finished
    pass


def test_open_loan_with_active_loan(token, usd_wand, accounts):
    amount = 1e20

    token.approve(usd_wand, amount * 2, {"from": accounts[0]})
    usd_wand.open_loan(amount, 2e21, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.open_loan(amount, 2e21, {"from": accounts[0]})


def test_open_loan_below_min_debt(token, usd_wand, accounts):
    amount = 1

    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.open_loan(1e21, amount, {"from": accounts[0]})


def test_open_loan_with_insufficent_balance(token, usd_wand, accounts):
    amount = 1e21

    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.open_loan(amount * 2, 2e21, {"from": accounts[0]})


def test_open_loan_without_approval(token, usd_wand, accounts):
    amount = 1e20

    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.open_loan(amount * 2, 2e21, {"from": accounts[0]})


def test_open_loan_below_lq_price(token, usd_wand, accounts):
    amount = 1e18

    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.open_loan(amount, 2e21, {"from": accounts[0]})


# close_loan Function


def test_open_loan_after_close_loan(token, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.set_rewards(accounts[0], {"from": usd_wand.deployer()})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})
    usd_wand.close_loan({"from": accounts[0]})

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})


def test_collateral_balance_updates_on_close_loan(token, usd_wand, accounts):
    init_bal = token.balanceOf(accounts[0])

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.set_rewards(accounts[0], {"from": usd_wand.deployer()})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})
    usd_wand.close_loan({"from": accounts[0]})
    assert token.balanceOf(accounts[0]) == init_bal
    assert token.balanceOf(usd_wand) == 0


def test_stablecoin_balance_updates_on_close_loan(token, usd_token, usd_wand, accounts):
    init_bal = usd_token.balanceOf(accounts[0])

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.set_rewards(accounts[0], {"from": usd_wand.deployer()})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})
    usd_wand.close_loan({"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal


def test_total_supply_of_stablecoin_updates_on_close_loan(token, usd_token, usd_wand, accounts):
    init_supply = usd_token.totalSupply()

    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.set_rewards(accounts[0], {"from": usd_wand.deployer()})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})
    usd_wand.close_loan({"from": accounts[0]})
    assert usd_token.totalSupply() == init_supply


def test_contract_values_update_on_close_loan(token, usd_token, usd_wand, eth_oracle, accounts):
    # Not Finished
    pass


def test_close_loan_without_active_loan(usd_wand, accounts):
    with brownie.reverts():
        usd_wand.close_loan({"from": accounts[0]})


def test_close_loan_with_insufficient_balance(token, usd_token, usd_wand, accounts):
    amount = 1e21

    usd_token.burnFrom(accounts[0], usd_token.balanceOf(accounts[0]), {"from": usd_wand})
    token.approve(usd_wand, amount, {"from": accounts[0]})
    usd_wand.open_loan(amount, 2e21, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.close_loan({"from": accounts[0]})


# deposit_collateral Function


def test_collateral_balance_updates_on_collateral_deposit(token, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})

    amount = 1e18
    init_bal = token.balanceOf(accounts[0])
    init_bal2 = token.balanceOf(usd_wand)

    token.approve(usd_wand, amount, {"from": accounts[0]})
    usd_wand.deposit_collateral(amount, {"from": accounts[0]})
    assert token.balanceOf(accounts[0]) == init_bal - amount
    assert token.balanceOf(usd_wand) == init_bal2 + amount


def test_contract_values_update_on_collateral_deposit(token, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})

    # Not Finished


def test_collateral_deposit_with_0_value(token, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})

    token.approve(usd_wand, 1e18, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.deposit_collateral(0, {"from": accounts[0]})


def test_collateral_deposit_without_active_loan(token, usd_wand, accounts):
    amount = 1e18

    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.deposit_collateral(amount, {"from": accounts[0]})


def test_collateral_deposit_with_insufficient_balance(token, wand, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})

    amount = 1e18

    token.burnFrom(accounts[0], token.balanceOf(accounts[0]) - amount, {"from": wand})
    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.deposit_collateral(amount * 2, {"from": accounts[0]})


def test_collateral_deposit_without_approval(token, usd_wand, accounts):
    token.approve(usd_wand, 1e20, {"from": accounts[0]})
    usd_wand.open_loan(1e20, 2e21, {"from": accounts[0]})

    amount = 1e18

    token.approve(usd_wand, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_wand.deposit_collateral(amount * 2, {"from": accounts[0]})


# withdraw_collateral Function


def test_collateral_balance_updates_on_collateral_withdraw(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    amount = 1e18
    init_bal = token.balanceOf(accounts[0])
    init_bal2 = token.balanceOf(usd_wand)

    usd_wand.withdraw_collateral(amount, {"from": accounts[0]})
    assert token.balanceOf(accounts[0]) == init_bal + amount
    assert token.balanceOf(usd_wand) ==  init_bal2 - amount


def test_contract_values_update_on_collateral_withdraw(token, usd_token, usd_wand, eth_oracle, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    # Not Finished


def test_collateral_withdraw_with_0_value(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    with brownie.reverts():
        usd_wand.withdraw_collateral(0, {"from": accounts[0]})


def test_collateral_withdraw_without_active_loan(usd_wand, accounts):
    amount = 1e18

    with brownie.reverts():
        usd_wand.withdraw_collateral(amount, {"from": accounts[0]})


def test_collateral_withdraw_below_lq_price(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    amount = 999e18

    with brownie.reverts():
        usd_wand.withdraw_collateral(amount, {"from": accounts[0]})


# borrow_stablecoin Function


def test_stablecoin_balance_updates_on_stablecoin_borrow(token, usd_token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    amount = 1e21
    init_bal = usd_token.balanceOf(accounts[0])

    usd_wand.borrow_stablecoin(amount, {"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal + amount


def test_contract_values_update_on_stablecoin_borrow(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    # Not Finished


def test_stablecoin_borrow_with_0_value(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    with brownie.reverts():
        usd_wand.borrow_stablecoin(0, {"from": accounts[0]})


def test_stablecoin_borrow_without_active_loan(usd_wand, accounts):
    amount = 1e21

    with brownie.reverts():
        usd_wand.borrow_stablecoin(amount, {"from": accounts[0]})


def test_stablecoin_borrow_below_lq_price(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    amount = 1e30

    with brownie.reverts():
        usd_wand.borrow_stablecoin(amount, {"from": accounts[0]})


# repay_stablecoin Function


def test_stablecoin_balance_updates_on_stablecoin_repay(token, usd_token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 5e21, {"from": accounts[0]})

    amount = 1e21
    init_bal = usd_token.balanceOf(accounts[0])

    usd_wand.repay_stablecoin(amount, {"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount


def test_contract_values_update_on_stablecoin_repay(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 5e21, {"from": accounts[0]})

    # Not Finished


def test_stablecoin_repay_with_0_value(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 5e21, {"from": accounts[0]})

    with brownie.reverts():
        usd_wand.repay_stablecoin(0, {"from": accounts[0]})


def test_stablecoin_repay_without_active_loan(usd_wand, accounts):
    amount = 1e21

    with brownie.reverts():
        usd_wand.repay_stablecoin(amount, {"from": accounts[0]})


def test_stablecoin_repay_with_insufficient_balance(token, usd_token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 5e21, {"from": accounts[0]})

    amount = 1e21

    usd_token.burnFrom(accounts[0], usd_token.balanceOf(accounts[0]), {"from": usd_wand})
    with brownie.reverts():
        usd_wand.repay_stablecoin(amount, {"from": accounts[0]})


def test_stablecoin_repay_below_min_borrow_amount(token, usd_wand, accounts):
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 5e21, {"from": accounts[0]})

    amount = 4e21

    with brownie.reverts():
        usd_wand.repay_stablecoin(amount, {"from": accounts[0]})


# liquidate Function


def test_collateral_balance_updates_on_liquidation(token, usd_token, usd_wand, usd_stability_pool, eth_oracle, accounts):
    # Account 0 has Loan, 1 has deposit in Stability Pool, and 2 is the liquidator of 0
    amount = 1e21

    token.approve(usd_wand, amount, {"from": accounts[0]})
    usd_wand.open_loan(amount, 5e21, {"from": accounts[0]})

    usd_token.mintTo(accounts[1], 1e24, {"from": usd_wand})
    usd_token.approve(usd_stability_pool, 1e24, {"from": accounts[1]})
    usd_stability_pool.open_deposit(1e24, {"from": accounts[1]})

    init_bal = token.balanceOf(usd_wand)
    init_bal2 = token.balanceOf(usd_stability_pool)
    init_bal3 = token.balanceOf(accounts[2])

    eth_oracle.setCurrentPrice(1e18, {"from": eth_oracle.deployer()})
    usd_wand.liquidate(accounts[0], {"from": accounts[2]})
    assert token.balanceOf(usd_wand) == init_bal - amount
    assert token.balanceOf(usd_stability_pool) == init_bal2 + (amount * 199 / 200)
    assert token.balanceOf(accounts[2]) == init_bal3 + (amount / 200)



def test_stablecoin_balance_updates_on_liquidation(token, usd_token, usd_wand, usd_stability_pool, eth_oracle, accounts):
    # Account 0 has Loan, 1 has deposit in Stability Pool, and 2 is the liquidator of 0
    amount = 2e21

    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, amount, {"from": accounts[0]})

    usd_token.mintTo(accounts[1], 1e24, {"from": usd_wand})
    usd_token.approve(usd_stability_pool, 1e24, {"from": accounts[1]})
    usd_stability_pool.open_deposit(1e24, {"from": accounts[1]})

    init_bal = usd_token.balanceOf(usd_stability_pool)
    init_bal2 = usd_token.balanceOf(accounts[2])

    eth_oracle.setCurrentPrice(1e18, {"from": eth_oracle.deployer()})
    usd_wand.liquidate(accounts[0], {"from": accounts[2]})
    assert usd_token.balanceOf(usd_stability_pool) == init_bal - (amount * 201 / 200) - 2e20
    assert usd_token.balanceOf(accounts[2]) == init_bal2 + 2e20


def test_contract_values_update_on_liquidation(token, usd_token, usd_wand, eth_oracle, accounts):
    # Not Finished
    pass


def test_liquidaiton_without_active_loan(usd_wand, accounts):
    # Account 0 has Loan and 1 is the liquidator
    with brownie.reverts():
        usd_wand.liquidate(accounts[0], {"from": accounts[1]})


def test_liquidation_with_insufficient_stability_pool_balance(token, usd_wand, accounts):
    # Account 0 has Loan and 1 is the liquidator
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    with brownie.reverts():
        usd_wand.liquidate(accounts[0], {"from": accounts[1]})


def test_liquidation_above_lq_price(token, usd_token, usd_wand, usd_stability_pool, accounts):
    # Account 0 has Loan, 1 has deposit in Stability Pool, and 2 is the liquidator of 0
    token.approve(usd_wand, 1e21, {"from": accounts[0]})
    usd_wand.open_loan(1e21, 2e21, {"from": accounts[0]})

    usd_token.mintTo(accounts[1], 1e24, {"from": usd_wand})
    usd_token.approve(usd_stability_pool, 1e24, {"from": accounts[1]})
    usd_stability_pool.open_deposit(1e24, {"from": accounts[1]})

    with brownie.reverts():
        usd_wand.liquidate(accounts[0], {"from": accounts[2]})


# set_rewards Function


def test_deployer_can_set_rewards(usd_wand, accounts):
    assert usd_wand.rewards() != accounts[1]

    usd_wand.set_rewards(accounts[1], {"from": usd_wand.deployer()})
    assert usd_wand.rewards() == accounts[1]


def test_nondeployer_cannot_set_rewards(usd_wand, accounts):
    hacker = accounts[1]
    assert hacker != usd_wand.deployer()

    with brownie.reverts():
        usd_wand.set_rewards(hacker, {"from": hacker})