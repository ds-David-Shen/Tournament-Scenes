import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import patheffects
from matplotlib.animation import FuncAnimation
from PIL import Image, ImageSequence
from matplotlib import font_manager

# Load the custom font
font_path = 'assets/BubblegumSans-Regular.ttf'
bubblegum_font = font_manager.FontProperties(fname=font_path)

# Load the animated GIF and extract frames
gif_path = 'assets/bg.gif'
bg_gif = Image.open(gif_path)
frames = [frame.copy() for frame in ImageSequence.Iterator(bg_gif)]

# Get the dimensions of the GIF to match the figure size
gif_width, gif_height = bg_gif.size
fig_width = gif_width / 100  # Adjust the figure size to match GIF dimensions
fig_height = gif_height / 100

# Define vertical offset (-200 pixels converted to figure units)
vertical_offset = -200 / 100  # Move the bracket down by 200 pixels

# Custom path effect for shadow
shadow = [patheffects.withSimplePatchShadow(offset=(1, -1), shadow_rgbFace='gray', alpha=0.3)]

# Custom colors
color_win = '#6c8cd5'  # Darker blue for winners bracket
color_loss = '#ff6f61'  # Soft red for losers bracket
color_text = '#ffffff'  # White text
color_bg = '#343a40'  # Dark background for score and text rectangles
line_color = '#000000'  # Set line color to black
champ_color = '#ffdd57'  # Gold for the champion box

# **Player Names and Scores**
players_data = {
    "Winners Semi 1": {"player1": "Player A", "score1": 11, "player2": "Player B", "score2": 2},
    "Winners Semi 2": {"player1": "Player C", "score1": 11, "player2": "Player D", "score2": 4},
    "Winners Final": {"player1": "Player A", "score1": 11, "player2": "Player C", "score2": 6},
    "Losers Top 8 Match 1": {"player1": "Player E", "score1": 4, "player2": "Player F", "score2": 11},
    "Losers Top 8 Match 2": {"player1": "Player G", "score1": 6, "player2": "Player H", "score2": 11},
    "Losers Quarter 1": {"player1": "Player D", "score1": 11, "player2": "Player F", "score2": 5},
    "Losers Quarter 2": {"player1": "Player B", "score1": 11, "player2": "Player H", "score2": 5},
    "Losers Semi": {"player1": "Player D", "score1": 11, "player2": "Player B", "score2": 5},
    "Losers Final": {"player1": "Player C", "score1": 11, "player2": "Player D", "score2": 5},
    "Grand Final": {"player1": "Player A", "score1": 11, "player2": "Player C", "score2": 0},
    "True Final": {"player1": "Player A", "score1": 99, "player2": "Player C", "score2": 0}
}

# Create the figure and axes for the plot
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

def draw_match(x, y, match_key, color1, color2, label=None, size_factor=1):
    match_data = players_data[match_key]
    player1, score1 = match_data["player1"], match_data["score1"]
    player2, score2 = match_data["player2"], match_data["score2"]

    box_height = 0.4 * size_factor
    box1 = ax.add_patch(Rectangle((x, y), 2 * size_factor, box_height, facecolor=color1, edgecolor='black'))
    box1.set_path_effects(shadow)
    box2 = ax.add_patch(Rectangle((x, y - box_height), 2 * size_factor, box_height, facecolor=color2, edgecolor='black'))
    box2.set_path_effects(shadow)

    # Add text for players using custom font
    ax.text(x + 0.1, y + box_height / 2, f"{player1}", verticalalignment='center', fontsize=12 * size_factor, fontweight='bold', color=color_text, fontproperties=bubblegum_font)
    ax.text(x + 0.1, y - box_height / 2, f"{player2}", verticalalignment='center', fontsize=12 * size_factor, fontweight='bold', color=color_text, fontproperties=bubblegum_font)

    # Move score boxes adjacent to the player rectangles, aligning them
    score_box_x = x + 2 * size_factor
    score_box_height = 0.3 * size_factor
    ax.add_patch(Rectangle((score_box_x, y + box_height / 2 - score_box_height / 2), 0.5 * size_factor, score_box_height, edgecolor='black', facecolor=color_bg))
    ax.add_patch(Rectangle((score_box_x, y - box_height / 2 - score_box_height / 2), 0.5 * size_factor, score_box_height, edgecolor='black', facecolor=color_bg))
    ax.text(score_box_x + 0.25 * size_factor, y + box_height / 2, f"{score1}", verticalalignment='center', fontsize=12 * size_factor, horizontalalignment='center', fontweight='bold', color=color_text, fontproperties=bubblegum_font)
    ax.text(score_box_x + 0.25 * size_factor, y - box_height / 2, f"{score2}", verticalalignment='center', fontsize=12 * size_factor, horizontalalignment='center', fontweight='bold', color=color_text, fontproperties=bubblegum_font)

    if label:
        label_box_x = x
        ax.add_patch(Rectangle((label_box_x, y + box_height + 0.05), 2.5 * size_factor, 0.4 * size_factor, edgecolor='black', facecolor=color_bg))
        ax.text(label_box_x + 1.25 * size_factor, y + box_height + 0.25, label, verticalalignment='center', horizontalalignment='center', fontsize=12 * size_factor, fontweight='bold', color=color_text, fontproperties=bubblegum_font)

    return score_box_x + 0.6 * size_factor

