from PIL import Image, ImageDraw, ImageFont

def text_to_image(text, font_path, font_size=50, text_color=(255, 255, 255), bg_color=(0, 0, 0, 0), padding=10, output_path=None):
    """
    Creates an image with the given text using a specific font, and applies transparency
    to the background around the text.

    Args:
        text (str): The text to render.
        font_path (str): Path to the .ttf font file.
        font_size (int): Font size for rendering the text.
        text_color (tuple): Color of the text in RGB (default: white).
        bg_color (tuple): Background color as RGBA (default: transparent).
        padding (int): Extra space around the text to make the box bigger (default: 10).
        output_path (str, optional): File path to save the generated image. If None, returns the image.

    Returns:
        PIL.Image.Image: The generated image if output_path is None.
    """
    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    
    # Calculate the size of the text using textbbox
    dummy_image = Image.new("RGBA", (1, 1), bg_color)
    draw = ImageDraw.Draw(dummy_image)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    
    # Add padding to the text size
    img_width = text_width + 5 * padding
    img_height = text_height + 10 * padding

    # Create a new image with the adjusted size
    img = Image.new("RGBA", (img_width, img_height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calculate the position to center the text in the image
    x_position = (img_width - text_width) // 2
    y_position = (img_height - text_height) // 2
    
    # Draw the text at the calculated position
    draw.text((x_position, y_position), text, font=font, fill=text_color)
    
    # Save or return the image
    if output_path:
        img.save(output_path)
        print(f"Image saved to {output_path}")
    else:
        return img

# Example usage
if __name__ == "__main__":
    text = "Beautifulsoup"
    font_path = r"C:\Users\Corey Dearing\Desktop\gdelt\LLM_projects\assets\one_piece_font.ttf"  # Absolute path to your font
    output_image = text_to_image(text, font_path, font_size=120, text_color=(0, 0, 0), output_path="assets/beautifulsouptext.png")
    # output_image.show()  # Show the image if no output_path is specified
