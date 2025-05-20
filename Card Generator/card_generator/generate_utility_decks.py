from PIL import Image
from tqdm import tqdm

from config import *
from utils import xy, pos, read_cube, get_img

def get_card_deck_base_img():
    return Image.new('RGBA', pos(10, 7))

def add_card_at_pos(base_img, pokemon_card_path, position):
    img = get_img(pokemon_card_path, xy(8, 14))
    base_img.paste(img, position, img)
    return base_img

def run():
    possible_image_types = ["Excavated", "Disaster", "Fortune", "Influence", "Sunken", "Utility", "Gamble"]
    for image_type_filter in possible_image_types:
        print(f'Generating {image_type_filter} decks:')

        i, j = 0, 0
        df = read_cube(sheet_name='others')

        # Filter rows based on image_type
        df = df[df['image_type'] == image_type_filter]

        card_fronts_deck_img = get_card_deck_base_img()
        card_backs_deck_img = get_card_deck_base_img()

        for row_number, stats in tqdm(df.iterrows(), total=df.shape[0]):
            directory_name = stats.image_type if stats.image_type != "Warp" else "Shrine"
            output_dir = (OUTPUT_DIR / directory_name / 'decks')
            output_dir.mkdir(parents=True, exist_ok=True)

            if i == 70:
                card_fronts_deck_img.save(output_dir / CARD_FRONTS_DECK_IMG.format(j=j))
                card_fronts_deck_img = get_card_deck_base_img()
                card_backs_deck_img.save(output_dir / CARD_BACKS_DECK_IMG.format(j=j))
                card_backs_deck_img = get_card_deck_base_img()
                i = 0
                j += 1

            pokemon_card_path = OUTPUT_DIR / directory_name / 'card_fronts' / f'{row_number}_{stats.utility_name}.png'
            card_back_path = OUTPUT_DIR / directory_name / 'card_backs' / f'{stats.utility_name}.png'
            card_pos = pos(i % 10, (i // 10) % 7)

            card_fronts_deck_img = add_card_at_pos(card_fronts_deck_img, pokemon_card_path, card_pos)
            card_backs_deck_img = add_card_at_pos(card_backs_deck_img, card_back_path, card_pos)
            i += 1
        else:
            card_fronts_deck_img.save(output_dir / CARD_FRONTS_DECK_IMG.format(j=j))
            card_backs_deck_img.save(output_dir / CARD_BACKS_DECK_IMG.format(j=j))


if __name__ == '__main__':
        run()
