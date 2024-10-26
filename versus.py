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

# Function to create the versus screen for each frame of the animated GIF
def create_versus_screen(user1_id, seed1, user2_id, seed2):
    # Open the animated background GIF
    background_gif = Image.open("assets/bg.gif")
    
    # Initialize a list to store all the frames
    frames = []

    # Generate the player cards using the create_player_card function
    card1 = create_player_card(user1_id, seed1)
    card2 = create_player_card(user2_id, seed2)

    # Resize the cards to match the height of the screen (1080)
    new_height = background_gif.height
    card1 = card1.resize((background_gif.width // 3, new_height))  # Cards will take up 1/3 of the width
    card2 = card2.resize((background_gif.width // 3, new_height))

    # Define positions for the player cards (left and right sides)
    card1_x = 0  # Left side of the screen
    card1_y = 0
    card2_x = background_gif.width - card2.width  # Right side of the screen
    card2_y = 0

    # Load the font for the VS text
    font_vs = ImageFont.truetype("assets/BubblegumSans-Regular.ttf", 250)  # Increase font size and use the correct font
    vs_text = "VS"

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
        vs_y = (background_gif.height - vs_height) // 2

        # Draw shadow for VS text
        draw.text((vs_x + 5, vs_y + 5), vs_text, fill=(0, 0, 0, 150), font=font_vs)  # Shadow offset by 5 pixels

        # Add glow effect for the VS text
        add_glow(frame, vs_text, (vs_x, vs_y), font_vs, glow_color=(255, 255, 255, 255), glow_strength=10)

        # Draw the actual VS text
        draw.text((vs_x, vs_y), vs_text, fill=(255, 255, 255), font=font_vs)

        # Append the frame to the list
        frames.append(frame)

    # Save the final animated GIF
    frames[0].save('scenes/versus_screen.gif', save_all=True, append_images=frames[1:], duration=background_gif.info['duration'], loop=0)

if __name__ == "__main__":
    # User IDs and seeds for both players
    user1_id = "5ec684620cfca96246aa9bda"  # Replace with actual user1 ID
    seed1 = 1

    user2_id = "5f3718f11fee2b2e8c27d55f"  # Replace with actual user2 ID
    seed2 = 8

    # Create the versus screen
    create_versus_screen(user1_id, seed1, user2_id, seed2)
