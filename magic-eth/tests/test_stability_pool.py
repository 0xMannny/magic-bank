import brownie
from brownie import *


def test_pool_deployed(usd_stability_pool):
    assert hasattr(usd_stability_pool, "open_deposit")


def test_open_deposit(usd_token, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount


def test__open_deposit_below_min(usd_token, usd_stability_pool, accounts):
    amount = 10 ** 18

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_stability_pool.open_deposit(amount, {"from": accounts[0]})


def test_pool_deposit_and_withdraw_no_rewards(usd_token, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    usd_stability_pool.close_deposit({"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal


def test_pool_deposit_and_withdraw_with_rewards(token, usd_token, usd_wand, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])
    init_bal_2 = token.balanceOf(accounts[0])

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    usd_stability_pool.update_values(amount / 2, amount / 2, {"from": usd_wand})
    # Simulate Transfer of Collateral
    token.mintTo(usd_stability_pool, amount / 2, {"from": token.wand()})
    usd_stability_pool.close_deposit({"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount / 2
    assert token.balanceOf(accounts[0]) == init_bal_2 + amount / 2


def test_pool_deposit_and_withdraw_with_rewards(token, usd_token, usd_wand, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])
    init_bal_2 = token.balanceOf(accounts[0])

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    usd_stability_pool.update_values(amount, amount, {"from": usd_wand})
    # Simulate Transfer of Collateral
    token.mintTo(usd_stability_pool, amount, {"from": token.wand()})
    usd_stability_pool.close_deposit({"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount
    assert token.balanceOf(accounts[0]) == init_bal_2 + amount



def test_cannot_open_two_deposits(usd_token, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    
    usd_token.approve(usd_stability_pool, amount * 2, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    with brownie.reverts():
        usd_stability_pool.open_deposit(amount, {"from": accounts[0]})


def test_open_deposit_after_close_deposit(usd_token, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])
    
    usd_token.approve(usd_stability_pool, amount * 2, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    usd_stability_pool.close_deposit({"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount


# set_wand Function


def test_deployer_can_set_wand(usd_stability_pool, accounts):
    assert usd_stability_pool.wand() != accounts[1]

    usd_stability_pool.set_wand(accounts[1], {"from": usd_stability_pool.deployer()})
    assert usd_stability_pool.wand() == accounts[1]


def test_nondeployer_cannot_set_wand(usd_stability_pool, accounts):
    hacker = accounts[1]
    assert hacker != usd_stability_pool.deployer()

    with brownie.reverts():
        usd_stability_pool.set_wand(hacker, {"from": hacker})


# update_values Function


def test_wand_can_update_values(usd_token, usd_wand, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    init_bal = usd_token.balanceOf(accounts[0])

    usd_token.approve(usd_stability_pool, amount, {"from": accounts[0]})
    usd_stability_pool.open_deposit(amount, {"from": accounts[0]})
    usd_stability_pool.update_values(amount, 0, {"from": usd_wand})
    usd_stability_pool.close_deposit({"from": accounts[0]})
    assert usd_token.balanceOf(accounts[0]) == init_bal - amount


def test_nonwand_cannot_update_values(usd_wand, usd_stability_pool, accounts):
    amount = 10 ** 18 * 2000
    hacker = accounts[1]
    assert hacker != usd_stability_pool.wand()

    with brownie.reverts():
        usd_stability_pool.update_values(amount, amount, {"from": hacker})