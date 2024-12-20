import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageSequence
from player_cards import create_player_card  # Import your refactored function

# Function to add a glow effect to text
def add_glow(base_image, text, position, font, glow_color, glow_strength=5):
    # Create a temporary image to draw the glowing text on
    glow_image = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_image)
    
    # Draw multiple layers of the text to create the glow effect
    for offset in range(glow_strength):
        glow_draw.text((position[0] - offset, position[1] - offset), text, font=font, fill=glow_color)
        glow_draw.text((position[0] + offset, position[1] + offset), text, font=font, fill=glow_color)

    # Apply a blur filter to the glow image to soften the edges
    glow_image = glow_image.filter(ImageFilter.GaussianBlur(radius=glow_strength))
    
    # Overlay the glow image onto the base image
    base_image.paste(glow_image, (0, 0), glow_image)

# Function to load versus data from JSON
def load_versus_data(file_path="versus_data.json"):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

# Function to create the versus screen for each frame of the animated GIF
def create_versus_screen(data):
    # Open the animated background GIF
    background_gif = Image.open("assets/bg.gif")
    
    # Initialize a list to store all the frames
    frames = []
    
    margin = 20  # Margin to leave space between cards and edges

    # Extract player data
    player1 = data["player1"]
    player2 = data["player2"]

    # Generate the player cards using the create_player_card function
    card1 = create_player_card(player1["user_id"], player1["seed"], player1["flavour_text"])
    card2 = create_player_card(player2["user_id"], player2["seed"], player2["flavour_text"])

    # Resize the cards to match the height of the screen (1080)
    new_height = background_gif.height
    card1 = card1.resize((background_gif.width // 3, new_height - 2 * margin))  # Cards will take up 1/3 of the width
    card2 = card2.resize((background_gif.width // 3, new_height - 2 * margin))

    # Define positions for the player cards (left and right sides, leaving margin)
    card1_x = margin  # Left side of the screen with margin
    card1_y = margin
    card2_x = background_gif.width - card2.width - margin  # Right side with margin
    card2_y = margin

    # Load the font for the VS text
    font_vs = ImageFont.truetype(r"assets/VCR_OSD_MONO_1.001[1].ttf", 450)  # Increase font size and use the correct font
    vs_text = "VS"

    # Load and resize the logo
    logo = Image.open("assets/tournament_logo.png").convert("RGBA")
    logo_size = 350  # Increased logo size for better visibility
    logo = logo.resize((logo_size, logo_size))

    # Process each frame of the background GIF
    for frame in ImageSequence.Iterator(background_gif):
        # Convert the current frame to RGBA (if it isn't already)
        frame = frame.convert("RGBA")
        
        # Create a drawing context
        draw = ImageDraw.Draw(frame)

        # Paste the player cards onto the current frame
        frame.paste(card1, (card1_x, card1_y), card1)
        frame.paste(card2, (card2_x, card2_y), card2)

        # Calculate the position to center the VS text using textbbox
        vs_bbox = draw.textbbox((0, 0), vs_text, font=font_vs)
        vs_width = vs_bbox[2] - vs_bbox[0]
        vs_height = vs_bbox[3] - vs_bbox[1]
        vs_x = (background_gif.width - vs_width) // 2
        vs_y = (background_gif.height - vs_height) // 2 - 100  # Shift the VS text upwards slightly

        # Draw shadow for VS text
        draw.text((vs_x + 5, vs_y + 5), vs_text, fill=(0, 0, 0, 150), font=font_vs)  # Shadow offset by 5 pixels

        # Add glow effect for the VS text
        add_glow(frame, vs_text, (vs_x, vs_y), font_vs, glow_color=(255, 255, 255, 255), glow_strength=10)

        # Draw the actual VS text
        draw.text((vs_x, vs_y), vs_text, fill=(255, 255, 255), font=font_vs)

        # Calculate position for the logo to align with the bottom of the player cards
        logo_x = (background_gif.width - logo.width) // 2
        logo_y = card1_y + card1.height - logo.height - margin  # Align the logo's bottom with the player cards' bottom

        # Paste the logo onto the frame
        frame.paste(logo, (logo_x, logo_y), logo)

        # Append the frame to the list
        frames.append(frame)

    # Save the final animated GIF
    frames[0].save('scenes/versus_screen.gif', save_all=True, append_images=frames[1:], duration=background_gif.info['duration'], loop=0)

if __name__ == "__main__":
    # Load data from JSON file
    data = load_versus_data()

    # Create the versus screen
    create_versus_screen(data)
