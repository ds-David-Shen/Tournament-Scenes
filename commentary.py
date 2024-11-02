import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Polygon
from PIL import Image, ImageDraw, ImageFilter, ImageSequence
from io import BytesIO
import matplotlib.animation as animation
from matplotlib.font_manager import FontProperties
from matplotlib import patheffects
import os
import requests
import json

# Load VCR_OSD_MONO font
vcr_font = FontProperties(fname=r"assets/VCR_OSD_MONO_1.001[1].ttf")

# Cache for avatar images to avoid repeated downloads
avatar_cache = {}

# Function to check if character can be rendered
def can_render_text(char, font):
    fig, ax = plt.subplots()
    text = ax.text(0.5, 0.5, char, fontproperties=font)
    renderer = fig.canvas.get_renderer()
    bbox = text.get_window_extent(renderer)
    plt.close(fig)
    return bbox.width > 0 and bbox.height > 0

# Function to clean unsupported characters
def clean_text(text, font):
    return ''.join([char for char in text if can_render_text(char, font)])

# Fetch Tetr.io user data and cache avatar URLs
def fetch_cached_user_data(user_id):
    if user_id in avatar_cache:
        return avatar_cache[user_id]
    
    api_url = f"https://ch.tetr.io/api/users/{user_id}"
    response = requests.get(api_url)
    if response.status_code == 200 and response.json().get('success'):
        user_data = response.json().get('data')
        avatar_url = f"https://tetr.io/user-content/avatars/{user_data['_id']}.jpg?rv=0"
        avatar_cache[user_id] = (user_data, avatar_url)
        return user_data, avatar_url
    return None, 'assets/apple.png'

# Load avatar image from URL or fallback
def load_avatar_image(avatar_url):
    try:
        response = requests.get(avatar_url, stream=True)
        avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception:
        avatar_img = Image.open('assets/apple.png')
    return avatar_img

# Draw polished border
def draw_polished_border(ax):
    border_thickness = 5
    rounded_rect = plt.Rectangle((0.05, 0.05), 0.90, 0.82, fill=False, 
                                 edgecolor='#FFD700', linewidth=border_thickness,
                                 linestyle='-', zorder=1)
    ax.add_patch(rounded_rect)
    
    shadow_rect = plt.Rectangle((0.055, 0.045), 0.90, 0.82, fill=False,
                                edgecolor='#FFA500', linewidth=border_thickness + 2, 
                                alpha=0.3, zorder=0)
    ax.add_patch(shadow_rect)

# Add logo
def add_logo(ax, logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((80, 80), Image.Resampling.LANCZOS)
    imagebox = OffsetImage(logo, zoom=1)
    ab = AnnotationBbox(imagebox, (0.97, 0.92), frameon=False, xycoords='axes fraction')
    ax.add_artist(ab)

# Add text with glow effect
def add_text_with_glow(ax, text, position, fontsize=48, color='#333333', glow_color='#AAAAAA', shadow_color='#222222'):
    clean_txt = clean_text(text, vcr_font)
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=glow_color, transform=ax.transAxes,
            fontproperties=vcr_font,
            path_effects=[patheffects.withStroke(linewidth=4, foreground=shadow_color)])
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=color, transform=ax.transAxes,
            fontproperties=vcr_font)

# Add social icon and text with box
def add_social_icon_and_text(ax, logo_path, username, position, avatar_left_position, fontsize=24, icon_size=0.25, color='#333333', glow_color='#444444', shadow_color='#111111', box_facecolor='#FFD700'):
    avatar_left_position -= 0.11

    logo_img = Image.open(logo_path).convert("RGBA")
    logo_img = logo_img.resize((int(icon_size * 800), int(icon_size * 800)), Image.Resampling.LANCZOS)
    imagebox = OffsetImage(logo_img, zoom=icon_size)
    ab = AnnotationBbox(imagebox, (avatar_left_position, position[1]), frameon=False, xycoords='axes fraction')

    square_size = 0.08
    ax.add_patch(Polygon([[avatar_left_position - square_size / 2, position[1] - square_size / 2], 
                          [avatar_left_position + square_size / 2, position[1] - square_size / 2], 
                          [avatar_left_position + square_size / 2, position[1] + square_size / 2], 
                          [avatar_left_position - square_size / 2, position[1] + square_size / 2]], 
                          closed=True, fill=True, edgecolor='#7D9D7D', facecolor=box_facecolor, lw=2))
    ax.add_artist(ab)

    clean_txt = clean_text(username, vcr_font)
    ax.text(avatar_left_position + 0.05, position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='left', va='center', color=glow_color, transform=ax.transAxes,
            fontproperties=vcr_font,
            path_effects=[patheffects.withStroke(linewidth=5, foreground=shadow_color)])

    ax.text(avatar_left_position + 0.05, position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='left', va='center', color=color, transform=ax.transAxes,
            fontproperties=vcr_font,
            bbox=dict(facecolor=box_facecolor, edgecolor='#7D9D7D', boxstyle='round,pad=0.4', alpha=0.85))

