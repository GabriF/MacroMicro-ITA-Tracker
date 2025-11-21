import csv
import os
from config import DATA_DIR, FOOD_DETAILS_DIR, FOOD_DETAILS_EN_DIR
from utils import resource_path


class Data:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Data, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._init_it()
        self._serving_size: dict[str, int] = {}
        
        serving_file = os.path.join(DATA_DIR, "serving_size.tsv")
        with open(serving_file, 'r', encoding='utf-8') as f:
            for line in f.readlines()[1:]:
                tokens = line.split()
                self._serving_size[tokens[0]] = tokens[1]

    def _read_tsv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t',
                                    fieldnames=['food_id', 'food_name'])
            return [row for row in reader]

    def _init_it(self):
        self._food_data_path = FOOD_DETAILS_DIR
        corr_tsv = os.path.join(DATA_DIR, "name_foodID_correspondence.tsv")
        self._food_name_to_id = {
            row['food_name']: row['food_id']
            for row in self._read_tsv(corr_tsv)
        }

    def _init_en(self):
        self._food_data_path = FOOD_DETAILS_EN_DIR
        corr_tsv = os.path.join(DATA_DIR, "name_foodID_correspondence_EN.tsv")
        self._food_name_to_id = {
            row['food_name']: row['food_id']
            for row in self._read_tsv(corr_tsv)
        }

    def get_food_list(self) -> list[str]:
        return list(self._food_name_to_id.keys())

    def get_food_id(self, food_name: str) -> int:
        return self._food_name_to_id[food_name]

    def switch_language(self, language):
        {
            'Italian': self._init_it,
            'English': self._init_en
        }[language]()

    def read_food_details(self, id: str) -> dict[str, float]:
        file_path = os.path.join(self._food_data_path, id)
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            return {
                rows[0]: float(rows[1])
                for rows in reader
                if rows[1].replace('.', '', 1).isdigit()
            }

    def get_serving_size(self, id: str) -> int:
        return self._serving_size[id]

    def search_food(self, search_term: str) -> list[str]:
        return [
            food_name
            for food_name in self._food_name_to_id.keys()
            if search_term.lower() in food_name.lower()
        ]
