import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc
from gkg_tools import *

# Set up the GKG operator to use gkg_tools
gkg = gkg_operator() # create a gkg operator
manga = pd.read_csv('manga_soup_labeled.csv')
manga = manga[manga['sourcecommonname'].map(manga['sourcecommonname'].value_counts()) > 5]
manga = manga[manga['sharingimage'].notnull()]
gkg.get_gkg(data=manga) # stores in gkg.gkg_query as a dataframe
gkg.parse_urls()

# Sample images for the grid from manga sharingimage for rows in manga.
# manga is stored in gkg.gkg_query
images = [
    {"src": row["sharingimage"], "alt": row["title"]}
    for _, row in gkg.gkg_query.iterrows()
]

# Initialize the app
app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        # App title
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            style={'color': 'white', 'textAlign': 'center', 'font-size': '125px'}
        ),
        # Grid container for images
        html.Div(
            id="image-grid",
            children=[
                html.Img(
                    src=image["src"],
                    alt=image["alt"],
                    className="grid-item",
                    id=f"img-{index}",  # Unique ID for each image
                )
                for index, image in enumerate(images)
            ],
        ),
        # Modal for displaying image details
        dbc.Modal(
            [
                dbc.ModalBody(id="modal-content", children="This is the modal content."),
                dbc.ModalFooter(
                    dbc.Button(
                        "×",  # Close button text
                        id="close-modal-btn",  # ID for callback
                        className="btn-close",  # Apply optional CSS
                        style={"margin-right": "auto", "color": "black"},  # Inline styling
                    ), # Show close button
                    ),  # Hide the footer
            ],
            id="image-modal",
            scrollable=True,  # Allow modal to scroll
            is_open=False,  # Modal starts closed
            size="lg",
            backdrop="static",  # Disable clicking outside of modal to close
            autoFocus=True,  # Auto focus on modal
            centered=True,  # Center the modal
        ),
        dcc.Store(id="n_clicks_store", data=[0] * len(images)),  # Store for previous n_clicks
    ]
)

@app.callback(
    [
        Output("image-modal", "is_open"),
        Output("modal-content", "children"),
        Output("n_clicks_store", "data"),  # Update the stored state
    ],
    [
        Input(f"img-{index}", "n_clicks") for index in range(len(images))
    ] + [Input("close-modal-btn", "n_clicks")],
    [
        State("image-modal", "is_open"),
        State("n_clicks_store", "data"),  # Previous n_clicks state
    ],
)
def toggle_or_close_modal(*args):
    ctx = dash.callback_context  # Get callback context
    if not ctx.triggered:
        raise PreventUpdate  # Nothing triggered the callback

    # Get which input triggered the callback
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"Triggered ID: {triggered_id}")

    # Separate Inputs and States
    n_clicks_new = args[:len(images)]  # Inputs: Current n_clicks for images
    n_clicks_old = args[len(images) + 2]  # State: Previous n_clicks from Store

    # Handle None values
    n_clicks_new = [0 if click is None else click for click in n_clicks_new]
    n_clicks_old = [0 if click is None else click for click in n_clicks_old]

    # Handle Close Button Click
    if triggered_id == "close-modal-btn":
        print("Close button clicked")
        return False, "", [0] * len(images)

    # Handle Image Click
    if triggered_id.startswith("img-"):
        clicked_index = int(triggered_id.split("-")[1])  # Extract index
        print(f"Image {clicked_index} clicked")

        # Update Modal Content and Open Modal
        return True, html.Div([
            dbc.ModalTitle(
                f"{images[clicked_index]['alt']}",
                style={"color": "black", "textAlign": "center", 'font-size': '55px'}
            ),
            html.Img(src=images[clicked_index]['src'], style={"maxWidth": "100%"}),
        ]), n_clicks_new

    # If no valid trigger, prevent update
    print("No valid trigger detected, preventing update.")
    raise PreventUpdate



# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
