import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import plotly.express as px
from dash import html, register_page, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash_table
import json
# Register the page
register_page(__name__, path="/tSNE_news")

def tSNE_model(app):
    app.gkg.parse_gkg_field("allnames")
    app.gkg.vectorize_field(weight='weighted')
    app.gkgvf_arr = app.gkg.vectorized_df.copy()
    
    # Extract titles and labels
    titles = app.gkg.gkg_query['title'].tolist()
    labels = app.gkg.gkg_query['label']
    # Extract image URLs from app.images
    images = [image["src"] for image in app.images]  # Extract only the image URLs
    
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
    tsne_df['SourceImage'] = images  # Add the image URLs
    app.tsne_df = tsne_df  # Store the t-SNE results in the app object
    
    # Create 3D scatter plot
    app.tsne_fig = px.scatter_3d(
        tsne_df,
        x='TSNE1',
        y='TSNE2',
        z='TSNE3',
        color='Label',           # Use labels to color points
        hover_name='Title',      # Show article title on hover
        # hover_data={'SourceImage': True, 'Label':True},  # Hide the image URL
        labels={'TSNE1': 't-SNE Dimension 1', 'TSNE2': 't-SNE Dimension 2', 'TSNE3': 't-SNE Dimension 3'},
    )
        
    # Customize the layout for a transparent background and wireframe
    app.tsne_fig.update_layout(
        scene=dict(
            xaxis=dict(
                title='t-SNE Dimension 1',
                title_font=dict(color='white'),  # Change axis title to white
                tickfont=dict(color='white'),    # Change tick labels to white
                showgrid=True,                  # Keep the wireframe grid
                showline=False,                 # Remove axis lines
                zeroline=False,                 # Hide the origin line
                backgroundcolor="rgba(0, 0, 0, 0)",  # Transparent background
            ),
            yaxis=dict(
                title='t-SNE Dimension 2',
                title_font=dict(color='white'),  # Change axis title to white
                tickfont=dict(color='white'),    # Change tick labels to white
                showgrid=True,
                showline=False,
                zeroline=False,
                backgroundcolor="rgba(0, 0, 0, 0)",
            ),
            zaxis=dict(
                title='t-SNE Dimension 3',
                title_font=dict(color='white'),  # Change axis title to white
                tickfont=dict(color='white'),    # Change tick labels to white
                showgrid=True,
                showline=False,
                zeroline=False,
                backgroundcolor="rgba(0, 0, 0, 0)",
            ),
            bgcolor="rgba(0, 0, 0, 0)",  # Transparent background for the scene
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background for the entire figure
        legend=dict(
            font=dict(color='white')  # Change legend label color to white
        )
    )



# Define the layout for the tSNE page
def tSNE_layout(app):
    # Run the tSNE model
    tSNE_model(app)
    
    # Create a DataTable with pagination and sorting
    tsne_table = dash_table.DataTable(
        id='tsne-table',
        columns=[
            {'name': col, 'id': col} for col in app.tsne_df.columns
        ],
        data=app.tsne_df.to_dict('records'),
        style_table={'height': '400px', 'overflowY': 'auto'},  # Set the height of the table
        style_cell={'textAlign': 'left'},  # Text alignment in the table cells
        page_size=25,  # Number of rows per page
        sort_action='native',  # Enable sorting by clicking column headers
        sort_mode='multi',  # Allow sorting by multiple columns (optional)
        style_data={'whiteSpace': 'normal'},  # Wrap text in the table
    )
    
    # Define the modal for displaying clicked point information
    modal = dbc.Modal(
        [
            dbc.ModalBody(id="modal-content-tsne"),  # This will be dynamically updated
        ],
        id="info-modal",
        is_open=False,  # Initially closed
    )

    
    tSNE_layout = html.Div(
        [
            html.H1("tSNE News Clustering", className="dashboard-title"),
            html.Div(id="tSNE-content",
                    className="tSNE-content",
                    children=[
                        html.Div(id="tSNE-graph",
                                 className="tSNE-graph",
                                 children=[
                                    # show the tSNE figure
                                    dcc.Graph(id='tsne-3d-graph',
                                            figure=app.tsne_fig,
                                            style={'height': '100vh'}
                                    ),
                                 ]
                        ),
                        
                        
                    ]
            ),
            # tsne_table,
            modal,
        ]
    )
    return tSNE_layout


def summarize_text_via_backend(text):
        if text:
            import requests
            try:
                # Send text to Flask backend
                response = requests.post("http://127.0.0.1:8053/summarize", json={"text": text})
                if response.status_code == 200:
                    data = response.json()
                    return f"Summary result:\n{data.get('result', 'No result received')}"
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Failed to connect to the backend. Error: {e}"
        return "Enter text and click Summarize to process."


def extract_summary(input_text):
    # Find the start of the JSON part (it starts after the path and space)
    json_start = input_text.find("{")
    
    # Extract the JSON string from the input text
    json_string = input_text[json_start:]
    
    # Convert the JSON string to a dictionary
    try:
        summary_dict = json.loads(json_string)
        return summary_dict
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


def tSNE_scatter_modal(app):
    @callback(
        Output("info-modal", "is_open"),
        Output("modal-content-tsne", "children"),
        [Input("tsne-3d-graph", "clickData"),],
        [State("info-modal", "is_open")]
    )
    def toggle_modal(click_data, is_open):
        if click_data:  # A point was clicked
            point_info = click_data["points"][0]  # Get the first clicked point
            point_index = point_info.get("pointIndex")  # Attempt to get the index
            
            if point_index is None:  # Fallback if pointIndex is unavailable
                # Use x, y, z coordinates to identify the closest row in tsne_df
                x, y, z = point_info["x"], point_info["y"], point_info["z"]
                distances = ((app.tsne_df['TSNE1'] - x)**2 +
                            (app.tsne_df['TSNE2'] - y)**2 +
                            (app.tsne_df['TSNE3'] - z)**2)
                point_index = distances.idxmin()  # Index of the closest point
            
            # Retrieve data from tsne_df using the index
            row = app.tsne_df.iloc[point_index]
            
            # Use gkg tools to parse the soup of the clicked image url
            
            title = row['Title']
            # get index of row in gkg query with the same title
            gkg_index = app.gkg.gkg_query[app.gkg.gkg_query['title'] == title].index[0]
            app.gkg.parse_gkg_soup(url=app.gkg.urls[gkg_index],verbose=True)
            
            # paste together the paragraphs into a single string
            if app.ssh_connection_status:
                article_text = " ".join(app.gkg.parsed_paragraphs)
                summary_text = summarize_text_via_backend(article_text)
                summary_dict = extract_summary(summary_text)
                print(f"Summary: {summary_text}")
            else:
                summary_text = "Please connect to the SSH server to summarize the article."
                summary_dict = {"summary": summary_text}

            # Use the row data to construct modal content
            modal_content = html.Div(
                [
                    dbc.ModalTitle(
                        f"{app.images[gkg_index]['alt']}",
                        style={"color": "black", "textAlign": "center", 'font-size': '55px'}
                    ),
                    dcc.Markdown("---"),  # break line
                    html.Img(src=app.images[gkg_index]['src'], style={"maxWidth": "100%"}),
                    dcc.Markdown("---"),  # break line
                    # Create a container for the summary
                    html.Div([
                        html.H2("Summary", style={"margin-top": "20px","color": "black", "textAlign": "center", 'font-size': '45px'}),
                        html.P(summary_dict['summary']),
                    ]),
                    dcc.Markdown("---"),  # break line
                    # Create a parent container for the paragraphs
                    html.Div([
                        html.H2("Article", style={"margin-top": "20px","color": "black", "textAlign": "center", 'font-size': '45px'}),
                    ]),
                    html.Div(
                    [html.P(par) for par in app.gkg.parsed_paragraphs]),
                    dcc.Markdown("---"),  # break line
                    html.P(f"Label: {row['Label']}"),
                ]
            )
            return True, modal_content  # Open the modal with the updated content


        # Default: Do nothing
        return is_open, ""

