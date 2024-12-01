from dash import html, register_page

# Register the page
register_page(__name__, path="/contact_info")

def contact_layout(app):
    contact_layout = html.Div(
        [
            html.H1("Contact Information"),
            html.P("For more information, please contact us at:"),
        ]
    )
    return contact_layout