import json

import plotly.graph_objects as go


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


def plot_pie_chart(current_percentages, goal_percentages):
    """Plots an interactive pie chart showing the current allocation of assets and the goal allocation
    of assets.

    Args:
    - current_percentages: A dictionary containing the current percentage of each asset.
    - goal_percentages: A dictionary containing the goal percentage of each asset.
    """
    labels = list(current_percentages.keys())
    current_sizes = list(current_percentages.values())
    total_value = sum(current_percentages.values())

    goal_sizes = [
        (goal_percentages.get(asset, 0) / 100) * total_value for asset in labels
    ]

    colors = [
        "#FFE08F",
        "#C0C0C0",
        "#98FB98",
        "#FFDAB9",
        "#ADD8E6",
        "#D8BFD8",
        "#FFB6C1",
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=current_sizes,
                name="Current Allocation",
                hole=0.5,
                marker=dict(colors=colors),
            ),
            go.Pie(
                labels=labels,
                values=goal_sizes,
                name="Goal Allocation",
                hole=0.7,
                marker=dict(colors=colors, line=dict(width=1, color="black")),
            ),
        ]
    )

    action_suggestion = suggest_action(current_percentages, goal_percentages)

    fig.update_layout(
        title=dict(text="Investment Allocation", x=0.5, font_size=24),
        annotations=[
            dict(
                text="Current Allocation", x=0.5, y=0.5, font_size=20, showarrow=False
            ),
            dict(text="Goal Allocation", x=0.5, y=1, font_size=20, showarrow=False),
            dict(
                text=f"Suggestion: {action_suggestion}",
                x=0.5,
                y=-0.1,
                font_size=20,
                showarrow=False,
            ),
        ],
        legend=dict(
            x=0.9,
            y=0.5,
            traceorder="normal",
            font=dict(size=10),
            bgcolor="White",
            bordercolor="Black",
            borderwidth=1,
            orientation="v",
        ),
    )
    fig.show()


def suggest_action(current_percentages, goal_percentages):
    """Suggests an action based on the difference between current and goal percentages.

    Args:
    - current_percentages: A dictionary containing the current percentage of each asset.
    - goal_percentages: A dictionary containing the goal percentage of each asset.

    Returns:
    - A string suggesting an action to adjust the allocation for the asset with the largest difference.
    """
    asset_diffs = {}
    for asset, goal_perc in goal_percentages.items():
        curr_perc = current_percentages.get(asset, 0)
        diff = goal_perc - curr_perc
        asset_diffs[asset] = diff

    sorted_diffs = sorted(asset_diffs.items(), key=lambda x: abs(x[1]), reverse=True)

    largest_diff = sorted_diffs[0]
    asset_name = largest_diff[0]
    asset_diff = largest_diff[1]

    if asset_diff > 0:
        return f"Increase {asset_name} allocation by {abs(asset_diff):.2f}%."
    elif asset_diff < 0:
        return f"Decrease {asset_name} allocation by {abs(asset_diff):.2f}%."
    else:
        return "Asset allocation is on track with the goal."


def main():
    data = read_json("investments.json")
    current_percentages = calculate_current_percentage(data)
    goal_percentages = data.get("goal_percentage", {})
    plot_pie_chart(current_percentages, goal_percentages)


if __name__ == "__main__":
    main()
