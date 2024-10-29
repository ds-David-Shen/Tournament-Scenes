import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Polygon
from PIL import Image, ImageDraw, ImageFilter
from io import BytesIO
from matplotlib.font_manager import FontProperties
from matplotlib import patheffects
import os
import requests

# Load VCR_OSD_MONO font
vcr_font = FontProperties(fname=r"assets/VCR_OSD_MONO_1.001[1].ttf")

def can_render_text(char, font):
    fig, ax = plt.subplots()
    text = ax.text(0.5, 0.5, char, fontproperties=font)
    renderer = fig.canvas.get_renderer()
    bbox = text.get_window_extent(renderer)
    plt.close(fig)
    return bbox.width > 0 and bbox.height > 0

def clean_text(text, font):
    return ''.join([char for char in text if can_render_text(char, font)])

BASE_AVATAR_URL = "https://tetr.io/user-content/avatars/{USERID}.jpg?rv=0"

def fetch_tetrio_user_data(user_id):
    api_url = f"https://ch.tetr.io/api/users/{user_id}"
    response = requests.get(api_url)
    if response.status_code == 200 and response.json().get('success'):
        return response.json().get('data')
    return None

def get_avatar_url(user_data):
    user_id = user_data['_id']
    return BASE_AVATAR_URL.format(USERID=user_id)

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

def add_social_icon_and_text(ax, logo_path, username, position, avatar_left_position, fontsize=24, icon_size=0.25, color='#333333', glow_color='#444444', shadow_color='#111111', box_facecolor='#FFD700'):
    avatar_left_position -= 0.11  # Move the icons further to the left

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

# Function to add a boxed username at the bottom of the avatar
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

# Function to add glow effect to text without a box around it
def add_text_with_glow(ax, text, position, fontsize=48, color='#333333', glow_color='#AAAAAA', shadow_color='#222222'):
    clean_txt = clean_text(text, vcr_font)
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=glow_color, transform=ax.transAxes,
            fontproperties=vcr_font,
            path_effects=[patheffects.withStroke(linewidth=4, foreground=shadow_color)])
    
    ax.text(position[0], position[1], clean_txt, fontsize=fontsize, fontweight='bold',
            ha='center', va='center', color=color, transform=ax.transAxes,
            fontproperties=vcr_font)

def rounded_avatar_with_shadow(img, size, shadow_offset=(10, 10), shadow_color=(0, 0, 0, 100)):
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=50, fill=255)

    rounded_avatar = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    rounded_avatar.paste(img, (0, 0), mask=mask)

    shadow = Image.new('RGBA', (size + abs(shadow_offset[0]), size + abs(shadow_offset[1])), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle([abs(shadow_offset[0]), abs(shadow_offset[1]), size, size], radius=50, fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=12))
    shadow.paste(rounded_avatar, (0, 0), mask=rounded_avatar.split()[3])
    return shadow

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

def add_logo(ax, logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((80, 80), Image.Resampling.LANCZOS)
    imagebox = OffsetImage(logo, zoom=1)
    ab = AnnotationBbox(imagebox, (0.97, 0.92), frameon=False, xycoords='axes fraction')
    ax.add_artist(ab)

def create_commentary_scene(user_ids, logo_path, gif_path, tournament_title="COMMENTATORS"):
    gif = Image.open(gif_path)
    static_background = gif.convert("RGBA")

    fig_width, fig_height = 19.2, 10.8
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.imshow(static_background, extent=[0, 1, 0, 1], aspect='auto')
    draw_polished_border(ax)
    add_logo(ax, logo_path)

    add_text_with_glow(ax, tournament_title, (0.5, 0.94), fontsize=48, color='#333333')

    positions = [(0.25, 0.60), (0.75, 0.60)]
    avatar_size = 270

    for i, user_id in enumerate(user_ids):
        user_data = fetch_tetrio_user_data(user_id)
        avatar_url = get_avatar_url(user_data) if user_data else 'assets/apple.png'

        try:
            avatar_response = requests.get(avatar_url, stream=True)
            avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
        except Exception:
            avatar_img = Image.open('assets/apple.png')

        rounded_avatar_img = rounded_avatar_with_shadow(avatar_img, avatar_size, shadow_offset=(10, 10), shadow_color=(0, 0, 0, 128))
        imagebox = OffsetImage(rounded_avatar_img, zoom=1)
        ab = AnnotationBbox(imagebox, positions[i], frameon=False)
        ax.add_artist(ab)

        if user_data:
            socials = get_social_connections(user_data)
            username = user_data['username'].upper()
        else:
            socials = []
            username = f"USER{i+1}"

        # Add the username with a box below the avatar
        add_username_with_box(ax, username, (positions[i][0], 0.43), fontsize=34, color='#333333')

        social_box_background = '#A2D9A2'
        for j, (logo, social_username) in enumerate(socials):
            social_position = (positions[i][0], 0.32 - (0.09 * j))
            add_social_icon_and_text(ax, logo, social_username, social_position, positions[i][0], fontsize=24,
                                     icon_size=0.25, color='#333333', glow_color='#444444',
                                     shadow_color='#111111', box_facecolor=social_box_background)

    output_image_path = os.path.join("scenes", "commentary_scene.png")
    plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

user_ids = ["5ec684620cfca96246aa9bda", "5f3718f11fee2b2e8c27d55f"]
logo_path = 'assets/tournament_logo.png'
gif_path = 'assets/bg.gif'

create_commentary_scene(user_ids, logo_path, gif_path)
