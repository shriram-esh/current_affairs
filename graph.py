import numpy as np 
import plotly.graph_objects as go
import pandas as pd
import random

def generate_random_rgba(cleared):
    r = random.randint(0, 255)  # Random red value
    g = random.randint(0, 255)  # Random green value
    b = random.randint(0, 255)  # Random blue value
    alpha = 1.0 if cleared else 0.5  # Set alpha based on 'cleared' value
    return f'rgba({r}, {g}, {b}, {alpha})'

def convert_numpy_to_list(obj):
    """Recursively convert NumPy arrays to Python lists."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_to_list(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_list(value) for key, value in obj.items()}
    else:
        return obj

def create_graph(demand, marketPrice, bids):

    # {
    #     "bidQuantity": bid, 
    #     "from": runningQuantityCount,
    #     "to": (runningQuantityCount + bid), 
    #     "bidPrice": player["bidPrice"], 
    #     "player": player["username"],
    #     "cleared": isCleared
    # }

    df = pd.DataFrame(bids)
    df.columns = ['quantity', 'from', 'to', 'price', 'user', "cleared"]

    df['color'] = df.apply(lambda row: generate_random_rgba(row['cleared']), axis=1)

    df = df.sort_values(by=['from', 'cleared'], ascending=[True, False])

    print(f"Demand: ${demand}")
    print(f"MarketPrice: ${marketPrice}")
    print(df)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=((df["from"]+df["to"])/2).to_list(),
            y=df["price"],
            width=(df["to"]-df["from"]).to_list(),
            text=df['user'].to_list(),  # Add custom labels
            # hoverinfo="text",  # Show custom text and Y value
            marker=dict(color=df["color"]),
            # text=["Extra Info A", "Extra Info B", "Extra Info C"],  
            hovertemplate="<br>Price: %{y}<br>%{text}<extra></extra>"
        )
    )

    max_x = df["to"].max()
    if max_x < demand:
        max_x = demand

    max_y = round(df["price"].max() * 1.25)
    if max_y < marketPrice:
        max_y = marketPrice

    fig.add_hline(
        y=marketPrice,
        line_width=3,
        line_dash="dash",
        line_color="red",
        annotation_text="Market Price",  # Label text for the horizontal line
        annotation_position="top left"   # Position the label on the graph
    )

    fig.add_vline(
        x=demand,
        line_width=3,
        line_dash="dash",
        line_color="black",
        annotation_text="Demand",  # Label text for the vertical line
        annotation_position="top left"  # Position the label on the graph
    )

    fig.update_layout(
                        xaxis=dict(range=[0, max_x]),
                        yaxis=dict(range=[0, max_y]),
                        dragmode=False,
    )

    config = {
        "displayModeBar": False,  # Hide mode bar
        "staticPlot": False,  # Allow hover but disable zoom/pan
        "displaylogo": False,  # Remove Plotly logo
        "scrollZoom": False,  # Disable scroll zoom
        "editable": False  # Disable editing
    }

    fig_dict = fig.to_dict()
    fig_dict = convert_numpy_to_list(fig_dict)

    fig.show(config={
        'displayModeBar': False,  # Hide the mode bar (top-right)
        'staticPlot': False,       # Allow hover interactions while disabling pan/zoom
        'displaylogo': False,      # Disable the Plotly logo
        'scrollZoom': False,       # Disable scroll zoom
        'editable': False,         # Disable editing
    })

    # fig_json = {
    #     "fig_dict": fig_dict,
    #     "config": config  # Include config here
    # }

    # return fig_json

