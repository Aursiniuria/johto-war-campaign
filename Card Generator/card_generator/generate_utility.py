from io import BytesIO

import pandas as pd
import requests
from PIL import ImageDraw
from tqdm import tqdm

from config import *
from utils import xy, read_cube, get_img, text_font, title_font, bold_font, wrapped_text


#
# Base
#

def compose_base(stats):
    base_img = get_img(CARD_ASSETS_DIR / 'card_bases' / f'{stats.utility_type if stats.utility_type == "QUEST" else stats.image_type}.png',
    xy(16, 28)
)

    return base_img

def add_move(img, stats):
    d = ImageDraw.Draw(img)

    # Determine fill color based on image_type
    fill_color = WHITE_COLOUR if stats.image_type == "Warp" else DARK_COLOUR

    if stats.utility_type == "QUEST":
        # Card Name (Bolded)
        wrapped_text(d, stats.card_name, bold_font(48), boundaries=(10.81, 3.44), xy=xy(8, 3.07), fill=fill_color,
                    anchor='mm', align='center')
    
        # Card Type
        wrapped_text(d, stats.utility_type, text_font(33), boundaries=(8.7, 1.4), xy=xy(8, 5.38), fill=fill_color,
                    anchor='mm', align='center')

        # Image
        type_img = get_img(CARD_ASSETS_DIR / 'card_images' / f'{stats.utility_name}.png', xy(15.36, 21.1))
        img.paste(type_img, xy(0.32, 6.59), type_img)
    
        # Effect
        wrapped_text(d, stats.card_effect, text_font(36), boundaries=(13.82, 19.92), xy=xy(8, 17.14), fill=fill_color,
                 anchor='mm', align='center') 
    else:
        # Card Name (Bolded)
        wrapped_text(d, stats.card_name, bold_font(48), boundaries=(10.81, 3.44), xy=xy(8, 3.07), fill=fill_color,
                    anchor='mm', align='center')
    
        # Card Type
        wrapped_text(d, stats.utility_type, text_font(33), boundaries=(8.7, 1.4), xy=xy(8, 5.38), fill=fill_color,
                    anchor='mm', align='center')

        # Image
        type_img = get_img(CARD_ASSETS_DIR / 'card_images' / f'{stats.utility_name}.png', xy(14.56, 9.47))
        img.paste(type_img, xy(0.72, 6.69), type_img)
    
        # Effect
        wrapped_text(d, stats.card_effect, text_font(36), boundaries=(13.82, 10.09), xy=xy(8, 22.04), fill=fill_color,
                    anchor='mm', align='center')

def add_emblem(img):
    if VANILLA_EMBLEM_PATH.is_file():
        emblem_name = 'vanilla'
    else:
        emblem_name = 'custom'
    emblem_img = get_img(CARD_ASSETS_DIR / 'emblems' / f'{emblem_name}.png', xy(0.5, 0.5))
    img.paste(emblem_img, xy(15, 27), emblem_img)

def add_rocket(img, stats):
    if stats.rocket_ignore == 1:
        emblem_img = get_img(CARD_ASSETS_DIR / 'trainer_icons' / f'Rocket Ace.png', xy(0.75, 0.75))
        img.paste(emblem_img, xy(0.25, 26.925), emblem_img)

def generate_card_backs(overwrite):
    print('Generating card backs:')
    UTILITY_CARD_BACKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='others')
    for _, stats in tqdm(df.iterrows(), total=df.shape[0]):
        if stats.image_type != "Warp":
            directory_name = stats.image_type
        else:
            directory_name = "Shrine"
        output_dir = (OUTPUT_DIR / directory_name / 'card_backs')
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f'{stats.utility_name}.png'
        if output_path.is_file() and not overwrite:
            continue

        if stats.image_type != "Gamble":
            backimage = stats.image_type
        else:
            backimage = stats.utility_type
        img = get_img(CARD_ASSETS_DIR / 'card_backs' / f'{backimage}.png', xy(16, 28))
        img.save(output_path)
#
# Entry
#

def run(overwrite=True):
    print('Generating card fronts:')
    
    df = read_cube(sheet_name='others')
    for i, stats in tqdm(df.iterrows(), total=df.shape[0]):
        directory_name = stats.image_type if stats.image_type != "Warp" else "Shrine"
        output_dir = (OUTPUT_DIR / directory_name / 'card_fronts')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f'{i}_{stats.utility_name.lower()}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = compose_base(stats)

        add_move(img, stats)
        add_emblem(img)
        add_rocket(img, stats)

        img.save(output_path)
    generate_card_backs(overwrite)


if __name__ == '__main__':
    run(overwrite=True)
