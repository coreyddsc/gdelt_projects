import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc

# tools
from tools.gkg_tools import * # Import the gkg_operator class for gdelt gkg data processing

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

# access the underlying Flask server
access_flask_server(app)
# Add login route to the app
login_route(app)
add_google_oauth(app)
register_user(app)

# allow all layout and callback functions to access the app object
app.manga = manga.copy()
app.gkg = gkg
app.images = [
    {"src": row["sharingimage"], "alt": row["title"]}
    for _, row in app.gkg.gkg_query.iterrows()
]


logout = html.Div(
    [
        html.Button("Logout", id="logout", n_clicks=0),
        dcc.Location(id="redirect", refresh=True),
    ],
    style={
        'position': 'absolute',
        'top': '20px',
        'right': '20px',
        'zIndex': 1001,  # Ensure it's above other content
        'background': 'white',
        'border': 'none',
        'padding': '2.5px',
        'cursor': 'pointer',
        'border-radius': '2px',
        'button-radius': '10px',
    }
)


app.layout = html.Div(
    children=[
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            className="dashboard-title",
        ),
        # Update the image grid with titles,
        
        
        image_grid(app),
        # Modal for displaying image details
        main_modal(app),
        sidebar(app),
        logout,
    ]
)


main_modal_callbacks(app)
sidebar_callbacks(app)
# Add the logout callback
handle_logout(app)

# callback for updating the modal content
# print(f"Test to see if main modal stored app.images: {app.images}")

# Test the gkg operator
# print(f"Test using app.gkg: {app.gkg.parse_gkg_field('v2tone')}")

print(app.menu_items)

# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
