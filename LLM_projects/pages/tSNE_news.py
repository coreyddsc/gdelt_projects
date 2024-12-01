from dash import html, register_page

# Register the page
register_page(__name__, path="/tSNE_news")

def tSNE_layout(app):
    tSNE_layout = html.Div(
        [
            html.H1("tSNE News Clustering", className="dashboard-title"),
        ]
    )
    return tSNE_layout