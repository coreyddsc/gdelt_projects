from components.main_modal import * # Import the main_modal_callbacks function and image grid layout
from components.image_grid import * # Import the image grid layout

from dash import html, register_page

# Register the page
register_page(__name__, path="/")


def news_grid_layout(app):
    news_grid_layout = html.Div([
        html.H1(
            "ONE PIECE NEWS DASHBOARD!",
            className="dashboard-title",
        ),
        image_grid(app),
        main_modal(app)
        ])  # Create the layout
    return news_grid_layout