import sys
import yaml

with open("finance_info.yaml") as file:
    yaml_file = yaml.load(file, Loader=yaml.FullLoader)
PORTFOLIO_BALANCE = int(sys.argv[1])
CASH = int(sys.argv[2])
PORTFOLIO_INVESTED = yaml_file["PORTFOLIO_INVESTED"]
LOAN = yaml_file["LOAN"]
LOAN_BENEFIT = yaml_file["LOAN_BENEFIT"]
STOCK_TAX = yaml_file["STOCK_TAX"]
DIVIDEND_TAX = yaml_file["DIVIDEND_TAX"]

print(
    "Savings:           ",
    PORTFOLIO_INVESTED - LOAN + CASH + STOCK_TAX)
print(
    "Investment profits:",
    PORTFOLIO_BALANCE - PORTFOLIO_INVESTED + LOAN_BENEFIT - STOCK_TAX)
