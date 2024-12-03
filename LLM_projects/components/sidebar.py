import dash
from dash import Input, Output, State, html, dcc, ctx, callback_context
import dash_bootstrap_components as dbc
from components.login import *

    

def navigation_icon(app):
    # SVG button in the top-left corner
    app.navigation_icon = html.Div(
        children=[
            html.Button(
                children=[
                    html.ObjectEl(
                        type="image/svg+xml",
                        data="/assets/extracted_logpose.png",  # Reference to the SVG in the assets folder
                        width="150px",  # Adjust width as necessary
                        height="150px",  # Adjust height as necessary
                    )
                ],
                id="svg-button",  # Optional ID for the button
                style={
                    "position": "fixed",
                    "top": "20px",  # Adjust the top margin to position the button
                    "left": "20px",  # Adjust the left margin to position the button
                    "border": "none",
                    "background": "transparent",
                    "cursor": "pointer",
                    "z-index": "3000",  # Bring to the front by setting a high z-index
                    # "box-shadow": "4px 4px 10px rgba(0, 0, 0, 0.3)",  # Shadow effect
                },
                n_clicks=0  # This tracks the number of clicks, if needed
            )
        ]
    )
    return app.navigation_icon



# make off-canvas dbc componet that opens when the navigation icon is clicked
def off_canvas_nav(app):
    # Define the off-canvas navigation component
    app.off_canvas = dbc.Offcanvas(
        children=[
            html.H3("Navigation Menu", className="mb-3"),
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("tSNE News Clustering", href="/tSNE_news", active="exact"),
                    dbc.NavLink("About", href="/about", active="exact"),
                    dbc.NavLink("Contact", href="/contact_info", active="exact"),
                    dcc.Markdown("---"),  # break line
                    html.H3("SSH Activation Panel", className='mb-3'),  # SSH activation panel title
                    dcc.Input(id="ssh-host", type="text", placeholder="lambda2.uncw.edu"),  # Input field for host
                    dcc.Input(id="ssh-user", type="text", placeholder="username"),  # Input field for username
                    dcc.Input(id="ssh-password", type="password", placeholder="password"),  # Input field for password
                    # Button to activate the SSH connection
                    dbc.Button("Connect", id="ssh-connect", color="primary", className="mt-2"),
                    # Button to disconnect the SSH connection
                    dbc.Button("Disconnect", id="ssh-disconnect", color="danger", className="mt-2"),
                    # Status message for the SSH connection
                    html.Div(id="ssh-status", className="mt-2"),
                    dcc.Markdown("---"),  # break line
                    logout_button(app),  # Logout button below the panels
                ],
                vertical=True,
                pills=True,
            ),
        ],
        id="offcanvas-nav",
        is_open=False,
        placement="start",  # Position the off-canvas on the left
    )

    # Callback to toggle the off-canvas visibility
    @app.callback(
        Output("offcanvas-nav", "is_open"),
        [Input("svg-button", "n_clicks")],
        [State("offcanvas-nav", "is_open")],
    )
    def toggle_offcanvas(n_clicks, is_open):
        if n_clicks:
            return not is_open
        return is_open

    return app.off_canvas


def ssh_connection(app):
    # Callback to handle SSH connection
    @app.callback(
        Output("ssh-status", "children"),  # Update a status message
        Input("ssh-connect", "n_clicks"),  # Trigger on Connect button click
        [
            State("ssh-host", "value"),       # Retrieve host input value
            State("ssh-user", "value"),       # Retrieve username input value
            State("ssh-password", "value"),   # Retrieve password input value
        ]
    )
    def connect_ssh(n_clicks, host, user, password):
        if not ctx.triggered_id or n_clicks is None:
            return "Enter the SSH connection details and click Connect."
        
        # Connect to the SSH server
        try:
            app.ssh_connection = SSHConnection(hostname=host, username=user, password=password)
            app.ssh_connection.connect()
            app.ssh_connection_status = True  # Set the SSH status to True
            return "Connected to the SSH server."
        except Exception as e:
            return f"Failed to connect to the SSH server. Error: {e}"


