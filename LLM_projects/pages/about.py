from dash import html, register_page

# Register the page
register_page(__name__, path="/about")

def about_layout(app):
    about_layout = html.Div(
        [
            html.H1("About Us"),
            html.P("Learn more about our application here."),
        ]
    )
    return about_layout
