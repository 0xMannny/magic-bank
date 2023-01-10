import brownie
from brownie import *


def test_wand_deployed(wand):
    assert hasattr(wand, "mint")


# mint Function


def test_token_balance_updates_on_mint_with_no_mint_fee(token, wand, accounts):
    amount = 1e18
    init_bal = token.balanceOf(accounts[0])

    wand.mint({"from": accounts[0], "value": "1 ether"})
    assert token.balanceOf(accounts[0]) == init_bal + amount


def test_token_balance_updates_on_mint_with_mint_fee(token, wand, accounts):
    amount = 1e18
    init_bal = token.balanceOf(accounts[0])

    wand.set_rewards(accounts[1], {"from": token.deployer()})
    wand.mint({"from": accounts[0], "value": "1 ether"})
    assert token.balanceOf(accounts[0]) == init_bal + amount * 199 / 200


def test_token_total_supply_updates_on_mint(token, wand, accounts):
    amount = 1e18
    init_supply = token.totalSupply()

    wand.mint({"from": accounts[0], "value": "1 ether"})
    assert token.totalSupply() == init_supply + amount


def test_token_mint_with_0_value(wand, accounts):
    with brownie.reverts():
        wand.mint({"from": accounts[0], "value": "0 ether"})


# redeem Function


def test_token_balances_update_on_redeem(token, wand, accounts):
    init_bal = token.balanceOf(accounts[0])

    wand.mint({"from": accounts[0], "value": "1 ether"})
    wand.redeem(1e18, {"from": accounts[0]})
    assert token.balanceOf(accounts[0]) == init_bal


def test_token_total_supply_updates_on_mint_and_redeem(token, wand, accounts):
    init_supply = token.totalSupply()

    wand.mint({"from": accounts[0], "value": "1 ether"})
    wand.redeem(1e18, {"from": accounts[0]})
    assert token.totalSupply() == init_supply


def test_token_redeem_with_0_value(wand, accounts):
    amount = 0

    wand.mint({"from": accounts[0], "value": "1 ether"})
    with brownie.reverts():
        wand.redeem(amount * 2, {"from": accounts[0]})


def test_token_redeem_with_insufficient_balance(wand, accounts):
    amount = 1e18

    wand.mint({"from": accounts[0], "value": "1 ether"})
    with brownie.reverts():
        wand.redeem(amount * 2, {"from": accounts[0]})


# set_wand Function


def test_deployer_can_set_wand(token, accounts):
    assert token.wand() != accounts[1]

    token.set_wand(accounts[1], {"from": token.deployer()})
    assert token.wand() == accounts[1]


def test_nondeployer_cannot_set_wand(token, accounts):
    hacker = accounts[1]
    assert hacker != token.deployer()

    with brownie.reverts():
        token.set_wand(hacker, {"from": hacker})


# mintTo Function


def test_nonwand_cannot_mint(token, accounts):
    hacker = accounts[1]
    assert hacker != token.wand()

    with brownie.reverts():
        token.mintTo(hacker, 1e18, {"from": hacker})