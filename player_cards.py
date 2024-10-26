import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

# Function to add text with a shadow for better readability
def draw_text_with_shadow(draw, text, position, font, text_color=(255, 255, 255), shadow_color=(0, 0, 0), shadow_offset=2):
    # Draw shadow
    x, y = position
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    # Draw actual text
    draw.text((x, y), text, font=font, fill=text_color)

# Define the function to create a player card
def create_player_card(user_id, seed_value):
    avatar_revision = "0"
    apple_texture_path = "assets/apple.png"  # Updated path to apple texture

    # URLs for fetching user data and stats
    user_info_url = f"https://ch.tetr.io/api/users/{user_id}"
    league_summary_url = f"https://ch.tetr.io/api/users/{user_id}/summaries/league"
    avatar_url = f"https://tetr.io/user-content/avatars/{user_id}.jpg?rv={avatar_revision}"

    # Get the user info (to fetch the username, country, and AR)
    response_user_info = requests.get(user_info_url)
    if response_user_info.status_code == 200:
        user_data = response_user_info.json()
        if user_data['success']:
            username = user_data['data']['username'].upper()  # Convert username to all caps
            ar = user_data['data'].get('ar', 'N/A')  # Fetch AR (Attack Rating)
            country_code = user_data['data'].get('country', 'N/A').lower()  # Fetch country code
        else:
            username = "UNKNOWN"
            ar = "Unavailable"
            country_code = "N/A"
    else:
        print(f"Error fetching user info: {response_user_info.status_code}")
        username = "ERROR"
        ar = "Error"
        country_code = "N/A"

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
        avatar_response.raise_for_status()  # Check if the request was successful
        avatar_img = Image.open(BytesIO(avatar_response.content)).convert("RGBA")
    except (requests.exceptions.HTTPError, requests.exceptions.RequestException):
        # Use apple.png as a default image if the avatar request fails
        avatar_img = Image.open(apple_texture_path).convert("RGBA")

    # Fetch country flag
    flag_url = f"https://tetr.io/res/flags/{country_code}.png"
    flag_response = requests.get(flag_url)
    flag_img = Image.open(BytesIO(flag_response.content)).convert("RGBA")

    # Fetch rank image
    rank_url = f"https://tetr.io/res/league-ranks/{rank}.png"
    rank_response = requests.get(rank_url)
    rank_img = Image.open(BytesIO(rank_response.content)).convert("RGBA")

    # Create the card with an opaque background to block the GIF background from showing through
    width, height = 400, 700
    card = Image.new('RGBA', (width, height), (255, 255, 255, 255))  # Solid white background to block GIF

    # Apply apple pattern on the card background
    apple_texture = Image.open(apple_texture_path).convert("RGBA")
    apple_texture = apple_texture.resize((100, 100))  # Resize the apple texture
    apple_texture = ImageOps.colorize(apple_texture.convert('L'), (255, 224, 102), (255, 229, 153))  # Softer yellow apple color
    apple_texture.putalpha(120)  # Maintain transparency for the pattern

    # Apply apple texture in a diagonal pattern, filling the whole card
    diagonal_offset = 30  # Slight diagonal offset
    for i in range(-200, width + 100, 90):  # Ensure the apples go beyond the card's width
        for j in range(-100, height + 100, 90):  # Ensure the apples go beyond the card's height
            x_offset = i + (j // diagonal_offset) * 10  # Apply diagonal shift
            card.paste(apple_texture, (x_offset, j), apple_texture)

    # Load fonts (adjust paths for your system)
    font_path = "assets/BubblegumSans-Regular.ttf"
    try:
        font_large = ImageFont.truetype(font_path, 36)  # Boldened username font
        font_medium = ImageFont.truetype(font_path, 25)  # Boldened rank and TR font
        font_small = ImageFont.truetype(font_path, 18)     # Small font for additional details
        font_bold = ImageFont.truetype(font_path, 30)    # Bold font for title
    except IOError:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    draw = ImageDraw.Draw(card)

    # Add smoother border around the card (darker orange for outer border)
    outer_border_color = (255, 140, 0)  # Darker orange for the card border
    draw.rounded_rectangle([0, 0, width-1, height-1], outline=outer_border_color, width=10, radius=15)

    # Center align the combination of username and flag with shadow
    username_bbox = draw.textbbox((0, 0), username, font=font_large)
    username_width = username_bbox[2] - username_bbox[0]
    flag_width = 40
    total_width = username_width + flag_width + 10
    username_flag_x = (width - total_width) // 2
    draw_text_with_shadow(draw, username, (username_flag_x, 50), font=font_large, text_color=(255, 128, 34))
    flag_img = flag_img.resize((40, 30))
    card.paste(flag_img, (username_flag_x + username_width + 10, 55), flag_img)

    # Add avatar with softer orange border and shadow
    avatar_size = 220
    avatar_x = (width - avatar_size) // 2
    avatar_y = 100
    avatar_img = avatar_img.resize((avatar_size, avatar_size))
    card.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
    avatar_border_color = (255, 165, 0)  # Softer orange for avatar border
    border_offset = 8  # Thicker avatar border
    draw.rounded_rectangle([avatar_x - border_offset, avatar_y - border_offset, avatar_x + avatar_size + border_offset, avatar_y + avatar_size + border_offset], outline=avatar_border_color, width=border_offset, radius=10)

    # Add Rank image and TR
    rank_img_size = 70
    rank_img = rank_img.resize((rank_img_size, rank_img_size))
    rank_img_x = (width // 2) - 160 + 10
    rank_y = avatar_y + avatar_size
    rank_img_y = rank_y + 5
    card.paste(rank_img, (rank_img_x, rank_img_y), rank_img)

    tr_string = f"{tr}TR"
    tr_number_x = rank_img_x + rank_img_size + 20
    tr_number_y = rank_img_y + 15
    draw_text_with_shadow(draw, tr_string, (tr_number_x, tr_number_y), font=font_large, text_color=(255, 255, 255))

    # Add the seed text with margin and a thickened border (draw it later so it's on top)
    seed_text = f"Seed: #{seed_value}"
    seed_rect_y = rank_y + 80
    seed_rect_height = 60
    seed_margin = 10  # Add margin away from card border
    seed_rect_radius = 20
    seed_rect_border_thickness = 5  # Thicker border for the seed rectangle

    # Draw the stats background first (so the seed goes on top)
    draw.rectangle([10, rank_y + 130, width - 10, height - 10], fill=(50, 50, 50, 255))  # Solid dark gray background

    stats = {
        "PPS": {"value": pps, "color": (255, 165, 0), "max": 5},   # Orange for PPS
        "APM": {"value": apm, "color": (255, 215, 0), "max": 250}, # Gold for APM
        "VS": {"value": vs, "color": (255, 140, 0), "max": 450},   # Darker orange for VS
        "AR": {"value": ar, "color": (255, 69, 0), "max": 450}     # Red-orange for AR
    }

    def draw_dotted_bars(draw, start_x, start_y, stat_value, max_value, stat_type, display_value):
        total_dots = 20
        filled_dots = min(round((stat_value / max_value) * total_dots), total_dots)
        dot_spacing = 10
        dot_size = 5
        # Change the dot colors based on the stats dictionary
        dot_color = stats[stat_type]["color"]
        for i in range(total_dots):
            color = dot_color if i < filled_dots else (255, 255, 255)
            draw.ellipse([start_x + i * dot_spacing, start_y, start_x + dot_size + i * dot_spacing, start_y + dot_size], fill=color)
        value_x = start_x + total_dots * dot_spacing + 10
        draw_text_with_shadow(draw, str(display_value), (value_x, start_y - dot_size), font=font_small)

    # Draw the stats with improved readability
    y_offset = rank_y + 150
    for stat, info in stats.items():
        draw_text_with_shadow(draw, f"{stat}", (20, y_offset), font=font_medium, text_color=(255, 255, 255))
        draw_dotted_bars(draw, start_x=120, start_y=y_offset + 10, stat_value=info["value"], max_value=info["max"], stat_type=stat, display_value=info["value"])
        y_offset += 60

    # Finally, draw the seed rectangle and text on top
    draw.rounded_rectangle([seed_margin, seed_rect_y, width-seed_margin, seed_rect_y + seed_rect_height], fill=(255, 224, 102, 255), outline=(255, 165, 0), width=seed_rect_border_thickness, radius=seed_rect_radius)
    seed_bbox = draw.textbbox((0, 0), seed_text, font=font_medium)
    seed_width = seed_bbox[2] - seed_bbox[0]
    draw_text_with_shadow(draw, seed_text, ((width - seed_width) // 2, seed_rect_y + 15), font=font_bold)

    return card
