import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import plotly.express as px
from dash import html, register_page, dcc
import dash_bootstrap_components as dbc
# Register the page
register_page(__name__, path="/tSNE_news")

def tSNE_model(app):
    app.gkg.parse_gkg_field("allnames")
    app.gkg.vectorize_field(weight='weighted')
    app.gkgvf_arr = app.gkg.vectorized_df.copy()
    
    # Extract titles and labels
    titles = app.gkg.gkg_query['title'].tolist()
    labels = app.gkg.gkg_query['label']
    
    # Step 2: Use t-SNE to reduce dimensions
    tsne_model = TSNE(n_components=3, perplexity=30, random_state=42, n_iter=1000)
    tsne_results = tsne_model.fit_transform(app.gkgvf_arr.values)
    
    # Step 3: Normalize the t-SNE output
    scaler = MinMaxScaler()
    tsne_scaled = scaler.fit_transform(tsne_results)
    
    # Create a DataFrame for the t-SNE results
    tsne_df = pd.DataFrame(tsne_scaled, columns=['TSNE1', 'TSNE2', 'TSNE3'])
    tsne_df['Title'] = titles  # Optionally add titles as a label
    tsne_df['Label'] = labels  # Add labels as a new column
    app.tsne_df = tsne_df  # Store the t-SNE results in the app object
    
    # Create 3D scatter plot
    app.tsne_fig = px.scatter_3d(
        tsne_df,
        x='TSNE1',
        y='TSNE2',
        z='TSNE3',
        color='Label',           # Use labels to color points
        hover_name='Title',      # Show article title on hover
        labels={'TSNE1': 't-SNE Dimension 1', 'TSNE2': 't-SNE Dimension 2', 'TSNE3': 't-SNE Dimension 3'},
    )
    
    # Customize the layout for a transparent background and wireframe
    app.tsne_fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='t-SNE Dimension 1',
                showgrid=True,    # Keep the wireframe grid
                showline=False,   # Remove axis lines
                zeroline=False,   # Hide the origin line
                backgroundcolor="rgba(0, 0, 0, 0)",  # Transparent
            ),
            yaxis=dict(
                title='t-SNE Dimension 2',
                showgrid=True,
                showline=False,
                zeroline=False,
                backgroundcolor="rgba(0, 0, 0, 0)",
            ),
            zaxis=dict(
                title='t-SNE Dimension 3',
                showgrid=True,
                showline=False,
                zeroline=False,
                backgroundcolor="rgba(0, 0, 0, 0)",
            ),
            bgcolor="rgba(0, 0, 0, 0)",  # Transparent background for the scene
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background for the entire figure
    )

def tSNE_layout(app):
    tSNE_model(app)
    tSNE_layout = html.Div(
        [
            html.H1("tSNE News Clustering", className="dashboard-title"),
            html.Div(id="tSNE-content",
                    className="tSNE-content",
                    children=[
                        html.Div(id="tSNE-graph"),
                        # table to display the tSNE results
                        # dbc.Table.from_dataframe(app.tsne_df.head(), striped=True, bordered=True, hover=True),
                        # show the tSNE figure
                        dcc.Graph(id='tsne-3d-graph',
                                figure=app.tsne_fig,
                                style={'height': '100vh'}),
                    ]),
        ]
    )
    return tSNE_layout