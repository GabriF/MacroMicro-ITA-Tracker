import csv
import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller build.
    """
    if hasattr(sys, "_MEIPASS"):
        # When running from the PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # When running from source, assume this file is in src/ and go one level up
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)


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
    data_dir = resource_path("data")
    file_path = os.path.join(data_dir, "blank_table.tsv")
    return read_table(file_path)
