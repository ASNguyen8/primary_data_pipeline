from tqdm import tqdm
import seaborn as sns

from helpers import *

if __name__ == "__main__":
    
    # # Sample csv for test
    # csv_path = "https://raw.githubusercontent.com/ASNguyen8/ASNguyen8.github.io/master/docs/essence.csv"
    # csv_sep = ";"
    # col_dtypes = {'Prix': "float64", 'Volume': "float64", 'Prix_litre': "float64", 'TVA': "float64", 'Pays': "object"}
    # parse_dates = ["Date"]

    # Prior informations about data to manually provide (atm)
    csv_path = input("Path of csv data : ")
    csv_sep = input("CSV Separator : ")

    df = pd.read_csv(csv_path, sep=csv_sep)
    col_dtypes = {}
    parse_dates = []
    dtypes = ["float64", "int64", "object", "bool", "datetime64", "timedelta", "category",]

    print("Please specify the datatype of csv columns...")
    print(f"Choose between {dtypes}...")
    for col in df.columns:
        new_dtype = input(f"{col} : ")
        if new_dtype == "datetime64":
            parse_dates.append(col)
            continue
        while new_dtype not in dtypes:
            print(f"Please choose between {dtypes}...")
            new_dtype = input(f"{col} : ")
            if new_dtype == "datetime64":
                parse_dates.append(col)
                continue
        col_dtypes[col] = new_dtype
    df = pd.read_csv(csv_path, sep=csv_sep, dtype=col_dtypes, parse_dates=parse_dates)

    # Create the folder that contains results of the pipeline
    folder_name = "primary_data_pipeline_results"
    count = len([folder for folder in os.listdir(os.getcwd()) if folder_name in folder])
    folder_name = os.path.join(os.getcwd(), folder_name + f"_({count})"*(count > 0))
    os.mkdir(folder_name)

    # Informations about columns
    figsize = (12, 8)

    print("Missing values...", end="")
    missing_values = {col: df[col].isna().sum() for col in df.columns}
    barh_dict(
        data=missing_values,
        title="Missing values in dataframe\n",
        figname=os.path.join(folder_name, "missing_values_per_columns"),
        figsize=figsize
        )
    df = df.dropna().reset_index(drop=True)
    print("Done\n")

    df.describe().to_csv(os.path.join(folder_name, "statistics.csv"), sep=csv_sep, index=True)
    print("Compute descriptive statistics...\n")

    for col in tqdm(col_dtypes.keys(), desc="Plotting box/bar plot of data columns..."):
        plot_column_by_dtype(
            col_data=df[col],
            col_name=col,
            dirname=folder_name,
            figsize=figsize,
            percentage=False
            )
        if df[col].dtype == "object":
            plot_column_by_dtype(
                col_data=df[col],
                col_name=col,
                dirname=folder_name,
                figsize=figsize,
                percentage=True
                )

    for col in tqdm(df.columns, desc="Plotting histograms of numeric data columns..."):
        if df[col].dtype in ['float64', 'int64']:
            figname = os.path.join(folder_name, f"hist_{col}")
            hist_col(data=df[col], title=col, figname=figname, density=False, figsize=figsize)
            hist_col(data=df[col], title=col, figname=figname, density=True, figsize=figsize)

    print("Standardize numeric data...", end="")
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = standardize_col(df[col])
    print("Done\n")
    
    print("One hot encoding...", end="")
    df_dummies = pd.get_dummies(df, columns=[col for col in df.columns if df[col].dtype in ['object', 'category']])
    print("Done\n")
    
    print("Computing correlation...")
    # corr = df_dummies[[col for col in df_dummies.columns if df_dummies[col].dtype in ['float64', 'int64']]].corr()
    corr = df_dummies.corr()
    corr.to_csv(os.path.join(folder_name, "correlations.csv"), sep=csv_sep, index=False)
    mask = 1 - np.tril(np.ones_like(corr))
    plt.figure(figsize=figsize)
    sns.heatmap(corr, mask=mask, vmin=-1, vmax=1, annot=True, cmap='coolwarm')
    plt.title("Correlation between variables\nCategorical variables are one-hot encoded")
    plt.savefig(os.path.join(folder_name, "correlations"))
    plt.close()

    new_csv_name = os.path.basename(csv_path)
    new_csv_name = new_csv_name[:new_csv_name.find('.csv')] + "_cleaned.csv"
    df_dummies.to_csv(os.path.join(folder_name, new_csv_name), sep=csv_sep, index=False)

    print("\nPrimary exploration of data is done.")
    os.startfile(folder_name)
