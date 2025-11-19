import csv

def read_table(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        return [row for row in reader]

def write_tsv(file_path, data, headers):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers, delimiter='\t')
        writer.writeheader()
        writer.writerows(data)

def load_blank_table():
    return read_table('blank_table.tsv')
