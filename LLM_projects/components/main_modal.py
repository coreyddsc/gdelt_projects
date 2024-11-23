import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc
from tools.gkg_tools import *

def image_grid(app):
    image_grid = html.Div(id="image-grid", 
                        children=[
                                html.Div(
                                    className="image-container",  # Container for image and title
                                    children=[
                                        html.Img(
                                            src=image["src"],
                                            alt=image["alt"],
                                            className="grid-item",
                                            id=f"img-{index}",  # Unique ID for each image
                                        ),
                                        html.Div(
                                            className="image-title",  # Title text overlay
                                            children=image["alt"],  # Use the title text
                                        ),
                                    ],
                                )
                                for index, image in enumerate(app.images)
                            ])
    return image_grid

def main_modal(app):
    # Modal for displaying image details
    main_modal = dbc.Modal(
                [
                    dcc.Store(id="n_clicks_store", data=[0] * len(app.images)),  # Store the number of clicks
                    dbc.ModalBody(id="modal-content", children="This is the modal content."),
                    dbc.ModalFooter(
                        dbc.Button(
                            "×",  # Close button text
                            id="close-modal-btn",  # ID for callback
                            className="btn-close",  # Apply optional CSS
                            style={"margin-left": "auto", "color": "black", "display":"flex"},  # Inline styling
                        ), # Show close button
                    ), # Modal footer
                ],
                id="image-modal",
                scrollable=True,  # Allow modal to scroll
                is_open=False,  # Modal starts closed
                size="xl",
                backdrop="static",  # Disable clicking outside of modal to close
                autoFocus=True,  # Auto focus on modal
                centered=True,  # Center the modal
            )
    return main_modal

def main_modal_callbacks(app):
    # Callback to toggle or close the modal
    @app.callback(
        [
            Output("image-modal", "is_open"),
            Output("modal-content", "children"),
            Output("n_clicks_store", "data"),  # Update the stored state
        ],
        [
            Input(f"img-{index}", "n_clicks") for index in range(len(app.images))
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
        n_clicks_new = args[:len(app.images)]  # Inputs: Current n_clicks for images
        n_clicks_old = args[len(app.images) + 2]  # State: Previous n_clicks from Store

        # Handle None values
        n_clicks_new = [0 if click is None else click for click in n_clicks_new]
        n_clicks_old = [0 if click is None else click for click in n_clicks_old]

        # Handle Close Button Click
        if triggered_id == "close-modal-btn":
            print("Close button clicked")
            return False, "", [0] * len(app.images)

        # Handle Image Click
        if triggered_id.startswith("img-"):
            clicked_index = int(triggered_id.split("-")[1])  # Extract index
            print(f"Image {clicked_index} clicked")

            # Use gkg tools to parse the soup of the clicked image url
            app.gkg.parse_gkg_soup(url=app.gkg.urls[clicked_index],verbose=True)
            # Modal Content
            model_content = html.Div([
                dbc.ModalTitle(
                    f"{app.images[clicked_index]['alt']}",
                    style={"color": "black", "textAlign": "center", 'font-size': '55px'}
                ),
                html.Img(src=app.images[clicked_index]['src'], style={"maxWidth": "100%"}),
                # Create a parent container for the paragraphs
                html.Div([html.P(par) for par in app.gkg.parsed_paragraphs], style={"margin-top": "20px"})
            ])
            # Update Modal Content and Open Modal
            return True, model_content, n_clicks_new

        # If no valid trigger, prevent update
        print("No valid trigger detected, preventing update.")
        raise PreventUpdate