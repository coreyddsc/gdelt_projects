import dash
from dash import Dash, html, Input, Output, State
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

# Layout
app.layout = html.Div(
    children=[
        # App title
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            style={'color': 'white', 'textAlign': 'center', 'font-size': '100px'}
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
                    style={
                        "cursor": "pointer",  # Clickable images
                        "width": "400px",  # Uniform width
                        "height": "300px",  # Uniform height
                        "objectFit": "cover",  # Maintain aspect ratio while filling the space
                        "borderRadius": "10px",  # Optional: rounded corners
                    },
                )
                for index, image in enumerate(images)
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",  # Always 5 columns
                "gap": "5px",
                "padding": "5px",
                "justifyContent": "center",
                "alignItems": "center",
            },
        ),
        # Modal for displaying image details
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Article Title")),  # Static header
                dbc.ModalBody(id="modal-content"),
            ],
            id="image-modal",
            is_open=False,
            size="lg",  # Large modal size
        ),
    ]
)

# Callback to handle image click and open modal
@app.callback(
    Output("image-modal", "is_open"),
    Output("modal-content", "children"),
    [Input(f"img-{index}", "n_clicks") for index in range(len(images))],
    [State("image-modal", "is_open")],
)
def toggle_modal(*args):
    n_clicks = args[:-1]
    is_open = args[-1]
    # Check which image was clicked
    for i, click in enumerate(n_clicks):
        if click:
            return (
                not is_open,
                html.Div([
                    html.Img(src=images[i]['src'], style={"maxWidth": "100%"}),
                    html.P(f"This is {images[i]['alt']}", style={"color": "black"}),
                ])
            )
    return is_open, ""

# Run the app
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8053, debug=True)
