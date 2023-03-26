import json
import random

import plotly.graph_objs as go
from plotly.subplots import make_subplots


class GoalPercentageError(Exception):
    pass


def check_goal_percentage(data):
    """Checks if the sum of goal percentages is equal to 100.

    Args:
    - data (dict): A dictionary containing the current and goal values for each asset.

    Raises:
    - ValueError: If the sum of goal percentages is not equal to 100.
    """
    goal_perc_total = sum(data["goal_percentage"].values())
    if goal_perc_total != 100:
        raise GoalPercentageError(
            "Goal percentages must sum up to 100. It's currently {}.".format(
                goal_perc_total
            )
        )


def read_json(file_path: str) -> dict:
    """
    Reads a JSON file and returns a dictionary containing its data.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: A dictionary containing the data from the JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict):
        check_goal_percentage(data)
        return data
    else:
        raise ValueError("JSON file does not contain a dictionary.")


def calculate_current_percentage(data):
    """
    Calculates the current percentage of each asset in the portfolio.

    Parameters:
    data (dict): A dictionary containing the current value of each asset.

    Returns:
    dict: A dictionary containing the current percentage of each asset.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    current_total = sum([v for k, v in data["current_value"].items()])
    current_percentages = {
        k: v / current_total * 100 for k, v in data["current_value"].items()
    }

    return current_percentages


def create_table(current_percentages, goal_percentages, total_value):
    """Creates a table containing the total value of the portfolio, current value for each asset,
    and values for each goal percentage.

    Args:
    - current_percentages: A dictionary containing the current percentage of each asset.
    - goal_percentages: A dictionary containing the goal percentage of each asset.
    - total_value: The total value of the portfolio.

    Returns:
    - A Plotly table containing the information.
    """
    asset_names = list(current_percentages.keys())
    current_percs = list(current_percentages.values())
    current_values = [curr_perc / 100 * total_value for curr_perc in current_percs]
    goal_percs = list(goal_percentages.values())
    goal_values = [goal_perc / 100 * total_value for goal_perc in goal_percs]
    diff_percs = [
        curr_perc - goal_perc for curr_perc, goal_perc in zip(current_percs, goal_percs)
    ]
    diff_values = [
        curr_value - goal_value
        for curr_value, goal_value in zip(current_values, goal_values)
    ]

    table_data = [
        [
            "Asset",
            "Current %",
            "Current Value",
            "Goal %",
            "Goal Value",
            "Difference %",
            "Difference Value",
        ]
    ]
    for (
        asset,
        curr_perc,
        curr_value,
        goal_perc,
        goal_value,
        diff_perc,
        diff_value,
    ) in zip(
        asset_names,
        current_percs,
        current_values,
        goal_percs,
        goal_values,
        diff_percs,
        diff_values,
    ):
        table_data.append(
            [
                asset,
                f"{curr_perc:.2f}%",
                f"${curr_value:,.2f}",
                f"{goal_perc:.2f}%",
                f"${goal_value:,.2f}",
                f"{diff_perc:.2f}%",
                f"${diff_value:,.2f}",
            ]
        )

    # Calculate total values
    total_current_perc = sum(current_percs)
    total_current_value = sum(current_values)

    # Append total row to table data
    table_data.append(
        [
            "Total Portfolio",
            f"{total_current_perc:.2f}%",
            f"${total_current_value:,.2f}",
            f"-",
            f"-",
            f"-",
            f"-",
        ]
    )

    table = go.Table(
        header=dict(
            values=table_data[0],
            font=dict(size=8),
            align=["left", "center"],
        ),
        cells=dict(
            values=list(zip(*table_data[1:])),
            font=dict(size=10),
            align=["left", "center"],
            height=30,
        ),
        columnwidth=[40, 30, 40, 30, 40, 30],
    )

    return table


