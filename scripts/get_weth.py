from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def get_weth():
  """
  mints weth by depositing eth
  
  # ABI
  # ADDRESS
  """
  # get an account and an address
  account = get_account()
  # get the abi,
  weth = interface.IWeth(
      config["networks"][network.show_active()]["weth_token"])
  # you can use the get contract function or get the contract address if a mainnet fork is to be used or deploy mocks if local blockchain enviroments is to be used but since we're not deploying mocks here, you can just use the config file directly
  tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
  tx.wait(1)
  print("recieved .1eth ")


def main():
  get_weth()
