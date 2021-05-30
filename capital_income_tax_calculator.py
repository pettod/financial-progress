import csv
import pandas as pd
import numpy as np


STOCK_CSV_FILE = "nordnet-ostoerittain.csv"
DIVIDEND_CSV_FILE = "transactions_export.csv"
BASE_TAX_PERCENTAGE = 30
MARGIN_TAX_PERCENTAGE = 34
MARGIN_TAX_THRESHOLD = 50000
ZERO_TAX_THRESHOLD = 1000
N_YEARS_LOSSES_ACCUMULATED = 5
STOCK_NAMING_CONVERSION = {  # Define here the headers in CSV file
    "sell_date": "Luovutusaika",
    "profit": "Voitto tai tappio EUR",
    "buy_cost": "Hankintakulut EUR",
    "sell_cost": "Myyntikulut EUR",
}
DIVIDEND_NAMING_CONVERSION = {  # Define here the headers in CSV file
    "date": "Maksupäivä",
    "profit": "Summa",
    "transaction_type": "Tapahtumatyyppi",
    "dividend": "OSINKO",
    "tax": "ENNAKKOPIDÄTYS",
}


def taxAmount(incomes):
    # Calculate income based on previous years losses
    previous_years_incomes = sum(incomes[-N_YEARS_LOSSES_ACCUMULATED:-1])
    income = incomes[-1]
    if previous_years_incomes < 0:
        income += previous_years_incomes

    # Calculate tax for income
    if income > MARGIN_TAX_THRESHOLD:
        base_tax = BASE_TAX_PERCENTAGE * MARGIN_TAX_THRESHOLD
        margin_tax = MARGIN_TAX_PERCENTAGE * (income - MARGIN_TAX_THRESHOLD)
        tax = (base_tax + margin_tax) / 100
    elif income <= ZERO_TAX_THRESHOLD:
        tax = 0
    else:
        tax = BASE_TAX_PERCENTAGE * income / 100
    return tax


def printTable(texts, values):
    # Compute header length
    text_lengths = []
    for i, text in enumerate(texts):
        text_lengths.append(5 if i == 0 else max(9, len(text)))
    table_length = sum(text_lengths) + 4 + 3 * max(0, len(text_lengths) - 1)

    # Print header
    print(table_length * "-")
    print("| ", end="")
    for i, text in enumerate(texts):
        number_of_spaces = max(0, text_lengths[i] - len(text))
        print("{}{}".format(" " * number_of_spaces, text), end=" | ")

    # Print table
    print("\n" + table_length * "-")
    for i in range(len(values[0])):
        if i == len(values[0]) - 1:
            print(table_length * "-")
        print("| ", end="")
        for j in range(len(values)):
            value = values[j][i]
            if type(value) == np.float64:
                value = "{0:.2f}".format(value)
            number_of_spaces = max(0, text_lengths[j] - len(str(value)))
            print("{}{}".format(" " * number_of_spaces, value), end=" | ")
        print()
    print(table_length * "-")


def main():
    snc = STOCK_NAMING_CONVERSION
    dnc = DIVIDEND_NAMING_CONVERSION

    # Read CSV
    stock_df = pd.read_csv(
        STOCK_CSV_FILE, header=0, sep="\t", encoding="utf-16", decimal=",")
    dividend_df = pd.read_csv(
        DIVIDEND_CSV_FILE, header=0, sep="\t", encoding="utf-16", decimal=",")
    stock_df[snc["sell_date"]] = pd.to_datetime(
        stock_df[snc["sell_date"]], format="%d.%m.%Y")
    dividend_df[dnc["date"]] = pd.to_datetime(
        dividend_df[dnc["date"]], format="%Y.%m.%d")
    min_year_stock = min(stock_df[snc["sell_date"]]).year
    max_year_stock = max(stock_df[snc["sell_date"]]).year
    min_year_dividend = min(dividend_df[dnc["date"]]).year
    max_year_dividend = max(dividend_df[dnc["date"]]).year
    min_year = min(min_year_stock, min_year_dividend)
    max_year = max(max_year_stock, max_year_dividend)

    # Process annual info
    years = list(range(min_year, max_year + 1))
    buy_costs = []
    sell_costs = []
    losses = []
    profits = []
    dividends = []
    dividend_taxes = []
    incomes = []
    stock_taxes = []
    net_incomes = []
    for year in years:
        rows_stock = stock_df[
            (stock_df[snc["sell_date"]] > f"01-01-{year}") &
            (stock_df[snc["sell_date"]] < f"31-12-{year}")
        ]
        rows_dividend = dividend_df[
            (dividend_df[dnc["date"]] > f"01-01-{year}") &
            (dividend_df[dnc["date"]] < f"31-12-{year}")
        ]
        buy_cost = rows_stock[snc["buy_cost"]].astype(float).to_numpy().sum()
        sell_cost = rows_stock[snc["sell_cost"]].astype(float).to_numpy().sum()
        loss = abs(rows_stock[rows_stock[snc["profit"]] < 0][
            snc["profit"]].to_numpy().sum())
        profit = rows_stock[rows_stock[snc["profit"]] >= 0][
            snc["profit"]].to_numpy().sum()
        dividend = rows_dividend[
            rows_dividend[dnc["transaction_type"]] ==
            dnc["dividend"]][dnc["profit"]].to_numpy().astype(np.float64).sum()
        dividend_tax = abs(rows_dividend[rows_dividend[
            dnc["transaction_type"]] ==
            dnc["tax"]][dnc["profit"]].to_numpy().astype(np.float64).sum())
        income = profit - buy_cost - sell_cost - loss
        incomes.append(income)
        tax = taxAmount(incomes)
        net_income = income - tax
        buy_costs.append(buy_cost)
        sell_costs.append(sell_cost)
        profits.append(profit)
        dividends.append(dividend)
        dividend_taxes.append(dividend_tax)
        losses.append(loss)
        stock_taxes.append(tax)
        net_incomes.append(net_income)

    # Add dividends to incomes after tax calculations because dividends are
    # already taxed immediately when you receive them
    total_taxes = [a + b for (a, b) in zip(stock_taxes, dividend_taxes)]
    incomes = [a + b + c for (a, b, c) in zip(
        incomes, dividends, dividend_taxes)]
    net_incomes = [a + b for (a, b) in zip(net_incomes, dividends)]

    # Print
    texts = [
        "Year",
        "Buy cost",
        "Sell cost",
        "Loss",
        "Profit",
        "Dividend",
        "Income",
        "Stock tax",
        "Dividend tax",
        "Total tax",
        "Net income"
    ]
    values = [
        years + ["Total"],
        buy_costs,
        sell_costs,
        losses,
        profits,
        dividends,
        incomes,
        stock_taxes,
        dividend_taxes,
        total_taxes,
        net_incomes,
    ]
    for i in range(1, len(values)):
        values[i].append(sum(values[i]))
    printTable(texts, values)


main()
