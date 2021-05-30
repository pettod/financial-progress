import sys
import yaml

with open("finance_info.yaml") as file:
    yaml_file = yaml.load(file, Loader=yaml.FullLoader)
PORTFOLIO_BALANCE = int(sys.argv[1])
CASH = int(sys.argv[2])
PORTFOLIO_INVESTED = yaml_file["PORTFOLIO_INVESTED"]
LOAN = yaml_file["LOAN"]
LOAN_BENEFIT = yaml_file["LOAN_BENEFIT"]
CAPITAL_TAX = yaml_file["CAPITAL_TAX"]

print(
    "Savings:           ",
    PORTFOLIO_INVESTED - LOAN + CASH + CAPITAL_TAX)
print(
    "Investment profits:",
    PORTFOLIO_BALANCE - PORTFOLIO_INVESTED + LOAN_BENEFIT - CAPITAL_TAX)
