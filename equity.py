import sys
import yaml

with open("finance_info.yaml") as file:
    yaml_file = yaml.load(file, Loader=yaml.FullLoader)
PORTFOLIO_BALANCE = int(sys.argv[1])
CASH = int(sys.argv[2])
PORTFOLIO_INVESTED = yaml_file["PORTFOLIO_INVESTED"]
LOAN = yaml_file["STUDY_LOAN_LEFT"]
LOAN_BENEFIT = yaml_file["LOAN_BENEFIT"]
STOCK_TAX = yaml_file["STOCK_TAX"]
DIVIDEND_TAX = yaml_file["DIVIDEND_TAX"]

print(
    "Savings:           ",
    PORTFOLIO_INVESTED + CASH + STOCK_TAX - LOAN - LOAN_BENEFIT)
print(
    "Investment profits:",
    PORTFOLIO_BALANCE - PORTFOLIO_INVESTED + LOAN_BENEFIT - STOCK_TAX)
