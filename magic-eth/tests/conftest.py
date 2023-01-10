#!/usr/bin/python3

import pytest

# . This runs before ALL tests

# Temp ETH Price Oracle Deployer


@pytest.fixture
def eth_oracle(MockPriceOracle, accounts):
    eth_oracle = MockPriceOracle.deploy({"from": accounts[0]})
    price = 1e21
    eth_oracle.setCurrentPrice(price, {"from": eth_oracle.deployer()})
    return eth_oracle


# ETH Wand Deployer


@pytest.fixture
def token(Token, accounts):
    return Token.deploy("Test ETH", "tETH", 18, 1e21, {"from": accounts[0]})


@pytest.fixture
def wand(token, SwapWand, accounts):
    wand = SwapWand.deploy(token, {"from": accounts[0]})
    token.set_wand(wand, {"from": token.deployer()})
    return wand


# USD Wand Deployer


@pytest.fixture
def usd_token(Token, accounts):
    return Token.deploy("Test USD", "tUSD", 18, 1e24, {'from': accounts[0]})


@pytest.fixture
def usd_stability_pool(StabilityPool, usd_token, token, accounts):
    return StabilityPool.deploy(usd_token, token, 2e21, {'from': accounts[0]})


@pytest.fixture
def usd_wand(BorrowWand, usd_token, token, usd_stability_pool, eth_oracle, accounts):
    usd_wand = BorrowWand.deploy(usd_token, token, usd_stability_pool, eth_oracle, 9000, 50, 2e20, 2e21, {"from": accounts[0]})
    usd_wand.set_rewards(usd_wand, {"from": usd_wand.deployer()})
    usd_token.set_wand(usd_wand, {"from": usd_token.deployer()})
    usd_stability_pool.set_wand(usd_wand, {"from": usd_stability_pool.deployer()})
    return usd_wand
