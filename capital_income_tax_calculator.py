import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, ceil


STOCK_CSV_FILE = "9a-report.csv"
DIVIDEND_CSV_FILE = "transactions-and-notes.csv"
BASE_TAX_PERCENTAGE = 30
MARGIN_TAX_PERCENTAGE = 34
MARGIN_TAX_THRESHOLD = 30000
ZERO_TAX_THRESHOLD = 1000
N_YEARS_LOSSES_ACCUMULATED = 5

# Define here the headers in CSV file
# 9a-report.csv
STOCK_NAMING_CONVERSION = {
    "sell_date": "Luovutusaika",
    "profit": "Voitto tai tappio EUR",
    "buy_cost": "Hankintakulut EUR",
    "sell_cost": "Myyntikulut EUR",
}

# Define here the headers in CSV file
# transactions-and-notes.csv
DIVIDEND_NAMING_CONVERSION = {
    "date": "Kauppapäivä",
    "profit": "Summa",
    "transaction_type": "Tapahtumatyyppi",
    "dividend": "OSINKO",
    "tax": "ENNAKKOPIDÄTYS",
    "loan_interest": "LAINAKORKO",
    "deposit": ["TALLETUS", "Reaaliaikainen talle"],
}


def singleTax(income):
    if income > MARGIN_TAX_THRESHOLD:
        base_tax = BASE_TAX_PERCENTAGE * MARGIN_TAX_THRESHOLD
        margin_tax = MARGIN_TAX_PERCENTAGE * (income - MARGIN_TAX_THRESHOLD)
        tax = (base_tax + margin_tax) / 100
    elif income <= ZERO_TAX_THRESHOLD:
        tax = 0
    else:
        tax = BASE_TAX_PERCENTAGE * income / 100
    return tax


def totalTax(incomes):
    # Calculate income based on previous years losses
    previous_years_incomes = sum(incomes[-N_YEARS_LOSSES_ACCUMULATED:-1])
    income = incomes[-1]
    if previous_years_incomes < 0:
        income += previous_years_incomes

    # Calculate tax for income
    return singleTax(income)


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
            if type(value) == np.float64 or type(value) == float:
                value = "{0:.2f}".format(value)
            number_of_spaces = max(0, text_lengths[j] - len(str(value)))
            print("{}{}".format(" " * number_of_spaces, value), end=" | ")
        print()
    print(table_length * "-")


def getRedGreenColorMap(data):
    color_map = []
    for value in data:
        if value < 0:
            color_map.append('r')
        else:
            color_map.append('g')
    return tuple(color_map)


