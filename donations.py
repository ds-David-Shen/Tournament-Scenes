from PIL import Image, ImageDraw, ImageFont
import json
import os

# Load donor data from JSON file and sort by contribution (highest to lowest)
with open("get_donors.json", "r", encoding="utf-8") as f:
    donors = json.load(f)
    donors.sort(key=lambda x: float(x['Contribution'].replace('$', '')), reverse=True)

# Create the scenes directory if it doesn't exist
os.makedirs("scenes", exist_ok=True)

# Image dimensions and settings for the scrollable element
width, height = 800, 400  # Width set for display, height reduced to show only scrollable content
font_path = r"assets/VCR_OSD_MONO_1.001[1].ttf"

# Define fonts
donor_font = ImageFont.truetype(font_path, 28)
comment_font = ImageFont.truetype(font_path, 24)

# Define scrolling area properties
entry_height = 110  # Height per donor entry
scroll_speed = 2  # Pixels to move per frame

# Function to wrap text based on pixel width
def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if draw.textlength(test_line, font=font) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

# Calculate number of frames for a full scroll
total_donor_entries = len(donors)
extended_height = entry_height * total_donor_entries * 2  # Double list for seamless wrap
num_frames = extended_height // scroll_speed

# Create a scrollable image with a dark indigo background
scroll_img = Image.new("RGBA", (width, extended_height), (26, 30, 41, 255))  # Using #1A1E29
scroll_draw = ImageDraw.Draw(scroll_img)

# Draw all donors twice in the extended scroll image (for seamless scrolling)
for j in range(2):  # Repeat donors twice for seamless scrolling
    for i, donor in enumerate(donors):
        y_position = i * entry_height + j * entry_height * total_donor_entries
        name_text = f"Donor: {donor['Donor']}"
        amount_text = f"Amount: {donor['Contribution']}"
        comment_text = f"Comment: {donor['Comment']}"

        # Add subtle divider line between entries
        if i > 0:
            scroll_draw.line([(10, y_position), (width - 10, y_position)], fill=(50, 50, 50, 255), width=1)

        # Draw donor name on the left
        scroll_draw.text((20, y_position + 10), name_text, font=donor_font, fill=(173, 216, 230, 255))
        
        # Draw amount label closer to the donor name
        scroll_draw.text((400, y_position + 10), amount_text, font=donor_font, fill=(144, 238, 144, 255))

        # Wrap and draw the comment text
        wrapped_comment = wrap_text(comment_text, comment_font, width - 80, scroll_draw)
        comment_y = y_position + 40
        for line in wrapped_comment:
            scroll_draw.text((20, comment_y), line, font=comment_font, fill=(211, 211, 211, 255))
            comment_y += 26  # Line spacing for comments

# Create frames for GIF
frames = []
for frame_num in range(num_frames):
    # Create the base image with only the scrollable content
    base_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # Calculate offset for scrolling effect
    scroll_y_offset = -(frame_num * scroll_speed) % (entry_height * total_donor_entries)

    # Crop the scrolling part from the extended image and paste it precisely into the base image
    cropped_scroll = scroll_img.crop((0, scroll_y_offset, width, scroll_y_offset + height))
    base_img.paste(cropped_scroll, (0, 0))  # Paste at (0, 0) to fill the full base image

    # Append the frame to the list
    frames.append(base_img)

# Save as GIF with looping
output_path = os.path.join("scenes", "donation_scroll.gif")
frames[0].save(output_path, format="GIF", append_images=frames[1:], save_all=True, duration=50, loop=0)
print(f"Scrollable donation scene saved as {output_path}.")
