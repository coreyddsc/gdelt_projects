import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate
import dash_bootstrap_components as dbc

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


def summarize_text_via_backend(text):
        if text:
            import requests
            try:
                # Send text to Flask backend
                response = requests.post("http://127.0.0.1:8053/summarize", json={"text": text})
                if response.status_code == 200:
                    data = response.json()
                    return f"Summary result:\n{data.get('result', 'No result received')}"
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Failed to connect to the backend. Error: {e}"
        return "Enter text and click Summarize to process."


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
            
            # paste together the paragraphs into a single string
            if app.ssh_connection_status:
                article_text = " ".join(app.gkg.parsed_paragraphs)
                summary_text = summarize_text_via_backend(article_text)
                print(f"Summary: {summary_text}")
            else:
                summary_text = "Please connect to the SSH server to summarize the article."
            
            # Modal Content
            model_content = html.Div([
                dbc.ModalTitle(
                    f"{app.images[clicked_index]['alt']}",
                    style={"color": "black", "textAlign": "center", 'font-size': '55px'}
                ),
                html.Img(src=app.images[clicked_index]['src'], style={"maxWidth": "100%"}),
                dcc.Markdown("---"),  # break line
                # Create a container for the summary
                html.Div([
                    html.H2("Summary", style={"margin-top": "20px","color": "black", "textAlign": "center", 'font-size': '45px'}),
                    html.P(summary_text)
                ]),
                dcc.Markdown("---"),  # break line
                # Create a parent container for the paragraphs
                html.Div([
                    html.H2("Article", style={"margin-top": "20px","color": "black", "textAlign": "center", 'font-size': '45px'}),
                ]),
                html.Div(
                    [html.P(par) for par in app.gkg.parsed_paragraphs],style={"margin-top": "20px"})
            ])
            # Update Modal Content and Open Modal
            return True, model_content, n_clicks_new

        # If no valid trigger, prevent update
        print("No valid trigger detected, preventing update.")
        raise PreventUpdate