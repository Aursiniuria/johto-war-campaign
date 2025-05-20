from io import BytesIO

import pandas as pd
import requests
from PIL import ImageDraw
from tqdm import tqdm

from config import *
from utils import xy, read_cube, get_img, text_font, title_font, wrapped_text


#
# Base
#


def compose_base(stats):
    if stats.move_tier == "Plasma Card" and stats.move_attack_strength != "blank":
        card_base = 'Plasma Move'
    elif stats.move_tier == "Plasma Card":
        card_base = 'Plasma Ability'
    elif stats.move_type == "shadow":
        card_base = 'Shadow'
    else:
        card_base = 'TM'
    
    base_img = get_img(CARD_ASSETS_DIR / 'card_bases' / f'{card_base}.png', xy(16, 28))
    return base_img


def compose_back(stats):
    if stats.move_tier == "Plasma Move":
        card_base = 'Plasma Move'
    elif stats.move_tier == "Plasma Ability":
        card_base = 'Plasma Ability'
    elif stats.move_type == "shadow":
        card_base = 'Shadow'
    else:
        card_base = 'TM'

    base_img = get_img(CARD_ASSETS_DIR / 'card_backs' / f'{card_base}.png', xy(16, 28))
    return base_img

def add_move(img, stats):
    if stats.move_tier not in ["blank"]:
        move_img = get_img(TM_MOVES_OUTPUT_DIR / f'{stats.move_name}.png', xy(14.5, 7.5))
        img.paste(move_img, xy(0.75, 19.75), move_img)

def add_back_move(img, stats):
    if stats.move_tier not in ["blank", "Plasma Move", "Plasma Ability"] and stats.move_type not in ["shadow"]:
        move_img = get_img(TM_MOVES_OUTPUT_DIR / f'{stats.move_name}.png', xy(14.5, 7.5))
        img.paste(move_img, xy(0.75, 19.75), move_img)


def add_emblem(img, stats):   
    if VANILLA_EMBLEM_PATH.is_file():
        emblem_name = 'vanilla'
    else:
        emblem_name = 'custom'
    emblem_img = get_img(CARD_ASSETS_DIR / 'emblems' / f'{emblem_name}.png', xy(0.5, 0.5))
    img.paste(emblem_img, xy(15, 27), emblem_img)

def add_back_emblem(img, stats):   
    if stats.move_tier not in ["blank", "Plasma Move", "Plasma Ability"] and stats.move_type not in ["shadow"]:
        if VANILLA_EMBLEM_PATH.is_file():
            emblem_name = 'vanilla'
        else:
            emblem_name = 'custom'
        emblem_img = get_img(CARD_ASSETS_DIR / 'emblems' / f'{emblem_name}.png', xy(0.5, 0.5))
        img.paste(emblem_img, xy(15, 27), emblem_img)

#
# Entry
#

def generate_card_backs(overwrite=True):
    print('Generating card backs:')
    TM_BACKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='moves')
    for i, stats in tqdm(df.iterrows(), total=df.shape[0]):
        if stats.move_tier in ["blank"]:
            continue
        output_path = TM_BACKS_OUTPUT_DIR / f'{stats.move_tier}_{stats.move_name.lower()}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = compose_back(stats)
        add_back_move(img, stats)
        add_back_emblem(img, stats)

        # base_img.paste(img, xy(0, 0), img)
        img.save(output_path)

def run(overwrite=True):
    print('Generating card fronts:')
    TM_FRONTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='moves')
    for i, stats in tqdm(df.iterrows(), total=df.shape[0]):
        if stats.move_tier in ["blank"]:
            continue
        output_path = TM_FRONTS_OUTPUT_DIR / f'{stats.move_tier}_{stats.move_name.lower()}.png'
        if output_path.is_file() and not overwrite:
            continue

        img = compose_base(stats)
        add_move(img, stats)
        add_emblem(img, stats)

        # base_img.paste(img, xy(0, 0), img)
        img.save(output_path)
    generate_card_backs(overwrite)


if __name__ == '__main__':
    run(overwrite=True)
