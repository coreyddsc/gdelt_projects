import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc
from dash.exceptions import PreventUpdate  # Import PreventUpdate

import dash_bootstrap_components as dbc
from tools.gkg_tools import * # Import the gkg_operator class for gdelt gkg data processing
from components.main_modal import * # Import the main_modal_callbacks function and image grid layout


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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.manga = manga.copy()
app.gkg = gkg
app.images = [
    {"src": row["sharingimage"], "alt": row["title"]}
    for _, row in app.gkg.gkg_query.iterrows()
]


app.layout = html.Div(
    children=[
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            className="dashboard-title",
        ),
        # Update the image grid with titles
        image_grid(app),
        # Modal for displaying image details
        main_modal(app),
    ]
)

# callback for updating the modal content
print(f"Test to see if main modal stored app.images: {app.images}")

main_modal_callbacks(app)

print(f"Test using app.gkg: {app.gkg.parse_gkg_field('v2tone')}")

# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
