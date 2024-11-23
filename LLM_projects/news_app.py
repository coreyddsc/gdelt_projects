import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc
from tools.gkg_tools import * # Import the gkg_operator class for gdelt gkg data processing
from components.main_modal import * # Import the main_modal_callbacks function and image grid layout

# app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div(
    children=[
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            className="dashboard-title",
        ),
        # Store the images data to be shared across callbacks
        image_store,
        # Update the image grid with titles
        image_grid,
        # Modal for displaying image details
        main_modal,
        # Store the number of clicks for each image for tracking
        n_clicks_store,
    ]
)

# callback for updating the modal content
main_modal_callbacks(app)


# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
