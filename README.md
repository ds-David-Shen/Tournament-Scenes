# Tournament Scenes

## Description
This project generates tournament scene visualizations using Python (`matplotlib`, `Pillow`). It includes customizable player cards, brackets, and commentary scenes.

## Setup

### Clone the Repository
```bash
git clone https://github.com/yourusername/Tournament-Scenes.git
cd Tournament-Scenes
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Running

### Generate Scenes
- **Bracket Scene**: Generate using `bracket.py`, which creates `scenes/bracket_scene.gif`.
    - Player data is in the player data section of `bracket.py`.

```bash
python bracket.py
```

- **Versus Screen**: Generate using `versus.py`, which creates `scenes/versus_screen.gif`.
    - Modify the user ID and seed for the two players.

```bash
python versus.py
```

- **Commentary Scene**: Generate using `commentary.py`, which creates `scenes/commentary_scene.gif`.
    - Modify the user IDs for the two commentators.

```bash
python commentary.py
```

## Project Structure
- `player_cards.py`: Player card generation.
- `bracket.py`: Tournament brackets.
- `versus.py`: Versus screen generation.
- `commentary.py`: Commentary scenes.
- `scenes/`: Contains generated GIFs (bracket_scene.gif, versus_screen.gif, commentary_scene.gif).
- `assets/`: Contains images (avatars, backgrounds, etc.).