# Add username with box
def add_username_with_box(ax, username, position, fontsize=34, color='#333333', glow_color='#AAAAAA', shadow_color='#222222', box_facecolor='#FFECB3'):
    clean_txt = clean_text(username, vcr_font)
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=glow_color, transform=ax.transAxes,
            fontproperties=vcr_font,
            path_effects=[patheffects.withStroke(linewidth=4, foreground=shadow_color)],
            bbox=dict(facecolor=box_facecolor, edgecolor='none', boxstyle='round,pad=0.5', alpha=0.85))
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=color, transform=ax.transAxes,
            fontproperties=vcr_font)

# Draw static elements (border, usernames, avatars) only once
def draw_static_elements(ax, logo_path, tournament_title, user_data_list):
    ax.clear()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    draw_polished_border(ax)
    add_logo(ax, logo_path)
    
    add_text_with_glow(ax, tournament_title, (0.5, 0.94), fontsize=48, color='#333333')
    
    for i, (user_data, avatar_img) in enumerate(user_data_list):
        avatar_img = avatar_img.resize((270, 270), Image.LANCZOS)
        imagebox = OffsetImage(avatar_img, zoom=1)
        ab = AnnotationBbox(imagebox, (0.25 + i * 0.5, 0.60), frameon=False)
        ax.add_artist(ab)
        
        username = user_data['username'].upper() if user_data else f"USER{i+1}"
        add_username_with_box(ax, username, (0.25 + i * 0.5, 0.43), fontsize=34, color='#333333')

        if user_data:
            socials = get_social_connections(user_data)
            social_box_background = '#A2D9A2'
            for j, (logo, social_username) in enumerate(socials):
                social_position = (0.25 + i * 0.5, 0.32 - (0.09 * j))
                add_social_icon_and_text(ax, logo, social_username, social_position, 0.25 + i * 0.5, fontsize=24,
                                         icon_size=0.25, color='#333333', glow_color='#444444',
                                         shadow_color='#111111', box_facecolor=social_box_background)

# Get social connections
def get_social_connections(user_data):
    connections = user_data.get('connections', {})
    social_list = []

    if 'discord' in connections:
        social_list.append(('assets/discord_logo.png', f"{connections['discord'].get('display_username')}"))
    if 'twitch' in connections:
        social_list.append(('assets/twitch_logo.png', f"{connections['twitch'].get('display_username')}"))
    if 'twitter' in connections:
        social_list.append(('assets/twitter_logo.png', f"{connections['twitter'].get('display_username')}"))
    return social_list[:3]

# Main function to create the commentary scene with animated GIF background
def create_commentary_scene(logo_path, gif_path, tournament_title="COMMENTATORS"):
    # Load user IDs from commentary_data.json
    with open('commentary_data.json', 'r') as f:
        data = json.load(f)
    user_ids = [commentator["user_id"] for commentator in data.get("commentators", [])]

    # Load user data and avatars once
    user_data_list = []
    for user_id in user_ids:
        user_data, avatar_url = fetch_cached_user_data(user_id)
        avatar_img = load_avatar_image(avatar_url)
        user_data_list.append((user_data, avatar_img))

    # Load the GIF frames
    gif = Image.open(gif_path)
    frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(gif)]

    # Set up the figure and axis for animation
    fig, ax = plt.subplots(figsize=(19.2, 10.8))
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw static elements only once
    draw_static_elements(ax, logo_path, tournament_title, user_data_list)

    # Function to update the background for each frame in the animation
    def update(frame):
        ax.imshow(frame, extent=[0, 1, 0, 1], aspect='auto')

    # Create the animation
    ani = animation.FuncAnimation(fig, update, frames=frames, repeat=False)
    
    output_image_path = os.path.join("scenes", "commentary_scene.gif")
    ani.save(output_image_path, writer='imagemagick', fps=10)
    plt.close(fig)

# Run the commentary scene creation
logo_path = 'assets/tournament_logo.png'
gif_path = 'assets/bg.gif'
create_commentary_scene(logo_path, gif_path)
