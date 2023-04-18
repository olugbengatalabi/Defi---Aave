from brownie import network, accounts, config
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "maiinnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    'development', "ganache-local", "ganache-locale", "mainnet-fork"]

def get_account(index=None, id=None):
  print("get account called")
  if index:
    return accounts[index]
  if id:
    return accounts.load(id)

  if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
    print("network in local blockchain enviroment")
    return accounts[0]
  return accounts.add(config["wallets"]["from_key"])
