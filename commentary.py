import requests
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Polygon
from PIL import Image, ImageDraw, ImageEnhance
from matplotlib.animation import FuncAnimation
from matplotlib import patheffects
from io import BytesIO
from matplotlib.font_manager import FontProperties
import os

# Load BubblegumSans font
bubblegum_font = FontProperties(fname="assets/BubblegumSans-Regular.ttf")

# Base URL for fetching avatars with hardcoded revision 0
BASE_AVATAR_URL = "https://tetr.io/user-content/avatars/{USERID}.jpg?rv=0"

# Function to fetch TETR.IO user data from the correct API
def fetch_tetrio_user_data(user_id):
    api_url = f"https://ch.tetr.io/api/users/{user_id}"  # Correct API endpoint
    response = requests.get(api_url)
    if response.status_code == 200 and response.json().get('success'):
        return response.json().get('data')
    return None

# Function to extract avatar URL
def get_avatar_url(user_data):
    user_id = user_data['_id']  # Fetch user ID
    return BASE_AVATAR_URL.format(USERID=user_id)  # Return the avatar URL with revision 0

# Function to extract all social connections or fallback, limit to 3
def get_social_connections(user_data):
    connections = user_data.get('connections', {})
    social_list = []
    
    if 'discord' in connections:
        social_list.append(f"Discord: {connections['discord'].get('display_username')}")
    if 'twitch' in connections:
        social_list.append(f"Twitch: {connections['twitch'].get('display_username')}")
    if 'twitter' in connections:
        social_list.append(f"Twitter: {connections['twitter'].get('display_username')}")
    if 'reddit' in connections:
        social_list.append(f"Reddit: {connections['reddit'].get('display_username')}")
    if 'youtube' in connections:
        social_list.append(f"YouTube: {connections['youtube'].get('display_username')}")
    if 'steam' in connections:
        social_list.append(f"Steam: {connections['steam'].get('display_username')}")
    
    return social_list[:3]  # Limit to a maximum of 3 social connections

# Function to load GIF and return the frames as a list
def load_gif_frames(gif_path):
    gif = Image.open(gif_path)
    frames = []
    try:
        while True:
            frame = gif.copy().convert("RGBA")  # Ensure it is in RGBA format for transparency
            frames.append(frame)
            gif.seek(len(frames))  # Move to next frame
    except EOFError:
        pass  # End of GIF reached
    return frames

# Function to update the background frame
def update_frame(frame_num, img, frames):
    img.set_data(frames[frame_num])

# Function to add text with shadow and use the BubblegumSans font
def add_text_with_style(ax, text, position, fontsize=24, color='black', shadow_color='gray', box_facecolor=None):
    if box_facecolor:
        # Add rounded box with padding
        ax.text(position[0], position[1], text, fontsize=fontsize, fontweight='bold',
                ha='center', va='center', color=color, transform=ax.transAxes,
                fontproperties=bubblegum_font,
                bbox=dict(facecolor=box_facecolor, edgecolor='black', boxstyle='round,pad=0.6', alpha=0.85))
    else:
        # Add shadow effect
        ax.text(position[0], position[1], text, fontsize=fontsize, fontweight='bold',
                ha='center', va='center', color=shadow_color, transform=ax.transAxes,
                fontproperties=bubblegum_font, 
                path_effects=[patheffects.withStroke(linewidth=4, foreground=shadow_color)])
        # Add primary text
        ax.text(position[0], position[1], text, fontsize=fontsize, fontweight='bold',
                ha='center', va='center', color=color, transform=ax.transAxes,
                fontproperties=bubblegum_font)

