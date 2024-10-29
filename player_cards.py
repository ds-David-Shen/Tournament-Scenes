import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

# Function to add text with a shadow for better readability
def draw_text_with_shadow(draw, text, position, font, text_color=(255, 255, 255), shadow_color=(0, 0, 0), shadow_offset=2):
    x, y = position
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=text_color)

# Function to create a mask for rounded rectangle borders
def create_rounded_rectangle_mask(width, height, radius, margin=5):
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([margin, margin, width-margin, height-margin], fill=255, radius=radius)
    return mask

# Define the function to create a player card
def create_player_card(user_id, seed_value, flavour_text="[EX] Ability: 6-3"):
    avatar_revision = "0"
    apple_texture_path = "assets/apple.png"

    # URLs for fetching user data and stats
    user_info_url = f"https://ch.tetr.io/api/users/{user_id}"
    league_summary_url = f"https://ch.tetr.io/api/users/{user_id}/summaries/league"
    avatar_url = f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}"

    # Get the user info (to fetch the username and AR)
    response_user_info = requests.get(user_info_url)
    if response_user_info.status_code == 200:
        user_data = response_user_info.json()
        if user_data['success']:
            username = user_data['data']['username'].upper()  # Convert username to all caps
            ar = user_data['data'].get('ar', 'N/A')  # Fetch AR (Attack Rating)
        else:
            username = "UNKNOWN"
            ar = "Unavailable"
    else:
        print(f"Error fetching user info: {response_user_info.status_code}")
        username = "ERROR"
        ar = "Error"

    # Get the TETRA LEAGUE stats
    response_league = requests.get(league_summary_url)
    if response_league.status_code == 200:
        data = response_league.json()
        if data['success']:
            tetra_data = data['data']
            pps = tetra_data.get('pps', 'N/A')  # Pieces per Second
            apm = round(tetra_data.get('apm', 0))  # Round APM to nearest integer
            vs = round(tetra_data.get('vs', 0))    # Round VS to nearest integer
            rank = tetra_data.get('rank', 'N/A').lower()  # Fetch rank for rank image
            tr = round(tetra_data.get('tr', 0))  # Tetra Rating, rounded to the nearest integer
        else:
            pps = apm = vs = rank = tr = "Unavailable"
    else:
        print(f"Error fetching stats: {response_league.status_code}")
        pps = apm = vs = rank = tr = "Error"

    # Fetch avatar image
    try:
        avatar_response = requests.get(avatar_url)
        avatar_response.raise_for_status()
        avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
        avatar_img = Image.open(apple_texture_path).convert("RGBA")

    # Fetch rank image
    rank_url = f"https://tetr.io/res/league-ranks/{rank}.png"
    rank_response = requests.get(rank_url)
    rank_img = Image.open(BytesIO(rank_response.content)).convert("RGBA")

    # Create the card with an opaque background
    width, height = 400, 700
    card = Image.new('RGBA', (width, height), (255, 255, 255, 255))

    # Create a mask to prevent content from spilling out of the rounded corners
    rounded_mask = create_rounded_rectangle_mask(width, height, radius=15)

    # Apply apple pattern on the card background
    apple_texture = Image.open(apple_texture_path).convert("RGBA")
    apple_texture = apple_texture.resize((100, 100))
    apple_texture = ImageOps.colorize(apple_texture.convert('L'), (244, 208, 63), (255, 229, 153))
    apple_texture.putalpha(120)

    # Apply apple texture in a diagonal pattern
    diagonal_offset = 30
    for i in range(-200, width + 100, 90):
        for j in range(-100, height + 100, 90):
            x_offset = i + (j // diagonal_offset) * 10
            card.paste(apple_texture, (x_offset, j), apple_texture)

    # Load fonts
    font_path = r"assets\VCR_OSD_MONO_1.001[1].ttf"
    font_large = ImageFont.truetype(font_path, 36)
    font_medium = ImageFont.truetype(font_path, 22)
    font_small = ImageFont.truetype(font_path, 16)
    font_tiny = ImageFont.truetype(font_path, 12)
    font_bold = ImageFont.truetype(font_path, 30)

    draw = ImageDraw.Draw(card)

    # Username section with dynamic font size adjustment
    nameplate_y = 5
    nameplate_height = 50
    nameplate_radius = 20
    tr_rect_y = nameplate_y
    tr_rect_x = width - 120
    tr_rect_width = width
    
    # Draw the TR and Rank area
    draw.rounded_rectangle([tr_rect_x, tr_rect_y, tr_rect_width, tr_rect_y + nameplate_height], fill=(255, 224, 130, 255), radius=nameplate_radius)
    draw.rounded_rectangle([5, nameplate_y, width - 105, nameplate_y + nameplate_height], fill=(244, 208, 63, 255), radius=nameplate_radius)

    # Adjust font size dynamically based on username length
    username_x = 15
    max_width = width - 120
    font_username = font_large
    username_width = draw.textbbox((0, 0), username, font=font_username)[2]
    while username_width > max_width and font_username.size > 12:
        font_username = ImageFont.truetype(font_path, font_username.size - 1)
        username_width = draw.textbbox((0, 0), username, font=font_username)[2]

    draw_text_with_shadow(draw, username, (username_x, nameplate_y + 10), font=font_username, text_color=(0, 0, 0))

    # TR and rank positioning
    tr_label = "TR"
    tr_value_str = str(tr)
    tr_x = width - 100
    tr_y = nameplate_y + 20

    draw_text_with_shadow(draw, tr_label, (tr_x, tr_y), font=font_tiny, text_color=(0, 0, 0), shadow_offset=0)
    tr_value_x = tr_x + 15
    draw_text_with_shadow(draw, tr_value_str, (tr_value_x, tr_y), font=font_small, text_color=(0, 0, 0), shadow_offset=0)

    rank_img_size = 25
    rank_img = rank_img.resize((rank_img_size, rank_img_size))
    rank_img_y = nameplate_y + 10
    card.paste(rank_img, (tr_value_x + 45, rank_img_y), rank_img)

    # Avatar section
    avatar_size = 320
    avatar_x = (width - avatar_size) // 2
    avatar_y = nameplate_y + nameplate_height + 10
    avatar_img = avatar_img.resize((avatar_size, avatar_size))
    card.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

    # Define padding for rectangular border around avatar
    padding_width = 40
    padding_height = 12
    avatar_border_color = (255, 183, 77)
    avatar_border_size = 255
    avatar_border_x = (width - avatar_border_size) // 2

    draw.rounded_rectangle(
        [avatar_border_x - padding_width, avatar_y - padding_height, avatar_border_x + avatar_border_size + padding_width, avatar_y + avatar_size + padding_height],
        outline=avatar_border_color, width=12, radius=10
    )

    # Seed and stats section
    draw.rectangle([10, avatar_y + avatar_size + 20, width - 10, height - 10], fill=(44, 44, 44, 255))
    seed_text = f"Seed #{seed_value}"
    seed_rect_y = avatar_y + avatar_size + 10
    seed_rect_height = 40
    seed_margin = 10
    seed_rect_border_thickness = 5

    draw.rounded_rectangle([seed_margin, seed_rect_y, width-seed_margin, seed_rect_y + seed_rect_height], fill=(244, 208, 63, 255), outline=(255, 165, 0), width=seed_rect_border_thickness)

    draw_text_with_shadow(draw, seed_text, (seed_margin + 10, seed_rect_y + 5), font=font_bold)

    flavour_bbox = draw.textbbox((0, 0), flavour_text, font=font_small)
    flavour_x = width - flavour_bbox[2] - seed_margin - 10
    flavour_y = seed_rect_y + seed_rect_height - 25
    draw_text_with_shadow(draw, flavour_text, (flavour_x, flavour_y), font=font_small)

    # Stats section
    stats = {
        "PPS": {"value": pps, "max": 5, "color": (255, 183, 77)},
        "APM": {"value": apm, "max": 250, "color": (255, 215, 0)},
        "VS": {"value": vs, "max": 450, "color": (255, 140, 0)},
        "AR": {"value": ar, "max": 450, "color": (255, 69, 0)}
    }

    def draw_dotted_bars(draw, start_x, start_y, stat_value, max_value, color):
        total_dots = 20
        filled_dots = min(round((stat_value / max_value) * total_dots), total_dots)
        dot_spacing = 14
        dot_size = 5
        total_width = total_dots * dot_spacing + dot_size
        bar_height = dot_size + 10
        draw.rounded_rectangle([start_x - 5, start_y - 5, start_x + total_width + 5, start_y + bar_height], fill=(60, 60, 60, 255), radius=10)
        for i in range(total_dots):
            dot_color = color if i < filled_dots else (255, 255, 255)
            draw.ellipse([start_x + i * dot_spacing, start_y, start_x + dot_size + i * dot_spacing, start_y + dot_size], fill=dot_color)

    y_offset = seed_rect_y + seed_rect_height + 43
    for stat, info in stats.items():
        stat_text_y = y_offset
        stat_value_y = y_offset
        stat_value_width = 60

        stat_rect_width = 60
        stat_rect_height = 40
        draw.rounded_rectangle([20, stat_text_y - 35, 20 + stat_rect_width, stat_text_y + stat_rect_height - 35], fill=(100, 100, 100, 255), radius=10)

        stat_text_bbox = draw.textbbox((0, 0), f"{stat}", font=font_medium)
        stat_text_x = 20 + (stat_rect_width - (stat_text_bbox[2] - stat_text_bbox[0])) // 2
        stat_text_y_centered = stat_text_y - 30
        draw_text_with_shadow(draw, f"{stat}", (stat_text_x, stat_text_y_centered), font=font_medium, text_color=(255, 255, 255))

        draw_dotted_bars(draw, start_x=40, start_y=y_offset + 10, stat_value=info["value"], max_value=info["max"], color=info["color"])

        draw.rounded_rectangle([width - stat_value_width - 26, stat_value_y - 15, width - 28, stat_value_y + stat_rect_height - 15], fill=(60, 60, 60, 255), radius=10)

        stat_value_text_bbox = draw.textbbox((0, 0), f"{info['value']}", font=font_medium)
        stat_value_x = width - stat_value_width - 28 + (stat_value_width - (stat_value_text_bbox[2] - stat_value_text_bbox[0])) // 2
        stat_value_y_centered = stat_value_y - 7
        draw_text_with_shadow(draw, f"{info['value']}", (stat_value_x, stat_value_y_centered), font=font_medium, text_color=(255, 255, 255))
        
        y_offset += 60

    outer_border_color = (255, 152, 0)
    draw.rounded_rectangle([0, 0, width-1, height-1], outline=outer_border_color, width=10, radius=15)

    card.putalpha(rounded_mask)
    return card
