from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageSequence

# Function to add glow effect to text
def add_glow(base_image, text, position, font, glow_color, glow_strength=4):
    glow_image = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_image)
    
    for offset in range(glow_strength):
        glow_draw.text((position[0] - offset, position[1] - offset), text, font=font, fill=glow_color)
        glow_draw.text((position[0] + offset, position[1] + offset), text, font=font, fill=glow_color)

    # Apply a blur filter to the glow image to soften the edges
    glow_image = glow_image.filter(ImageFilter.GaussianBlur(radius=glow_strength))
    
    # Overlay the glow image onto the base image
    base_image.paste(glow_image, (0, 0), glow_image)

# Function to create a very subtle gradient overlay
def create_gradient_overlay(size):
    gradient = Image.new("RGBA", size)
    for y in range(size[1]):
        # Reduced opacity for an even subtler gradient
        opacity = int(100 * (y / size[1]))  # Max opacity of 100 for a lighter effect
        gradient.paste((0, 0, 0, opacity), (0, y, size[0], y + 1))
    return gradient

# Function to create the animated poster
def create_poster(apply_gradient=False):
    # Open the animated background GIF
    background_gif = Image.open("assets/bg.gif")
    
    # Initialize a list to store all the frames
    frames = []
    
    # Load the tournament logo, resize, and position it closer to the corner
    tournament_logo = Image.open("assets/tournament_logo.png").convert("RGBA")
    logo_width = background_gif.width // 6  # Slightly smaller logo size
    logo_height = int(tournament_logo.height * (logo_width / tournament_logo.width))
    tournament_logo = tournament_logo.resize((logo_width, logo_height), Image.LANCZOS)
    logo_x = background_gif.width - logo_width - 30  # Adjusted closer to the corner with 30px padding
    logo_y = 30  # Slightly closer to the top

    # Load fonts for the title, event info, and CTA
    font_title = ImageFont.truetype(r"assets/VCR_OSD_MONO_1.001[1].ttf", 200)
    font_event = ImageFont.truetype(r"assets/VCR_OSD_MONO_1.001[1].ttf", 80)
    font_cta = ImageFont.truetype(r"assets/VCR_OSD_MONO_1.001[1].ttf", 70)

    title_text = "Apple Orchard Cup"
    event_info = "November 16, 2024 - 9:00 PM UTC"
    cta_info = "Sign up now at appleorchardcup.com"

    # Create a very subtle gradient overlay if apply_gradient is True
    gradient_overlay = create_gradient_overlay((background_gif.width, background_gif.height)) if apply_gradient else None

    # Process each frame of the background GIF
    for frame in ImageSequence.Iterator(background_gif):
        frame = frame.convert("RGBA")
        
        # Apply the very subtle gradient overlay to the frame if enabled
        if apply_gradient and gradient_overlay:
            frame = Image.alpha_composite(frame, gradient_overlay)
        
        # Create a drawing context
        draw = ImageDraw.Draw(frame)

        # Paste the tournament logo in the top-right corner without effects
        frame.paste(tournament_logo, (logo_x, logo_y), tournament_logo)

        # Calculate position for "Apple Orchard Cup" in a single line
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (background_gif.width - title_width) // 2
        title_y = background_gif.height - 600  # Move title higher up

        # Draw a subtle outline around "Apple Orchard Cup"
        outline_color = (0, 0, 0, 150)
        draw.text((title_x - 2, title_y - 2), title_text, font=font_title, fill=outline_color)
        draw.text((title_x + 2, title_y - 2), title_text, font=font_title, fill=outline_color)
        draw.text((title_x - 2, title_y + 2), title_text, font=font_title, fill=outline_color)
        draw.text((title_x + 2, title_y + 2), title_text, font=font_title, fill=outline_color)

        # Add glow effect with reduced strength for the title
        add_glow(frame, title_text, (title_x, title_y), font_title, glow_color=(255, 255, 255, 255), glow_strength=4)

        # Draw the actual "Apple Orchard Cup" text
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=font_title)

        # Calculate position for centering the event info and CTA
        event_bbox = draw.textbbox((0, 0), event_info, font=font_event)
        event_width = event_bbox[2] - event_bbox[0]
        event_height = event_bbox[3] - event_bbox[1]
        cta_bbox = draw.textbbox((0, 0), cta_info, font=font_cta)
        cta_width = cta_bbox[2] - cta_bbox[0]
        cta_height = cta_bbox[3] - cta_bbox[1]

        # Draw a semi-transparent background box with a border for event info and CTA
        box_width = max(event_width, cta_width) + 50
        box_height = event_height + cta_height + 60
        box_x = (background_gif.width - box_width) // 2
        box_y = background_gif.height - 250  # Move event box higher up

        overlay = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 128))  # Semi-transparent black
        frame.paste(overlay, (box_x, box_y), overlay)
        
        # Draw the border around the semi-transparent box
        border_color = (255, 255, 255, 100)
        draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], outline=border_color, width=3)

        # Draw the event info inside the box with better vertical spacing
        event_x = (background_gif.width - event_width) // 2
        event_y = box_y + 15
        draw.text((event_x, event_y), event_info, fill=(255, 255, 255), font=font_event)

        # Draw the call-to-action inside the box below the event info with more space
        cta_x = (background_gif.width - cta_width) // 2
        cta_y = event_y + event_height + 20  # Increase space between event info and CTA
        draw.text((cta_x, cta_y), cta_info, fill=(255, 255, 255), font=font_cta)

        # Append the frame to the list
        frames.append(frame)

    # Save the final animated GIF as poster.gif
    frames[0].save('scenes/poster.gif', save_all=True, append_images=frames[1:], duration=background_gif.info['duration'], loop=0)

if __name__ == "__main__":
    create_poster()