def plot_pie_chart(data):
    """Plots an interactive pie chart showing the current allocation of assets and the goal allocation
    of assets.

    Args:
    - data (dict): A dictionary containing the current and goal values for each asset.
    """
    current_percentages = calculate_current_percentage(data)
    labels = list(data["current_value"].keys())
    current_sizes = list(data["current_value"].values())
    total_value = sum(current_sizes)

    goal_percentages = data["goal_percentage"]
    goal_sizes = [goal_percentages[asset] / 100 * total_value for asset in labels]

    # Generate a list of random RGB values
    colors = [
        "#%02x%02x%02x" % (r, g, b)
        for r, g, b in zip(
            random.sample(range(256), len(labels)),
            random.sample(range(256), len(labels)),
            random.sample(range(256), len(labels)),
        )
    ]

    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "table"}]])

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=current_sizes,
            name="Current Allocation",
            hole=0.5,
            marker=dict(colors=colors),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=goal_sizes,
            name="Goal Allocation",
            hole=0.7,
            marker=dict(colors=colors, line=dict(width=1, color="black")),
        ),
        row=1,
        col=1,
    )

    table = create_table(current_percentages, goal_percentages, total_value)

    fig.add_trace(table, row=1, col=2)

    action_suggestion = suggest_action(current_percentages, goal_percentages)

    fig.update_layout(
        title=dict(text="Investment Allocation", x=0.5, font_size=24),
        annotations=[
            dict(
                text="Current Allocation", x=0.175, y=0.5, font_size=20, showarrow=False
            ),
            dict(text="Goal Allocation", x=0.175, y=1, font_size=20, showarrow=False),
            dict(text=f"Suggestion:", x=0.58, y=0.6, font_size=16, showarrow=False),
            dict(
                text=f"{action_suggestion}",
                x=0.95,
                y=0.55,
                font=dict(size=14),
                showarrow=False,
            ),
        ],
        legend=dict(
            x=1e-4,
            y=1e-4,
            traceorder="normal",
            font=dict(size=14),
            bgcolor="White",
            bordercolor="Black",
            borderwidth=1,
            orientation="v",
        ),
    )
    fig.show()


def suggest_action(current_percentages, goal_percentages):
    """Suggests an action to rebalance the portfolio based on the current and goal asset allocations.

    Args:
    - current_percentages (dict): A dictionary containing the percentage allocation of assets in the current portfolio.
    - goal_percentages (dict): A dictionary containing the percentage allocation of assets in the goal portfolio.

    Returns:
    - A string describing the suggested action.
    """
    overall_buy = []
    overall_sell = []
    asset_suggestions = ""

    for asset in current_percentages.keys():
        current_percentage = current_percentages[asset]
        goal_percentage = goal_percentages[asset]
        difference = goal_percentage - current_percentage

        if difference > 0:
            overall_buy.append((asset, difference))
        elif difference < 0:
            overall_sell.append((asset, difference))

        asset_suggestions += f"{asset}: "

        if difference > 0:
            asset_suggestions += f"Buy more to increase allocation to {goal_percentage}% (currently {current_percentage}%)\n"
        elif difference < 0:
            asset_suggestions += f"Sell some to decrease allocation to {goal_percentage}% (currently {current_percentage}%)\n"
        else:
            asset_suggestions += f"Allocation is already at the goal percentage of {goal_percentage}% (currently {current_percentage}%)\n"

    # Check if there are any overall buy or sell suggestions
    if overall_buy:
        overall_buy.sort(key=lambda x: -x[1])
        best_buy = overall_buy[0][0]
        buy_message = f"Invest in {best_buy} to increase allocation by {round(overall_buy[0][1],2)}%"
    else:
        buy_message = "No suggestion to buy"

    if overall_sell:
        overall_sell.sort(key=lambda x: x[1])
        best_sell = overall_sell[0][0]
        sell_message = f"Stop investing in {best_sell} to decrease allocation by {round(-overall_sell[0][1],2)}%"
    else:
        sell_message = "No suggestion to sell"

    # Concatenate the buy and sell messages
    action = f"<b>{buy_message}<br>{sell_message}</b>"

    return action


def main():
    data = read_json("investments.json")
    plot_pie_chart(data)


if __name__ == "__main__":
    main()
