from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

# Import the create_player_card function from player_cards.py
from player_cards import create_player_card

# Generate the front of the card using user_id and seed_value
user_id = "cheezwhiz"
seed_value = 1
flavour_text = "[EX] Ability: 6-3"

# Call create_player_card to generate the front card image
front_card_image = create_player_card(user_id, seed_value, flavour_text)

# Load the card back image (created earlier) from assets/player_card_back.png
card_back = Image.open("assets/player_card_back.png")

# Dynamically fetch the size of the card for alignment
card_width, card_height = front_card_image.size

# Card flip animation parameters
num_frames = 60  # Total frames in the animation (one flip)
card_position = (600, 450)  # Fixed position for the card (centered in frame)
flip_speed_factor = 4  # Flip is four times faster


def generate_frame(progress):
    # Adjust progress to make the flip faster
    adjusted_progress = (progress * flip_speed_factor) % 1  # Loop the progress after 1 cycle
    angle = 180 - (adjusted_progress * 180)  # Flip angle (from 180 to 0 degrees)
    
    # Determine which side of the card to show (front or back)
    if angle > 90:
        card_to_show = card_back  # Show the back of the card
        current_width, current_height = card_back.size
    else:
        card_to_show = front_card_image  # Show the front of the card
        current_width, current_height = card_width, card_height

    # Simulate the horizontal flip by resizing only the width
    scale = abs(np.cos(np.radians(angle)))  # Width scale changes with angle
    card_resized = card_to_show.resize((int(current_width * scale), current_height))  # Resize width only
    
    # Create a blank frame and paste the flipped card
    frame_image = Image.new("RGBA", (1200, 900), (255, 255, 255, 0))  # Adjust background size
    card_x = card_position[0] - card_resized.size[0] // 2  # Center the card horizontally
    card_y = card_position[1] - card_resized.size[1] // 2  # Center the card vertically
    frame_image.paste(card_resized, (card_x, card_y), card_resized)
    
    return frame_image


# Function to update the frame for preview
def update(frame_idx):
    # Calculate progress
    progress = frame_idx / (num_frames - 1)  # Calculate progress normally
    frame_image = generate_frame(progress)
    plt.clf()  # Clear the previous frame
    plt.imshow(frame_image)
    plt.axis('off')


# Save the animation as a GIF
def save_animation():
    fig = plt.figure(figsize=(12, 9))  # Increase figure size for better visualization
    ani = FuncAnimation(fig, update, frames=num_frames, interval=50, repeat=False)  # No repeat for single flip

    # Save the animation as a GIF
    ani.save("assets/card_flip_animation.gif", writer="imagemagick", fps=20)  # Save GIF to assets folder
    print("Animation saved as 'card_flip_animation.gif' in the assets folder.")

# Generate and save the animation
save_animation()
