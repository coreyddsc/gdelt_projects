import dash
from dash import Input, Output, State, html, dcc
from components.login import *
import feffery_antd_components as fac

# Define the sidebar function using fac
def sidebar(app):
    app.menu_items = [
        {"key": icon, "icon": icon}
        for icon in [
            "antd-home",
            "antd-cloud-upload",
            "antd-bar-chart",
            "antd-pie-chart",
            "antd-line-chart",
            "antd-calculator",
            "antd-database",
            "antd-history",
        ]
    ]

    return html.Div(
        [
            # Sidebar (AntdSider)
            fac.AntdSider(
                [
                    fac.AntdMenu(
                        menuItems=[
                            {
                                'component': 'Item',
                                'props': {
                                    'key': item['key'],
                                    'icon': item['icon'],
                                    'title': item['key'].replace('antd-', '').replace('-', ' ').capitalize(),
                                },
                            }
                            for item in app.menu_items
                        ],
                        mode='inline',
                        style={'height': '100%', 'overflow': 'hidden auto'},
                    ),
                ],
                collapsed=True,
                collapsible=True,
                collapsedWidth=40,
                style={
                    'backgroundColor': 'rgb(240, 242, 245)',
                    'transition': 'all 0.3s ease',
                    'position': 'fixed',  # Fix sidebar position
                    'top': 0,
                    'left': 0,
                    'bottom': 0,
                    'zIndex': 1000,  # Ensure it is above other content
                    'width': '250px',  # You can adjust this width
                },
            ),
        ],
        id="sidebar-wrapper",
    )
    
    

def navigation_icon(app):
    # SVG button in the top-left corner
    app.navigation_icon = html.Div(
        children=[
            html.Button(
                children=[
                    html.ObjectEl(
                        type="image/svg+xml",
                        data="/assets/extracted_region.png",  # Reference to the SVG in the assets folder
                        width="150px",  # Adjust width as necessary
                        height="150px",  # Adjust height as necessary
                    )
                ],
                id="svg-button",  # Optional ID for the button
                style={
                    "position": "fixed",
                    "top": "20px",  # Adjust the top margin to position the button
                    "left": "20px",  # Adjust the left margin to position the button
                    "border": "none",
                    "background": "transparent",
                    "cursor": "pointer",
                    "z-index": "9999",  # Bring to the front by setting a high z-index
                    # "box-shadow": "4px 4px 10px rgba(0, 0, 0, 0.3)",  # Shadow effect
                },
                n_clicks=0  # This tracks the number of clicks, if needed
            )
        ]
    )
    return app.navigation_icon


# Define the callback to toggle the sidebar (no longer needed as the sidebar already has the collapsible feature)
def sidebar_callbacks(app):
    pass

