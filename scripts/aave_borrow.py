from brownie import network, config, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3


amount = Web3.toWei(0.1, "ether")
# 0.1
token_adress = config["networks"][network.show_active()]["dai_token_address"]
def get_lending_pool():
  lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(config["networks"][network.show_active()]["lending_pool_addresses_provider"])
  lending_pool_address = lending_pool_addresses_provider.getLendingPool()
  # this gets us the address
  # the abi comes from the compilation of the interface
  lending_pool = interface.ILendingPool(lending_pool_address)
  return lending_pool
  
# address and abi needed.. the abi is gotten from the interface while the address is gotten from the aave  protocol address provider (lendingpool addresses provider)

def approve_erc20(amount, spender, erc20_address, account):
  print("Approving Erc 20")
  erc20 = interface.IERC20(erc20_address)
  tx = erc20.approve(spender, amount, {"from": account})
  tx.wait(1)
  print("approved")
  # abi 
  # address
  
def get_borrowable_data(lending_pool, account):
  (
      total_collateral_eth,
      total_debt_eth,
      available_borrow_eth,
      current_liquidation_threshold,
      ltv,
      health_factor,
  ) = lending_pool.getUserAccountData(account.address)
  # getUserAccountData is a view funtion so you dont have tp add a from account
  
  # the returned variables will be in wei, 
  available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
  total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
  total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
  print(f"you have {total_collateral_eth} worth of eth deposited")
  print(f"you have {total_debt_eth} worth of eth borrowed ")
  print(f"you can borrow {available_borrow_eth} worth of eth")
  return (float(available_borrow_eth), float(total_debt_eth))
  

def get_asset_price(price_feed_Address):
  # ABI
  # ADDRESS
  dai_eth_pricefeed = interface.AggregatorV3Interface(price_feed_Address)
  latest_price = dai_eth_pricefeed.latestRoundData()[1]
  print(f"THE DAI/ETH PRICE IS {latest_price}")
  # the price of dai is 479577455939142 which is basically, 0.000479577455939142 ether
  #remember the result has 18 decimal places 
  
  converted_latest_price = Web3.fromWei(latest_price, "ether")
  return float(converted_latest_price)

def repay_all(amount, lending_pool, account):
  approve_erc20(Web3.toWei(amount, "ether"), lending_pool, config["networks"][network.show_active()]["dai_token_address"], account)
  repay_tx = lending_pool.repay(config["networks"][network.show_active()]["dai_token_address"], amount, 1, account.address, {"from":account})
  repay_tx.wait(1)  
  print("repaid")
  
  
def main():
  account = get_account()
  erc20_address = config["networks"][network.show_active()]["weth_token"]
  if network.show_active() in ["mainnet-fork"]:
    get_weth()
  # get weth incase we dont already have it
  lending_pool = get_lending_pool()
  # approve the sending of our erc20 token
  approve_erc20( amount, lending_pool.address, erc20_address, account)
  print("depositing")
  tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from":account})
  tx.wait(1)
  print("deposited")
  # ...how much can be borrowed
  borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
  # lets borrow some DAI
  print("lets borrow some DAI")
  dai_eth_price = get_asset_price(
      (config["networks"][network.show_active()]["dai_eth_pricefeed"]))
  amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
  # converting oour borrowable eth to borrowable DAI
  # multiplying it by 95% to better our "health factor"
  print(f"we're going to borrow {amount_dai_to_borrow} DAI")
  # now we borrow
  dai_token_address = config["networks"][network.show_active()]["dai_token_address"] 
  borrow_tx = lending_pool.borrow(dai_token_address, Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account.address, {"from":account})
  # the 1 stands for the interest rate type. 1 is for fixed and 2 is for variable.. check the documentation for the parameters passed if unclear
  borrow_tx.wait(1) 
  print("borrowed some DAI")
  get_borrowable_data(lending_pool, account)
  repay_all(amount, lending_pool, account)
  print("you just deposited, borrowed and repayed with aave, brownie and chainlink")