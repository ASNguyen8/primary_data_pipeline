import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

def f():
    pass


if __name__ == "__main__":
    
    # Prior informations about data to manually provide (atm)
    # csv_path = input("Path of csv data : ")
    # csv_sep = input("CSV Separator : ")
    csv_path = "https://raw.githubusercontent.com/ASNguyen8/ASNguyen8.github.io/master/docs/essence.csv"
    csv_sep = ";"

    # Informations about columns
    df = pd.read_csv(csv_path, sep=csv_sep)
    for col in df.columns:
        print(f"{col} :\t{df[col].dtype}")

    ## Columns with Float64 dtype
    for col in df.columns:
        if df[col].dtype != "float64":
            continue
        plt.figure()
        plt.boxplot(df[col])
        plt.title(col)
        plt.show()
        plt.close()
