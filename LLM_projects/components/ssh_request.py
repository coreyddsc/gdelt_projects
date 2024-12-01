from dash import Dash, html, dcc, Input, Output, State

def ssh_text_summary(app):
    # Callback to send user input to Flask backend and display result
    @app.callback(
        Output("output-summary", "children"),
        Input("submit-button", "n_clicks"),
        State("input-text", "value"),
    )
    def summarize_text_via_backend(n_clicks, text):
        if n_clicks > 0 and text:
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