def plotData(x_labels, datas, titles, colors):
    grid_x = int(sqrt(len(datas)))
    grid_y = ceil(len(datas) / grid_x)
    plt.subplots_adjust(
        left=0.05,
        bottom=0.05,
        right=0.95,
        top=0.95,
        wspace=None,
        hspace=0.4)

    # y-axis limits
    y_max = 0
    y_min = 0
    for data in datas:
        y_min = min(y_min, min(data))
        y_max = max(y_max, max(data))
    text_y_offset = 0.01 * (y_max + abs(y_min))
    y_limit_offset = 0.1 * abs(y_max - y_min)

    for i in range(len(datas)):
        data = len(datas[0]) * [0]
        title = ""
        if i < len(datas):
            data = datas[i]
        if i < len(titles):
            title = titles[i]
        plt.subplot(grid_x, grid_y, i+1)
        plt.ylim(y_min - y_limit_offset, y_max + y_limit_offset)

        # Values on top the bars
        color = colors[i]
        if color not in ["r", "g", "rg"]:
            raise ValueError(
                f"Color ({color}) must be one the following ['r', 'g', 'rg']")
        if color == "rg":
            color = getRedGreenColorMap(data)
        bars = plt.bar(x_labels, data, color=color)
        for bar in bars:
            height = bar.get_height()
            width = bar.get_width()
            x = bar.get_x() + width / 2
            y = max(0, height) + text_y_offset
            value = round(height, 2)
            plt.text(x, y, value, horizontalalignment="center")
        plt.title(title)
    plt.show()


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

    # Data storage
    years = list(range(min_year, max_year + 1))
    deposits = []
    buy_costs = []
    sell_costs = []
    loan_interests = []
    losses = []
    profits = []
    dividends = []
    paid_dividend_taxes = []
    taxed_incomes = []
    stock_incomes = []
    total_taxes = []
    net_incomes = []

    # Process annual info
    for year in years:

        # Pick annual data
        rows_stock = stock_df[
            (stock_df[snc["sell_date"]] >= f"01-01-{year}") &
            (stock_df[snc["sell_date"]] <= f"31-12-{year}")
        ]
        rows_dividend = dividend_df[
            (dividend_df[dnc["date"]] >= f"01-01-{year}") &
            (dividend_df[dnc["date"]] <= f"31-12-{year}")
        ]

        # Read data
        buy_cost = rows_stock[snc["buy_cost"]].astype(float).to_numpy().sum()
        sell_cost = rows_stock[snc["sell_cost"]].astype(float).to_numpy().sum()
        loss = abs(rows_stock[rows_stock[snc["profit"]] < 0][
            snc["profit"]].to_numpy().sum())
        profit = rows_stock[rows_stock[snc["profit"]] >= 0][
            snc["profit"]].to_numpy().sum()

        try:
            deposit = sum([rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                deposit_name][dnc["profit"]].replace(' ', '').astype(float).to_numpy().sum() for deposit_name in dnc["deposit"]])
            dividend = rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                dnc["dividend"]][dnc["profit"]].astype(float).to_numpy().sum()
            loan_interest = abs(rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                dnc["loan_interest"]][dnc["profit"]].astype(float).to_numpy().sum())
            paid_dividend_tax = abs(rows_dividend[rows_dividend[
                dnc["transaction_type"]] ==
                dnc["tax"]][dnc["profit"]].astype(float).to_numpy().sum())
        except ValueError:
            deposit = sum([sum([float(d.replace(',', '.').replace(' ', '')) for d in rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                deposit_name][dnc["profit"]].to_numpy()]) for deposit_name in dnc["deposit"]])
            dividend = sum([float(d.replace(',', '.')) for d in rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                dnc["dividend"]][dnc["profit"]].to_numpy()])
            loan_interest = abs(sum([float(d.replace(',', '.')) for d in rows_dividend[
                rows_dividend[dnc["transaction_type"]] ==
                dnc["loan_interest"]][dnc["profit"]].to_numpy()]))
            paid_dividend_tax = abs(sum([float(pdt.replace(',', '.')) for pdt in
                rows_dividend[rows_dividend[dnc["transaction_type"]] ==
                dnc["tax"]][dnc["profit"]].to_numpy()]))

        # Calculate income and tax
        stock_income = profit - buy_cost - sell_cost - loan_interest - loss
        stock_incomes.append(stock_income)
        taxed_incomes.append(stock_income + 0.85 * dividend)
        total_tax = totalTax(taxed_incomes)
        net_income = stock_income + dividend - total_tax

        # Store data
        deposits.append(deposit)
        buy_costs.append(buy_cost)
        sell_costs.append(sell_cost)
        loan_interests.append(loan_interest)
        profits.append(profit)
        dividends.append(dividend)
        paid_dividend_taxes.append(paid_dividend_tax)
        losses.append(loss)
        total_taxes.append(total_tax)
        net_incomes.append(net_income)

    total_incomes = [a + b for (a, b) in zip(stock_incomes, dividends)]
    residual_taxes = [
        max(0, a - b) for (a, b) in zip(total_taxes, paid_dividend_taxes)]

    # Print
    texts = [
        "Year",
        "Deposit",
        "Buy cost",
        "Sell cost",
        "Loan interest",
        "Loss",
        "Profit",
        "Dividend",
        "Income",
        "Paid dividend tax",
        "Total tax",
        "Residual tax",
        "Net income",
    ]
    values = [
        years,
        deposits,
        buy_costs,
        sell_costs,
        loan_interests,
        losses,
        profits,
        dividends,
        total_incomes,
        paid_dividend_taxes,
        total_taxes,
        residual_taxes,
        net_incomes,
    ]
    colors = [
        "g",
        "r",
        "r",
        "r",
        "r",
        "g",
        "g",
        "rg",
        "r",
        "r",
        "r",
        "rg",
    ]
    plotData(years, values[1:], texts[1:], colors)
    for i in range(len(values)):
        if i == 0:
            total = ["Total"]
        else:
            total = [sum(values[i])]
        values[i] = values[i].copy() + total
    printTable(texts, values)


main()
