import dash
from dash import Dash, html, Input, Output, State, callback_context, dcc

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