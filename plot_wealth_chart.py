import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
from math import sqrt, ceil


# CSV file name and delimiter in CSV file
CSV_FILE_NAME = "omaisuus.csv"
DELIMITER = ','

# Date format e.g. 31.12.2019 or 12/31/2019
# Set how often the date is shown in x-axis, can use mdates.DayLocator
DATE_FORMAT = "%Y"
LOCATOR = mdates.YearLocator

YEARS_PREDICTION = 3


def readCsvData(file_name, delimiter):
    date_values = {
        "savings": [],
        "stock_profits": [],
        "equities": [],
        "dates_as_numbers": [],
    }
    year_values = {
        "savings": [],
        "stock_profits": [],
        "equities": [],
        "years": [],
    }
    previous_year = None
    with open(file_name, 'r') as csv_file:
        line_reader = csv.reader(csv_file, delimiter=delimiter)
        for i, line in enumerate(line_reader):
            if i == 0:
                continue
            [day, month, year, saving, stock_profit] = [int(l) for l in line]
            date = "{}/{}/{}".format(month, day, year)
            date_as_number = mdates.datestr2num(date)

            # Store values
            date_values["savings"].append(saving)
            date_values["stock_profits"].append(stock_profit)
            date_values["equities"].append(saving + stock_profit)
            date_values["dates_as_numbers"].append(date_as_number)

            # Interpolate values on year's last day 31st of Dec
            if previous_year is not None and year > previous_year:
                year_values["years"].append(previous_year)

                # Take x-axis values (dates)
                x0 = date_values["dates_as_numbers"][-2]
                x2 = date_as_number
                x1 = mdates.datestr2num(f"31/12/{previous_year}")

                # Interpolate y-axis values (weighted average)
                for key in date_values.keys():
                    if key == "dates_as_numbers":
                        continue
                    y0 = date_values[key][-2]
                    y2 = date_values[key][-1]
                    y1 = y0 + (y2 - y0) * (x1 - x0) / (x2 - x0)
                    year_values[key].append(y1)
            previous_year = year
        year_values["savings"].append(saving)
        year_values["stock_profits"].append(stock_profit)
        year_values["equities"].append(saving + stock_profit)
        year_values["years"].append(year)
    return date_values, year_values


def plotDataPerDay(
        dates_as_numbers, datas, labels, title, ylabel, show=True,
        line_style='-'):
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
    plt.gca().xaxis.set_major_locator(LOCATOR())
    for data, label in zip(datas, labels):
        plt.plot(dates_as_numbers, data, line_style, label=label)
    plt.legend()
    plt.grid(axis='y')
    plt.gcf().autofmt_xdate()
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gca().set_yticklabels(["{:,.0f}".format(x) for x in plt.gca().get_yticks()])
    if show:
        plt.show()


def readCommandLineArguments():
    csv_file_name = CSV_FILE_NAME
    delimiter = DELIMITER
    if len(sys.argv) > 1:
        csv_file_name = sys.argv[1]
    if len(sys.argv) > 2:
        delimiter = sys.argv[2]
    return csv_file_name, delimiter


def percentageYearlyGrowth(year_values, skip_keys, equity_comparison_keys=[]):
    percentage_yearly_growth = {}

    # Growth compared to last year value
    for key in year_values.keys():
        if key in skip_keys:
            continue
        growths = []
        for i in range(1, len(year_values[key])):
            growths.append(
                100 * (year_values[key][i] / year_values[key][i-1] - 1))
        percentage_yearly_growth[key] = growths

    # Growth compared to last year equity
    for key in equity_comparison_keys:
        growths = []
        for i in range(1, len(year_values[key])):
            growth = 100 * (year_values[key][i] - year_values[key][i-1]) / year_values["equities"][i-1]
            growths.append(growth)
        percentage_yearly_growth[key + "_per_equity"] = growths
    percentage_yearly_growth["years"] = year_values["years"][1:].copy()
    return percentage_yearly_growth


def absoluteYearlyGrowth(year_values, skip_keys):
    absolute_yearly_growth = {}
    for key in year_values.keys():
        if key in skip_keys:
            continue
        growths = []
        for i in range(1, len(year_values[key])):
            growths.append(year_values[key][i] - year_values[key][i-1])
        absolute_yearly_growth[key] = growths
    absolute_yearly_growth["years"] = year_values["years"][1:].copy()
    return absolute_yearly_growth


def getRedGreenColorMap(data):
    color_map = []
    for value in data:
        if value < 0:
            color_map.append('r')
        else:
            color_map.append('g')
    return tuple(color_map)


def plotBarChart(x, y, title, show=True):
    plt.bar(x, y, color=getRedGreenColorMap(y))
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel("%")
    if show:
        plt.show()


