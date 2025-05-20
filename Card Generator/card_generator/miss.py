import json
import pandas as pd
from config import *
from utils import read_cube


def get_description(stats):
    if pd.isnull(stats.trainer):
        return f'The {stats.classification}'
    else:
        return stats.description


def get_encounter_tier_tag(stats, is_evolution):
    # Define encounter tier and trainer tag maps
    encounter_tier_tag_map = {
        'starter': 'Starter Card',
        'weak': 'Weak Encounter Card',
        'moderate': 'Moderate Encounter Card',
        'strong': 'Strong Encounter Card',
        'legendary': 'Legendary Encounter Card',
        'warp': 'Warped Legendary',
        'ultra_beast': 'Ultra Beast Encounter Card',
        'ultra_burst': 'Ultra Burst Encounter Card',
        'noble': 'Noble Encounter Card'
    }

    trainer_tier_tag_map = {
        'Falkner': 'Falkner',
        'Bugsy': 'Bugsy',
        'Whitney': 'Whitney',
        'Morty': 'Morty',
        'Chuck': 'Chuck',
        'Jasmine': 'Jasmine',
        'Pryce': 'Pryce',
        'Clair': 'Clair',
        'Weak Grunt': 'Weak Grunt',
        'Moderate Grunt': 'Moderate Grunt',
        'Strong Grunt': 'Strong Grunt',
        'Weak Ace': 'Weak Ace',
        'Moderate Ace': 'Moderate Ace',
        'Strong Ace': 'Strong Ace',
        'Weak Plasma Grunt': 'Weak Plasma Grunt',
        'Moderate Plasma Grunt': 'Moderate Plasma Grunt',
        'Strong Plasma Grunt': 'Strong Plasma Grunt',
        'Weak Plasma Ace': 'Weak Plasma Ace',
        'Moderate Plasma Ace': 'Moderate Plasma Ace',
        'Strong Plasma Ace': 'Strong Plasma Ace',
        'Proton': 'Proton',
        'Ariana': 'Ariana',
        'Archer': 'Archer',
        'Darach': 'Darach',
        'Argenta': 'Argenta',
        'Palmer': 'Palmer',
        'Thorton': 'Thorton',
        'Dahlia': 'Dahlia',
        'Caitlin': 'Caitlin',
        'Mars': 'Mars',
        'Jupiter': 'Jupiter',
        'Saturn': 'Saturn',
        'Sird': 'Sird',
        'Charon': 'Charon',
        'Cyrus': 'Cyrus',
        'Queen': 'Queen',
        'Wattson': 'Wattson',
        'Flannery': 'Flannery',
        'Norman': 'Norman',
        'Winona': 'Winona',
        'Juan': 'Juan',
        'Sidney': 'Sidney',
        'Will': 'Will',
        'Koga': 'Koga',
        'Bruno': 'Bruno',
        'Karen': 'Karen',
        'Lance': 'Lance',
        'Colress': 'Colress',
        'Zinnia': 'Zinnia'
    }

    # Initialize an empty list to store tags
    tags = []

    # Get the encounter tier tag
    encounter_tag = encounter_tier_tag_map.get(stats.encounter_tier, None)

    # Get the trainer tag if a trainer is specified
    trainer_tag = trainer_tier_tag_map.get(stats.trainer, None)

    # Combine both tags if both are present
    if trainer_tag and encounter_tag:
        tags.append(trainer_tag)
        tags.append(encounter_tag)
    elif trainer_tag:
        tags.append(trainer_tag)
    elif encounter_tag:
        tags.append(encounter_tag)
    
    # Return the list of tags
    return tags


def get_tags(stats, is_evolution=False):
    # Get the encounter tier tag (which is a list of tags)
    encounter_tags = get_encounter_tier_tag(stats, is_evolution)
    
    # Initialize the base tags list
    tags = [
        "Pokemon Card",
        stats.biome,
        stats.climate
    ]
    
    # Add encounter tags to the main tags list
    if encounter_tags:
        tags.extend(encounter_tags)  # Use extend to flatten the list
    
    # Check if the encounter tag is "Warped Legendary" and add "Legendary Encounter Card"
    if "Warped Legendary" in encounter_tags:
        tags.append("Legendary Encounter Card")

    if "Starter Card" in encounter_tags:
        tags.append("Weak Encounter Card")
    
    # Add evolution tag if applicable
    if is_evolution:
        tags.append('Evolution Card')
    
    # Add shiny tag if applicable
    if stats.is_shiny == 1:
        tags.append('Shiny Encounter Card')

    if stats.is_shiny == 0:
        tags.append('Regular Encounter Card')

    if stats.is_shiny == 1 and stats.encounter_tier == "strong" and pd.isna(stats.trainer) and (stats.type_1 == "Bug" or stats.type_2 == "Bug"):
        tags.append('Bug Swarm')
    
    # Filter out any null or NaN values
    return [tag for tag in tags if not pd.isnull(tag)]


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
        'pokedex_name': f'"{stats.pokedex_name}"',
        'internal_name': f'"{stats.internal_name}"',
        'health': stats.health,
        'initiative': stats.initiative,
        'types': get_lua_table_from_fields((stats.type_1, stats.type_2)),
        'type1': stats.type_1,
        'type2': stats.type_2,
        'moves': get_lua_table_from_fields((stats.move_1, stats.move_2, stats.move_3, stats.move_4)),
        'evolve_into': get_lua_table_from_field(stats.evolve_into),
        'evolve_cost': (
            'nil' if stats.evolve_cost == "Hidden" 
            else int(stats.evolve_cost) if not pd.isnull(stats.evolve_cost) 
            else 'nil'
        ),
        'encounter_tier': f'"{stats.encounter_tier.capitalize()}"',
        'move_name': f'"{stats.move_name}"',
        'move_type': f'"{stats.move_type.capitalize()}"',
        'move_attack_strength': f'"{stats.move_attack_strength}"',
        'climate': f'"{stats.climate}"',
        'biome': f'"{stats.biome}"'
    }
    lua_script_lines = [f'{variable} = {value}' for variable, value in local_variables.items()]
    return '\n'.join(lua_script_lines)



