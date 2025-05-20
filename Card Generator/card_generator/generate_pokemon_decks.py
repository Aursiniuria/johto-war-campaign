from PIL import Image
from tqdm import tqdm
from config import *
from utils import xy, pos, read_cube, get_img
import pandas as pd


def get_card_deck_base_img():
    return Image.new('RGBA', pos(10, 7))


def add_card_at_pos(base_img, pokemon_card_path, position):
    img = get_img(pokemon_card_path, xy(8, 14))
    base_img.paste(img, position, img)
    return base_img


def add_move(img, stats):
    move_img = get_img(POKEMON_MOVES_OUTPUT_DIR / f'{stats.move_name}.png', xy(14.5, 7.5))
    img.paste(move_img, xy(0.75, 19.75), move_img)


def run():
    print('Generating decks:')
    POKEMON_DECKS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = read_cube(sheet_name='pokemon')

    deck_configurations = [
        ("Weak Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "weak" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Starter Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "starter" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Shiny Weak Pokemon", lambda stats: stats.is_shiny == 1 and stats.encounter_tier == "weak" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Moderate Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "moderate" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Shiny Moderate Pokemon", lambda stats: stats.is_shiny == 1 and stats.encounter_tier == "moderate" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Strong Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "strong" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Shiny Strong Pokemon", lambda stats: stats.is_shiny == 1 and stats.encounter_tier == "strong" and pd.isna(stats.trainer) and stats.climate != "Fossil" and stats.evo_only == 0),
        ("Quest Legendary Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "legendary" and pd.isna(stats.trainer) and stats.evo_only == 0),
        ("Shiny Quest Legendary Pokemon", lambda stats: stats.is_shiny == 1 and stats.encounter_tier == "legendary" and pd.isna(stats.trainer) and stats.evo_only == 0),
        ("Warp Legendary Pokemon", lambda stats: stats.is_shiny == 0 and stats.encounter_tier == "warp" and pd.isna(stats.trainer) and stats.evo_only == 0),
        ("Shiny Warp Legendary Pokemon", lambda stats: stats.is_shiny == 1 and stats.encounter_tier == "warp" and pd.isna(stats.trainer) and stats.evo_only == 0),
        ("Rocket Pokemon", lambda stats: stats.trainer == "Rocket Grunt" or stats.trainer == "Rocket Ace"),
        ("Plasma Pokemon", lambda stats: stats.trainer == "Plasma Ace" or stats.trainer == "Plasma Grunt"),
        ("Fossil Pokemon", lambda stats: stats.is_shiny == 0 and stats.climate == "Fossil" and stats.evo_only == 0),
        ("Shiny Fossil Pokemon", lambda stats: stats.is_shiny == 1 and stats.climate == "Fossil" and stats.evo_only == 0),
        ("Gym Pokemon", lambda stats: stats.trainer in ["Falkner", "Bugsy", "Whitney", "Morty", "Chuck", "Jasmine", "Pryce", "Clair"]),
        ("Boss Pokemon", lambda stats: stats.trainer in ["Proton", "Ariana", "Archer", "Giovanni", "Juan", "Sidney", "Flannery", "Norman", "Wattson", "Winona", "Darach", "Argenta", "Palmer", "Thorton", "Dahlia", "Caitlin", "Queen", "Lance", "Koga", "Bruno", "Karen", "Will", "Cyrus", "Mars", "Jupiter", "Saturn", "Sird", "Charon"]),
        ("Event Pokemon Deck", lambda stats: stats.trainer in ["Colress", "Zinnia"] or (stats.is_shiny == 1 and stats.encounter_tier == "strong" and pd.isna(stats.trainer) and stats.internal_name != "Shiny Armaldo" and (stats.type_1 == "Bug" or stats.type_2 == "Bug"))),
        ("Evolution Pokemon", lambda stats: stats.evo_only == 1 or stats.number_in_deck > 1)
    ]

    for folder_name, condition in deck_configurations:
        folder_path = POKEMON_DECKS_OUTPUT_DIR / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        filtered_df = df[df.apply(condition, axis=1)]
        i, j = 0, 0
        card_fronts_deck_img = get_card_deck_base_img()
        card_backs_deck_img = get_card_deck_base_img()

        for row_number, stats in tqdm(filtered_df.iterrows(), total=filtered_df.shape[0]):
            if i == 70:
                card_fronts_deck_img.save(folder_path / CARD_FRONTS_DECK_IMG.format(j=j))
                card_fronts_deck_img = get_card_deck_base_img()
                card_backs_deck_img.save(folder_path / CARD_BACKS_DECK_IMG.format(j=j))
                card_backs_deck_img = get_card_deck_base_img()
                i = 0
                j += 1

            pokemon_card_path = POKEMON_CARD_FRONTS_OUTPUT_DIR / f'{row_number}_{stats.pokedex_name}.png'
            card_back_path = (
                CARD_ASSETS_DIR / 'card_backs' / f'{stats.trainer}.png' if pd.notna(stats.trainer) else 
                POKEMON_CARD_BACKS_OUTPUT_DIR / f'{stats.move_name}.png' if pd.notna(stats.move_name) else
                CARD_ASSETS_DIR / 'card_backs' / 'default.png'  # Default card back image
            )
            card_pos = pos(i % 10, (i // 10) % 7)

            card_fronts_deck_img = add_card_at_pos(card_fronts_deck_img, pokemon_card_path, card_pos)
            card_backs_deck_img = add_card_at_pos(card_backs_deck_img, card_back_path, card_pos)
            i += 1

        card_fronts_deck_img.save(folder_path / CARD_FRONTS_DECK_IMG.format(j=j))
        card_backs_deck_img.save(folder_path / CARD_BACKS_DECK_IMG.format(j=j))

    input('Now upload the images under output/decks using the Modding -> Cloud Manager in Tabletop Simulator, then press enter to continue...')


if __name__ == '__main__':
    run()