def plot2Datasets(x, data_1, data_2, title, ylabel_1, ylabel_2,
                  data_name_1, data_name_2, values_can_be_negative=True,
                  bar_width=0.3):
    fig = plt.figure()
    ax_1 = fig.add_subplot(111)

    color = "tab:orange"
    if values_can_be_negative:
        color = getRedGreenColorMap(data_2)
        ax_1.plot(x, list(np.zeros(len(x))), color="black")

    indices_1 = list(np.array(x) - bar_width / 2)
    indices_2 = list(np.array(x) + bar_width / 2)
    ax_1.bar(indices_1, data_1, bar_width, label=data_name_1)
    ax_1.set_ylabel(ylabel_1)
    ax_1.bar(indices_2, data_2, bar_width, label=data_name_2, color=color)

    fig.legend()
    ax_1.set_xlabel("Year")
    plt.title(title)
    plt.gca().set_yticklabels(["{:,.0f}".format(x) for x in plt.gca().get_yticks()])
    plt.show()


def plotTable(year_values, date_values):
    table_data = []
    previous_equity = 0
    previous_saving = 0
    previous_stock_profit = 0
    number_of_years = len(year_values["years"])
    for i in range(number_of_years):
        months_a_year = mdates.num2date(date_values["dates_as_numbers"][-1]).month if i == number_of_years - 1 else 12
        equity = int(year_values["equities"][i])
        saving = int(year_values["savings"][i])
        stock_profit = int(year_values["stock_profits"][i])
        table_data.append([
            year_values["years"][i],
            "{:,.0f}".format(equity),
            "-" if previous_equity == 0 else "{:.2f} %".format(100 * (equity / previous_equity - 1)),
            "{:,.0f}".format(saving),
            "{:,.0f}".format((saving - previous_saving) / months_a_year),
            "-" if previous_saving == 0 else "{:.2f} %".format(100 * (saving / previous_saving - 1)),
            "{:,.0f}".format(stock_profit),
            "-" if previous_stock_profit <= 0 else "{:.2f} %".format(100 * (stock_profit / previous_stock_profit - 1)),
        ])
        previous_equity = equity
        previous_saving = saving
        previous_stock_profit = stock_profit
    plt.axis("off")
    table = plt.table(
        cellText=table_data,
        loc="center",
        colLabels=[
            "Year",
            "Equity",
            "YoY equity change",
            "Savings",
            "Monthly absolute savings",
            "YoY savings change",
            "Stock profit",
            "YoY stock profit change",
        ])
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    plt.title("Cumulative values")
    plt.show()


def predictGrowth(dates_as_numbers, datas, labels, title, y_label="€"):
    for i in range(len(datas)):
        p = np.polyfit(dates_as_numbers, np.log(np.array(datas[i])), 1)
        a = np.exp(p[1])
        b = p[0]
        fitted_x = np.linspace(
            dates_as_numbers[0], 366 * YEARS_PREDICTION + dates_as_numbers[-1], 100)
        fitted_y = a * np.exp(b * fitted_x)
        plotDataPerDay(
            dates_as_numbers, [datas[i]], [labels[i]], title, y_label, False)
        plotDataPerDay(
            fitted_x, [fitted_y], [f"{labels[i]} prediction"], title, y_label,
            False, line_style="--")
    plt.grid(axis='y')
    plt.show()


def main():
    # Read data
    csv_file_name, delimiter = readCommandLineArguments()
    date_values, year_values = readCsvData(csv_file_name, delimiter)
    percentage_yearly_growth = percentageYearlyGrowth(
        year_values, ["years", "stock_profits"], ["stock_profits", "savings"])
    absolute_yearly_growth = absoluteYearlyGrowth(year_values, ["years"])

    # Plot data
    plotDataPerDay(
        date_values["dates_as_numbers"],
        [
            date_values["savings"],
            date_values["stock_profits"],
            date_values["equities"],
        ], ["Savings", "Stock profits", "Equity"],
        "Wealth progress", "€")

    # Plot growth prediction
    predictGrowth(
        date_values["dates_as_numbers"],
        [
            date_values["savings"],
            date_values["equities"],
        ], ["Savings", "Equity"],
        "Wealth progress prediction")

    # Annual growth in table
    plotTable(year_values, date_values)

    # Plot growth
    y = [
        percentage_yearly_growth["stock_profits_per_equity"],
        percentage_yearly_growth["savings_per_equity"],
        percentage_yearly_growth["equities"],
        percentage_yearly_growth["savings"],
    ]
    titles = [
        "YoY Stock profit per equity",
        "YoY Savings per equity",
        "YoY Equity growth",
        "YoY Savings growth",
    ]
    grid_x = int(sqrt(len(y)))
    grid_y = ceil(len(y) / grid_x)
    for i in range(len(y)):
        plt.subplot(grid_x, grid_y, i+1)
        plotBarChart(percentage_yearly_growth["years"], y[i], titles[i], False)
    plt.show()

    plot2Datasets(
        absolute_yearly_growth["years"], absolute_yearly_growth["savings"],
        absolute_yearly_growth["stock_profits"], "Savings VS stock profits",
        "€", "€", "Savings", "Stock profits")


if __name__ == "__main__":
    main()