# Function to create diamond-shaped avatars with a larger border and thinner outline
def diamond_avatar_with_border(img, size, border_thickness=5, outer_padding=20):
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    border_size = size + 2 * (border_thickness + outer_padding)  # Add padding for space around the border
    border_img = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))  # Larger image for the border
    mask = Image.new('L', (size, size), 0)  # Mask only for the diamond size
    draw = ImageDraw.Draw(mask)

    # Draw the diamond shape on the mask
    draw.polygon([(size // 2, 0), (size, size // 2), (size // 2, size), (0, size // 2)], fill=255)

    # Paste the avatar onto the border image with proper spacing
    border_img.paste(img, (outer_padding + border_thickness, outer_padding + border_thickness), mask=mask)
    
    # Draw the thinner black border with more space
    draw = ImageDraw.Draw(border_img)
    draw.polygon([(border_size // 2, outer_padding),
                  (border_size - outer_padding, border_size // 2),
                  (border_size // 2, border_size - outer_padding),
                  (outer_padding, border_size // 2)], outline="black", width=border_thickness)

    return border_img

# Function to dynamically create the commentary scene with animated GIF background
def create_commentary_scene(user_ids, logo_path, gif_path, tournament_title="COMMENTATORS"):
    # Load the GIF frames
    gif_frames = load_gif_frames(gif_path)
    frame_count = len(gif_frames)

    # Set figure size to match the GIF dimensions (width x height)
    fig_width = 19.2  # Example width for 1920px
    fig_height = 10.8  # Example height for 1080px
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))  # Set size for 1920x1080 screen

    # Set limits to match the dimensions of the background
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')  # Maintain the aspect ratio
    ax.axis('off')  # Hide the axes

    # Initialize the first frame of the GIF
    img = ax.imshow(gif_frames[0], extent=[0, 1, 0, 1], aspect='auto')

    # Subtle shadow border around the entire commentator section
    ax.add_patch(Polygon([[0.05, 0.05], [0.95, 0.05], [0.95, 0.85], [0.05, 0.85]],
                         closed=True, fill=False, edgecolor='lightgray', linewidth=3))

    # Add the tournament logo with reduced saturation
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((80, 80), Image.Resampling.LANCZOS)
    logo = ImageEnhance.Color(logo).enhance(0.5)  # Reduced saturation of the logo
    imagebox = OffsetImage(logo, zoom=1)
    ab = AnnotationBbox(imagebox, (0.08, 0.08), frameon=False)
    ax.add_artist(ab)

    # Add the "COMMENTATORS" text at the top with a subtle shadow effect using BubblegumSans
    add_text_with_style(ax, tournament_title, (0.5, 0.9), fontsize=42, color='#FFD700', shadow_color='gray')

    # Apple-themed color scheme for the text boxes
    color_primary = '#FF6347'  # Apple Red for usernames
    color_social = '#7CFC00'  # Apple Green for handles and social connections

    positions = [(0.3, 0.60), (0.7, 0.60)]  # Adjust positions for 2 commentators
    avatar_size = 200  # Slightly increased avatar size for prominence

    frames_to_save = []  # To store frames for the GIF

    for i, user_id in enumerate(user_ids):
        user_data = fetch_tetrio_user_data(user_id)
        
        if user_data:
            avatar_url = get_avatar_url(user_data)
        else:
            avatar_url = 'assets/apple.png'  # Local fallback avatar if no avatar is present

        try:
            avatar_response = requests.get(avatar_url, stream=True)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        except Exception:
            avatar_img = Image.open('assets/apple.png')  # Fallback in case of failure

        diamond_avatar_img = diamond_avatar_with_border(avatar_img, avatar_size, border_thickness=5, outer_padding=20)
        imagebox = OffsetImage(diamond_avatar_img, zoom=1)
        ab = AnnotationBbox(imagebox, positions[i], frameon=False)
        ax.add_artist(ab)

        if user_data:
            socials = get_social_connections(user_data)
            username = user_data['username']  
        else:
            socials = []
            username = f"User{i+1}"

        # Add text boxes for username, with consistent spacing between the username and socials
        add_text_with_style(ax, username, (positions[i][0], 0.35), fontsize=26, color='white', shadow_color='black', box_facecolor=color_primary)

        # Display socials (including handle), limit to 3
        max_socials = min(len(socials), 3)  # Cap socials to a maximum of 3
        for j in range(max_socials):
            social_position = 0.27 - (0.07 * j)  # Move socials up for better alignment
            add_text_with_style(ax, socials[j], (positions[i][0], social_position), fontsize=20, color='white', shadow_color='black', box_facecolor=color_social)

    # Capture frames for the GIF
    for frame in gif_frames:
        img.set_data(frame)
        plt.draw()
        plt.pause(0.1)  # Pause to allow the image to update
        # Save the current figure to a temporary file
        temp_file = BytesIO()
        plt.savefig(temp_file, format='png', bbox_inches='tight', pad_inches=0)
        temp_file.seek(0)
        frames_to_save.append(Image.open(temp_file).convert("RGBA"))

    # Create a GIF from the frames
    output_gif_path = os.path.join("scenes", "commentary_scene.gif")
    frames_to_save[0].save(output_gif_path, save_all=True, append_images=frames_to_save[1:], optimize=False, duration=100, loop=0)

    plt.show()

# Example inputs with real TETR.IO user IDs
user_ids = ["5ec684620cfca96246aa9bda", "5f3718f11fee2b2e8c27d55f"]  
logo_path = 'assets/apple.png'  
gif_path = 'assets/bg.gif'  

# Call the function to generate the commentary screen
create_commentary_scene(user_ids, logo_path, gif_path)