def draw_line(x1, y1, x2, y2, x_mid=None):
    line_style = {'color': line_color, 'linewidth': 1.5}  # Black connecting lines
    line_len = 0.3
    x1 += 0.2
    x2 -= 4
    if x_mid:
        ax.plot([x1, x1 + line_len], [y1, y1], **line_style)
        ax.plot([x1 + line_len, x1 + line_len], [y1, y2], **line_style)
        ax.plot([x1 + line_len, x2], [y2, y2], **line_style)
    else:
        ax.plot([x1, x2], [y1, y2], **line_style)

def draw_bracket(frame_index):
    ax.clear()
    bg_image = frames[frame_index % len(frames)]
    ax.imshow(bg_image, aspect='auto', extent=[0, fig_width, 0, fig_height], zorder=0)

    ax.set_xlim(0, fig_width)
    ax.set_ylim(0, fig_height)

    # Increase spacing between elements and apply vertical offset
    x_positions = [1, 5.5, 10, 14.5]
    y_positions = [8 - vertical_offset, 6.5 - vertical_offset, 5 - vertical_offset, 3.5 - vertical_offset, 2 - vertical_offset]

    # Winners bracket
    end_score_x1 = draw_match(x_positions[0], y_positions[0], "Winners Semi 1", color_win, color_win, "Winners Semi", size_factor=0.9)
    end_score_x2 = draw_match(x_positions[0], y_positions[1], "Winners Semi 2", color_win, color_win, "Winners Semi", size_factor=0.9)
    end_score_final = draw_match(x_positions[1], (y_positions[0] + y_positions[1]) / 2, "Winners Final", color_win, color_win, "Winners Final", size_factor=1.2)

    draw_line(end_score_x1, y_positions[0], end_score_final, (y_positions[0] + y_positions[1]) / 2, x_mid=(end_score_x1 + end_score_final) / 2)
    draw_line(end_score_x2, y_positions[1], end_score_final, (y_positions[0] + y_positions[1]) / 2, x_mid=(end_score_x2 + end_score_final) / 2)

    # Losers bracket (adjust vertical positions for equal spacing like Winners Semis)
    end_score_x3 = draw_match(x_positions[0], y_positions[2], "Losers Top 8 Match 1", color_loss, color_loss, "Losers Top 8", size_factor=0.9)
    end_score_x4 = draw_match(x_positions[0], y_positions[3], "Losers Top 8 Match 2", color_loss, color_loss, "Losers Top 8", size_factor=0.9)
    end_score_lq1 = draw_match(x_positions[1], y_positions[2], "Losers Quarter 1", color_loss, color_loss, "Losers Quarter", size_factor=1.0)
    end_score_lq2 = draw_match(x_positions[1], y_positions[3], "Losers Quarter 2", color_loss, color_loss, "Losers Quarter", size_factor=1.0)
    end_score_ls = draw_match(x_positions[2], (y_positions[2] + y_positions[3]) / 2, "Losers Semi", color_loss, color_loss, "Losers Semi", size_factor=1.1)

    # Align the lines for the Losers bracket with similar spacing
    draw_line(end_score_x3, y_positions[2], end_score_lq1, y_positions[2], x_mid=(end_score_x3 + end_score_lq1) / 2)
    draw_line(end_score_x4, y_positions[3], end_score_lq2, y_positions[3], x_mid=(end_score_x4 + end_score_lq2) / 2)
    draw_line(end_score_lq1, y_positions[2], end_score_ls, (y_positions[2] + y_positions[3]) / 2, x_mid=(end_score_lq1 + end_score_ls) / 2)
    draw_line(end_score_lq2, y_positions[3], end_score_ls, (y_positions[2] + y_positions[3]) / 2, x_mid=(end_score_lq2 + end_score_ls) / 2)

    # Losers final and Grand Final
    end_score_lf = draw_match(x_positions[3], (y_positions[2] + y_positions[3]) / 2, "Losers Final", color_loss, color_loss, "Losers Final", size_factor=1.3)
    end_score_gf = draw_match(x_positions[2], (y_positions[0] + y_positions[1]) / 2, "Grand Final", color_win, color_win, "Grand Final", size_factor=1.5)
    end_score_tf = draw_match(x_positions[3], (y_positions[0] + y_positions[1]) / 2, "True Final", color_win, color_win, "True Final", size_factor=1.5)

    draw_line(end_score_gf, (y_positions[0] + y_positions[1]) / 2, end_score_tf, (y_positions[0] + y_positions[1]) / 2, x_mid=(end_score_gf + end_score_tf) / 2)
    draw_line(end_score_ls, (y_positions[2] + y_positions[3]) / 2, end_score_lf, (y_positions[2] + y_positions[3]) / 2, x_mid=(end_score_ls + end_score_lf) / 2)
    draw_line(end_score_final, (y_positions[0] + y_positions[1]) / 2, end_score_gf, (y_positions[0] + y_positions[1]) / 2, x_mid=(end_score_final + end_score_gf) / 2)

    champ_box = ax.add_patch(Rectangle((x_positions[3], y_positions[-1]), 2, 1, facecolor=champ_color, edgecolor='black'))
    champ_box.set_path_effects(shadow)
    ax.text(x_positions[3] + 1, y_positions[-1] + 0.5, "CHAMPION", verticalalignment='center', fontsize=14, fontweight='bold', horizontalalignment='center', color=color_text, fontproperties=bubblegum_font)

    ax.axis('off')

# Set up animation: update the frame of the GIF in a loop
ani = FuncAnimation(fig, draw_bracket, frames=len(frames), interval=100, repeat=True)

# Save the animation as a GIF
ani.save('scenes/bracket_scene.gif', writer='imagemagick')

# Show the animated plot (optional)
plt.show()
