import csv
from config import DATA_DIR

class Data:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Data, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self._init_it()

    def _read_tsv(cls, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t', fieldnames=['food_id', 'food_name'])
            return [row for row in reader]

    def _init_it(self):
        self._food_data_path = f'{DATA_DIR}/food_details'
        self._food_name_to_id = {row['food_name']: row['food_id'] for row in self._read_tsv(f'{DATA_DIR}/name_foodID_correspondence.tsv')}

    def _init_en(self):
        self._food_data_path = 'food_details_EN'
        self._food_name_to_id = {row['food_name']: row['food_id'] for row in self._read_tsv(f'{DATA_DIR}/name_foodID_correspondence_EN.tsv')}

    def get_food_list(self) -> list[str]:
        return self._food_name_to_id.keys()

    def get_food_id(self, food_name : str) -> int:
        return self._food_name_to_id[food_name]

    def switch_language(self, language):
        {
            'Italian' : self._init_it,
            'English' : self._init_en
        }[language]()

    def read_food_details(self, id : str) -> dict[str, float]:
        with open(f'{self._food_data_path}/{id}', 'r') as f:
            reader = csv.reader(f, delimiter='\t')
            return {rows[0]: float(rows[1]) for rows in reader if rows[1].replace('.', '', 1).isdigit()}

    def search_food(self, search_term : str) -> list[str]:
        return [food_name for food_name in self._food_name_to_id.keys() if search_term.lower() in food_name.lower()]
