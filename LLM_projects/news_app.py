import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc

# tools
from tools.gkg_tools import * # Import the gkg_operator class for gdelt gkg data processing
from tools.ssh_tunnel import * # Import the SSHConnection class for SSH tunneling
# components
from components.login import * # Import the login functions
from components.main_modal import * # Import the main_modal_callbacks function and image grid layout
from components.image_grid import * # Import the image grid layout
from components.sidebar import * # Import the sidebar layout


# Set up the GKG operator to use gkg_tools
gkg = gkg_operator() # create a gkg operator
# manga = pd.read_csv('.\\LLM_projects\\manga_soup_labeled.csv')
manga = pd.read_csv('data\\manga_soup_labeled.csv')
manga = manga[manga['sourcecommonname'].map(manga['sourcecommonname'].value_counts()) > 5]
manga = manga[manga['sharingimage'].notnull()]
gkg.get_gkg(data=manga) # stores in gkg.gkg_query as a dataframe
gkg.parse_urls()
# Set up images sample from manga sharingimage for rows in manga.


# app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"], suppress_callback_exceptions=True)

# note: `dash.register_page()` must be called after app instantiation
# pages
from pages.news_grid import * # Import the news grid layout
from pages.tSNE_news import * # Import the tSNE layout
from pages.about import * # Import the about layout
from pages.contact_info import * # Import the contact layout


app.title = "One Piece News Dashboard"
print([d for d in dir(app)])


# access the underlying Flask server
access_flask_server(app)
# Add login route to the app
login_route(app)
add_google_oauth(app)
register_user(app)

# establish connection to the remote server
app.ssh_connection_status = False # initialize the ssh status
ssh_server_route(app)


# allow all layout and callback functions to access the app object
app.manga = manga.copy()
app.gkg = gkg
app.images = [
    {"src": row["sharingimage"], "alt": row["title"]}
    for _, row in app.gkg.gkg_query.iterrows()
]

# Main layout
app.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),  # Tracks the URL
        # html.H1(
        #     "ONE PIECE NEWS DASHBOARD!",
        #     className="dashboard-title",
        # ),
        navigation_icon(app), # Navigation icon for the off-canvas menu
        off_canvas_nav(app), # Off-canvas navigation menu
        html.Div(id="page-content"),  # Placeholder for page content
    ]
)

# Callback to update page content based on URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/tSNE_news":
        return tSNE_layout(app)
    elif pathname == "/about":
        return about_layout(app)
    elif pathname == "/contact_info":
        return contact_layout(app)
    else:
        return news_grid_layout(app)  # Default to home


main_modal_callbacks(app)
ssh_connection(app)
tSNE_scatter_modal(app)
handle_logout(app)

# callback for updating the modal content
# print(f"Test to see if main modal stored app.images: {app.images}")

# Test the gkg operator
# print(f"Test using app.gkg: {app.gkg.parse_gkg_field('v2tone')}")

# print(app.menu_items)


# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
