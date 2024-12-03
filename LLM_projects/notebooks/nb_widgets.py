import ipywidgets as widgets
from IPython.display import display

def create_dropdown_widget(options):
    """
    Creates a dropdown widget and attaches a change handler.
    
    Args:
        options (list): List of options for the dropdown.
        
    Returns:
        widgets.Dropdown: The created dropdown widget.
    """
    dropdown = widgets.Dropdown(
        options=options,          # List of dropdown options
        value='allnames',         # Default value
        description='Select:',    # Label for the dropdown
        disabled=False            # Enable or disable the dropdown
    )

    # Define a function to handle dropdown selection
    def on_change(change):
        if change['type'] == 'change' and change['name'] == 'value':
            print(f"Selected option: {change['new']}")

    # Attach the handler to the dropdown
    dropdown.observe(on_change)
    
    # Display the dropdown in the notebook
    display(dropdown)
    
    return dropdown
