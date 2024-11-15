import subprocess
from PIL import Image, ImageSequence, ImageDraw, ImageFont

# Run get_donors.py
subprocess.run(["python", "get_donors.py"])
print("Finished running get_donors.py")

# Run donations.py
subprocess.run(["python", "donations.py"])
print("Finished running donations.py")

# Paths to the assets
background_path = r"assets\dono-wall.gif"
scroll_path = r"scenes\donation_scroll.gif"
font_path = r"assets\VCR_OSD_MONO_1.001[1].ttf"

# Load the background GIF and scroll GIF
background_gif = Image.open(background_path)
scroll_gif = Image.open(scroll_path)

# Store all frames of the background and scroll GIFs
background_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(background_gif)]
scroll_frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(scroll_gif)]
num_scroll_frames = len(scroll_frames)

# Extend background frames if it has fewer frames than the scroll GIF
extended_background_frames = background_frames * (num_scroll_frames // len(background_frames) + 1)
extended_background_frames = extended_background_frames[:num_scroll_frames]  # Match exactly

# Load the font for the title
title_font = ImageFont.truetype(font_path, 36)

# Prepare frames for the new GIF
output_frames = []

# Set positioning and scaling factors
scroll_x = 0  # Align to the left edge
scroll_y = 50  # Move higher on the background
scale_factor = 0.8  # Scale down to 80% of the original size

# Generate each frame by overlaying the scroll frame onto the background frame
for i in range(num_scroll_frames):
    bg_frame = extended_background_frames[i]
    scroll_frame = scroll_frames[i]

    # Resize the scroll frame to make it smaller
    new_width = int(scroll_frame.width * scale_factor)
    new_height = int(scroll_frame.height * scale_factor)
    resized_scroll_frame = scroll_frame.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create a composite frame with background and resized scroll overlay
    composite_frame = bg_frame.copy()
    resized_scroll_frame_with_alpha = resized_scroll_frame.copy()
    resized_scroll_frame_with_alpha.putalpha(180)  # Set opacity to 180 for more transparency

    # Paste the resized scroll GIF onto the background at the specified position
    composite_frame.paste(resized_scroll_frame_with_alpha, (scroll_x, scroll_y), mask=resized_scroll_frame_with_alpha)

    # Draw the "Donors" title at the top center with a shadow effect
    draw = ImageDraw.Draw(composite_frame)
    title_text = "Donors"
    
    # Calculate text position using textbbox for precise centering
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (bg_frame.width - title_width) // 2
    title_y = 10  # Padding from the top
    
    # Shadow effect for title
    shadow_offset = 2
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title_text, font=title_font, fill=(0, 0, 0, 128))
    draw.text((title_x, title_y), title_text, font=title_font, fill=(255, 255, 255, 255))

    # Append the composite frame to the output frames
    output_frames.append(composite_frame)

# Save the new GIF with the overlaid donation scroll and title
output_path = r"scenes\donowall.gif"
output_frames[0].save(
    output_path,
    format="GIF",
    append_images=output_frames[1:],
    save_all=True,
    duration=scroll_gif.info.get("duration", 100),
    loop=0
)

print(f"Donation wall GIF saved as {output_path}.")
