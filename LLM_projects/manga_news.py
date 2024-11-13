import streamlit as st
import pandas as pd

# Sample data to replicate `gkg_op` structure
gkg_op = pd.read_csv('manga_soup_labeled.csv')

# subset gkg_op to only include rows with images
gkg_op = gkg_op[gkg_op['sharingimage'].notnull()]


# Set up page layout and title
st.set_page_config(page_title="One Piece Image Grid", layout="wide")
# st.title("One Piece Image Grid")

# Display the images in a grid-like structure using columns
num_columns = 3  # You can adjust this based on the number of images or your preference

# Create image grid
cols = st.columns(num_columns)

# for idx, (_, row) in enumerate(gkg_op.iterrows()):
#     with cols[idx % num_columns]:  # Distribute images across columns
#         st.markdown(f"### [{row['title']}]({row['documentidentifier']})", unsafe_allow_html=True)
#         st.image(row['sharingimage'], use_column_width=True)

for idx, (_, row) in enumerate(gkg_op.iterrows()):
    with cols[idx % num_columns]:  # Distribute images across columns
        # Create HTML for image with title overlay
        image_html = f"""
        <div style="position: relative; display: inline-block;">
            <img src="{row['sharingimage']}" style="width: 100%; height: auto;">
            <div style="position: absolute; bottom: 10px; left: 10px; background-color: rgba(0, 0, 0, 0.6); color: white; padding: 5px; font-size: 16px;">
                <a href="{row['documentidentifier']}" target="_blank" style="color: white; text-decoration: none;">{row['title']}</a>
            </div>
        </div>
        """
        st.markdown(image_html, unsafe_allow_html=True)