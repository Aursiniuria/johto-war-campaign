import json

import pandas as pd

from config import *
from utils import read_cube

def get_tags(stats):
    if stats.image_type == "Excavated":
        return ["Excavated Treasure Card"]
    elif stats.image_type == "Disaster":
        return ["Disaster Card"]
    elif stats.image_type == "Fortune":
        return ["Fortune Card"]
    elif stats.image_type == "Influence":
        return ["Influence Card"]
    elif stats.image_type == "Sunken":
        return ["Sunken Treasure Card"]
    elif stats.utility_type == "COMPANION":
        return ["Companion Card"]
    elif stats.utility_type == "BATTLE":
        return ["Battle Card"]
    elif stats.utility_type == "QUEST":
        return ["Quest Card"]
    elif stats.image_type == "Utility":
        return ["Utility Card"]
    elif stats.utility_type == "PRIZE GAMBLE CARD":
        return ["Prize Gamble Card"]
    elif stats.utility_type == "ADDITIVE GAMBLE CARD":
        return ["Additive Gamble Card"]
    elif stats.utility_type == "MULTIPLY GAMBLE CARD":
        return ["Multiplicative Gamble Card"]
    elif stats.utility_type == "BETTING GAMBLE CARD":
        return ["Bet Gamble Card"]
    else:
        return []

def get_lua_table_from_fields(fields):
    values_list = [f'"{value.capitalize()}"' for value in fields if not pd.isnull(value)]
    values_str = ','.join(values_list)
    return '{' + values_str + '}'

def get_lua_table_from_field(field):
    if not pd.isnull(field):
        values_list = [f'"{value}"' for value in field.split('/')]
        values_str = ','.join(values_list)
        return '{' + values_str + '}'
    return 'nil'

def get_lua_script(stats):
    local_variables = {
        'internal_name': f'"{stats.internal_name}"'
    }
    lua_script_lines = [f'{variable} = {value}' for variable, value in local_variables.items()]

    if not pd.isnull(stats.lua):
        lua_script_lines.append(stats.lua)

    return '\n'.join(lua_script_lines)

def get_card_json(deck_json, i, j, stats, is_evolution=False):
    with open(CARD_OBJECT_TEMPLATE) as f:
        card_json = json.load(f)

    card_json['CardID'] = j * 100 + i
    card_json['Nickname'] = stats.internal_name
    card_json['Description'] = stats.classification
    card_json['Tags'] = get_tags(stats)
    card_json['LuaScript'] = get_lua_script(stats)
    card_json['Hands'] = True
    card_json['HideWhenFaceDown'] = True
    card_json['CustomDeck'][str(j)] = {
        'FaceURL': deck_json['ObjectStates'][0]['CustomDeck'][str(j)]['FaceURL'],
        'BackURL': deck_json['ObjectStates'][0]['CustomDeck'][str(j)]['BackURL'],
        'NumWidth': 10,
        'NumHeight': 7,
        'BackIsHidden': True,
        'Hands': True,
        'UniqueBack': True,
        'Type': 0
    }
    return card_json

def add_card_to_deck(deck_json, i, j, k, stats):
    card_json = get_card_json(deck_json, i, j, stats)
    if stats.state == 0:
        deck_json['ObjectStates'][0]['DeckIDs'].append(j * 100 + i)
        deck_json['ObjectStates'][0]['ContainedObjects'].append(card_json)
    elif stats.state == 1:
        deck_json['ObjectStates'][0]['DeckIDs'].append(j * 100 + i)
        deck_json['ObjectStates'][0]['ContainedObjects'].append(card_json)
        deck_json['ObjectStates'][0]['ContainedObjects'][-1]['States'] = {}
    elif stats.state > 1:
        deck_json['ObjectStates'][0]['ContainedObjects'][-(k + 1)]['States'][int(stats.state)] = card_json

def run():
    possible_image_types = ["Excavated", "Disaster", "Fortune", "Influence", "Sunken", "Utility", "Gamble"]
    for image_type_filter in possible_image_types:
        print(f'Generating {image_type_filter} deck object')
        DECK_OBJECT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with open(DECK_OBJECT_TEMPLATE) as f:
            deck_json = json.load(f)
        output_path = DECK_OBJECT_OUTPUT_DIR / f'{image_type_filter}_Deck.json'

        i, j = 0, 0
        df = read_cube(sheet_name='others')

        # Filter rows based on image_type
        df = df[df['image_type'] == image_type_filter]

        for _, stats in df.iterrows():
            if (i == 0 and j == 0) or i == 70:
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)] = {
                    'NumWidth': 10,
                    'NumHeight': 7,
                    'BackIsHidden': True,
                    'Hands': True,
                    'UniqueBack': True,
                    'Type': 0
                }
                face_url = input(f'Enter the Cloud URL for {CARD_FRONTS_DECK_IMG.format(j=j)} for {image_type_filter}:')
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)]['FaceURL'] = face_url
                back_url = input(f'Enter the Cloud URL for {CARD_BACKS_DECK_IMG.format(j=j)} for {image_type_filter}:')
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)]['BackURL'] = back_url
                i = 0
                j += 1

            for k in range(stats.number_in_deck):
                add_card_to_deck(deck_json, i, j, k, stats)

            i += 1
        else:
            with open(output_path, 'w') as f:
                json.dump(deck_json, f)
        print(
            f'Now place the deck.json file for {image_type_filter} found in output/deck_object into your local Documents/My Games/Tabletop Simulator/Saves/Saved Objects folder. You can now import them in Tabletop Simulator by going to Objects -> Saved Objects.')

if __name__ == '__main__':
        run()