def get_card_json(deck_json, i, j, stats, is_evolution=False):
    with open(CARD_OBJECT_TEMPLATE) as f:
        card_json = json.load(f)

    card_json['CardID'] = j * 100 + i
    card_json['Nickname'] = stats.pokedex_name + (f' ({stats.description})' if not pd.isnull(stats.description) else '')
    card_json['Description'] = get_description(stats)
    card_json['Tags'] = get_tags(stats, is_evolution)
    card_json['LuaScript'] = get_lua_script(stats)
    card_json['Hands'] = True
    card_json['CustomDeck'][str(j)] = {
        'FaceURL': deck_json['ObjectStates'][0]['CustomDeck'][str(j)]['FaceURL'],
        'BackURL': deck_json['ObjectStates'][0]['CustomDeck'][str(j)]['BackURL'],
        'NumWidth': 10,
        'NumHeight': 7,
        'HideWhenFaceDown': False,
        'BackIsHidden': True,
        'Hands': True,
        'UniqueBack': True,
        'Type': 0
    }
    return card_json


def add_card_to_deck(deck_json, i, j, k, stats, deck_name):
    is_evolution = deck_name == "Evolution Pokemon Deck"
    
    card_json = get_card_json(deck_json, i, j, stats, is_evolution=is_evolution)
    
    if stats.state == 0:
        deck_json['ObjectStates'][0]['DeckIDs'].append(j * 100 + i)
        deck_json['ObjectStates'][0]['ContainedObjects'].append(card_json)
    elif stats.state == 1:
        deck_json['ObjectStates'][0]['DeckIDs'].append(j * 100 + i)
        deck_json['ObjectStates'][0]['ContainedObjects'].append(card_json)
        deck_json['ObjectStates'][0]['ContainedObjects'][-1]['States'] = {}
    elif stats.state > 1:
        contained_object = deck_json['ObjectStates'][0]['ContainedObjects'][-(k + 1)]
        if 'States' not in contained_object:
            contained_object['States'] = {}
        contained_object['States'][str(stats.state)] = card_json


def run():
    print('Generating deck objects:')
    DECK_OBJECT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(DECK_OBJECT_TEMPLATE) as f:
        base_deck_json = json.load(f)

    deck_definitions = [
        {"name": "Rocket Pokemon Deck", "filter": lambda stats: stats.trainer == "Rocket Grunt" or stats.trainer == "Rocket Ace"},
        {"name": "Plasma Pokemon Deck", "filter": lambda stats: stats.trainer == "Plasma Grunt" or stats.trainer == "Plasma Ace"}
    ]

    for deck_definition in deck_definitions:
        deck_name = deck_definition["name"]
        filter_func = deck_definition["filter"]

        deck_json = base_deck_json.copy()
        deck_json['ObjectStates'][0]['DeckIDs'] = []
        deck_json['ObjectStates'][0]['ContainedObjects'] = []

        output_path = DECK_OBJECT_OUTPUT_DIR / f'{deck_name.replace(" ", "_").lower()}.json'

        i, j = 0, 0
        for _, stats in read_cube(sheet_name='pokemon').iterrows():
            if not filter_func(stats):
                continue

            if (i == 0 and j == 0) or i == 70:
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)] = {
                    'NumWidth': 10,
                    'NumHeight': 7,
                    'BackIsHidden': True,
                    'UniqueBack': True,
                    'Type': 0
                }
                face_url = input(f'Enter the Cloud URL for {CARD_FRONTS_DECK_IMG.format(j=j)} for {deck_name}:')
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)]['FaceURL'] = face_url
                back_url = input(f'Enter the Cloud URL for {CARD_BACKS_DECK_IMG.format(j=j)} for {deck_name}:')
                deck_json['ObjectStates'][0]['CustomDeck'][str(j + 1)]['BackURL'] = back_url
                i = 0
                j += 1

            add_card_to_deck(deck_json, i, j, 0, stats, deck_name)
            i += 1

        with open(output_path, 'w') as f:
            json.dump(deck_json, f)
        print(f'{deck_name} saved to {output_path}')

    print('Deck generation complete.')

if __name__ == '__main__':
    run()