# module import
import pandas as pd
import numpy as np
import multiprocessing as mp
import re
import csv

from nltk.metrics.distance import jaro_winkler_similarity, jaccard_distance
from nltk.util import ngrams


def loadFiles(file_name: str, file_col:int = 0):
    with open(file_name, mode='r', encoding="utf8") as file:
        dr = csv.reader(file)
        next(dr, None)  # skip 1st line
        for row in dr:
            yield row[file_col].strip().lower()


def cleaner(value):
    try:
        url_tags = ['http', 'www.', 'https', '://']
        has_tags = [tag for tag in url_tags if tag in value]
        is_url = re.findall(r'.*[\/|.](.*)\..*', value)

        if len(is_url) > 2 and has_tags:
            return is_url[0]
        return value.strip()
    except:
        pass
    return 'invalid'


# multiprocessing
def worker(df: pd.DataFrame, valid_words: list[str]):
    idx_values = df.index.values
    for idx in range(idx_values[0], int(idx_values[-1])+1):
        value = df.loc[idx]['clean']
        found = 'invalid'
        precision = 0
        
        if value != '':
            temp = [(jaccard_distance(set(ngrams(value, 2)),
                                      set(ngrams(valid_value, 2))), valid_value)
                    for valid_value in valid_words
                    if valid_value[0] == value[0] or valid_value in value]

            if temp:
                recognized_values = sorted(temp, key=lambda acc: acc[0])
                if recognized_values[0][0] <= 0.80:
                    found = recognized_values[0][1]
                    precision = 1-round(recognized_values[0][0], 1)
                else:
                    second_try = sorted([(jaro_winkler_similarity(value, valid_value[1], p=0.1, max_l=100),
                                        valid_value[1])
                                        for valid_value in recognized_values], reverse=True)
                    if second_try and second_try[0][0] >= 0.70:
                        found = second_try[0][1]
                        precision = round(second_try[0][0], 1)

        df.loc[idx, 'found'] = found
        df.loc[idx, 'precision'] = precision

    return df


def manager(df: pd.DataFrame, chunk_size: int, valid_words: list):
    count = 0
    while len(df):
        count += 1
        yield df.iloc[:chunk_size].copy(), valid_words
        df.drop(df.index[:chunk_size], inplace=True)  # free memory


if __name__ == "__main__":
    raw_file = './Resources/ws_invalid.csv'
    valid_file = './Resources/ws_valid.csv'
    output_file = "./Resources/ws_output.csv"

    #load
    raw_words = list(loadFiles(file_name=raw_file))
    valid_words = list(loadFiles(file_name=valid_file))
    
    #cleanup
    df = pd.DataFrame({'raw': raw_words})
    df['clean'] = df['raw'].copy().apply(cleaner)
    df['found'] = None

    #work
    cores = mp.cpu_count()
    chunk_size = 100
    ctx = mp.get_context('spawn')
    pool = ctx.Pool(cores)

    list_df = pool.starmap(worker, manager(df, chunk_size, valid_words))
    pool.close()
    pool.join()
    
    #results
    df = pd.concat(list_df)
    df['found'] = df['found'].str.title()
    df.to_csv(output_file, index=False)