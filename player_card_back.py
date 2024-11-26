from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import os

# Paths to assets
background_apple_path = "assets/apple.png"  # Path to apple icon
font_path = "assets/VCR_OSD_MONO_1.001[1].ttf"  # Path to font
logo_path = "assets/tournament_logo.png"  # Tournament logo
output_path = "assets/player_card_back.png"  # Output path to save the image

# Card dimensions
card_width = 400
card_height = 700
corner_radius = 20  # Rounded corners
border_thickness = 12  # Border thickness


# Function to create a rounded rectangle mask
def create_rounded_rectangle_mask(width, height, radius):
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width, height), radius, fill=255)
    return mask


# Function to create a gradient background
def create_gradient(width, height, top_color, bottom_color):
    base = Image.new("RGBA", (width, height), top_color)
    gradient = Image.new("RGBA", (width, height), bottom_color)
    for y in range(height):
        blend = int((y / height) * 255)
        blended_color = tuple([
            int(top_color[i] * (1 - blend / 255) + bottom_color[i] * (blend / 255))
            for i in range(3)
        ]) + (255,)
        gradient.paste(blended_color, (0, y, width, y + 1))
    return Image.alpha_composite(base, gradient)


# Function to create an apple pattern
def create_apple_pattern(base_image, tile_size, canvas_size, alpha=80):
    pattern = Image.new("RGBA", canvas_size, (0, 0, 0, 0))  # Transparent base
    apple = base_image.resize(tile_size, Image.Resampling.LANCZOS)  # Resize apple icon

    # Apply transparency by modifying the alpha channel
    apple = apple.copy()
    alpha_channel = apple.split()[-1].point(lambda p: p * (alpha / 255))  # Scale alpha channel
    apple.putalpha(alpha_channel)

    # Tile the apple across the canvas
    for x in range(0, canvas_size[0], tile_size[0]):
        for y in range(0, canvas_size[1], tile_size[1]):
            pattern.paste(apple, (x, y), apple)
    return pattern


# Function to generate the back of the player card
def save_player_card_back():
    # Create the base gradient background
    gradient_background = create_gradient(
        card_width - 2 * border_thickness, 
        card_height - 2 * border_thickness,
        (60, 60, 60, 255),  # Dark gray (top)
        (44, 44, 44, 255)   # Darker gray (bottom)
    )

    # Add apple pattern
    if background_apple_path:
        apple_icon = Image.open(background_apple_path).convert("RGBA")
        apple_pattern = create_apple_pattern(
            apple_icon, (40, 40), (card_width - 2 * border_thickness, card_height - 2 * border_thickness), alpha=80
        )
        gradient_background = Image.alpha_composite(gradient_background, apple_pattern)

    # Add orange border
    card = Image.new("RGBA", (card_width, card_height), (255, 165, 0, 255))  # Orange background

    # Paste the gradient with apple pattern onto the card
    inner_x = border_thickness
    inner_y = border_thickness
    card.paste(gradient_background, (inner_x, inner_y), gradient_background)

    # Add rounded corners
    mask = create_rounded_rectangle_mask(card_width, card_height, corner_radius)
    card.putalpha(mask)

    # Add central tournament logo
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((150, 150), Image.Resampling.LANCZOS)  # Resize logo
        logo_position = (
            (card_width - logo.width) // 2,
            (card_height - logo.height) // 2 + 50,  # Adjusted position to fit the text
        )
        card.paste(logo, logo_position, logo)

    # Add "APPLE ORCHARD CUP" text at the top (multiline)
    draw = ImageDraw.Draw(card)
    if font_path:
        font_size = 60  # Start with a larger font size
        font = ImageFont.truetype(font_path, font_size)
        text_top = "APPLE"
        text_bottom = "ORCHARD CUP"
        
        # Measure the bounding box for both lines
        text_top_bbox = draw.textbbox((0, 0), text_top, font=font)
        text_bottom_bbox = draw.textbbox((0, 0), text_bottom, font=font)
        
        # Ensure the text fits horizontally within the card width
        text_top_width = text_top_bbox[2] - text_top_bbox[0]
        text_bottom_width = text_bottom_bbox[2] - text_bottom_bbox[0]
        while text_top_width > card_width - 40 or text_bottom_width > card_width - 40:  # Adjust size if needed
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
            text_top_bbox = draw.textbbox((0, 0), text_top, font=font)
            text_bottom_bbox = draw.textbbox((0, 0), text_bottom, font=font)
            text_top_width = text_top_bbox[2] - text_top_bbox[0]
            text_bottom_width = text_bottom_bbox[2] - text_bottom_bbox[0]

        # Position the text (about a third of the way down)
        text_top_position = ((card_width - text_top_width) // 2, card_height // 3 - text_top_bbox[3] // 2)
        text_bottom_position = ((card_width - text_bottom_width) // 2, card_height // 3 + text_top_bbox[3] // 2)

        # Draw the text
        draw.text(text_top_position, text_top, fill="white", font=font)
        draw.text(text_bottom_position, text_bottom, fill="white", font=font)

    # Save the card as a PNG
    card.save(output_path)
    print(f"Player card back saved as {output_path}")


# Generate and save the player card back
save_player_card_back()
