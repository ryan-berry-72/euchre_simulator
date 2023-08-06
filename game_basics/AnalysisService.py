import pandas as pd


def analyze_cards(csv_file):
    df = pd.read_csv(csv_file)
    print(df.head())
