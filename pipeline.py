import json
from tqdm import tqdm
import seaborn as sns
from shutil import make_archive, rmtree

from helpers import *


def primary_data_pipeline(csv_params_path: str, figsize: tuple=(12, 8)):

    # Load csv
    with open(csv_params_path, 'r') as json_file:
        params = json.load(json_file)
    df = pd.read_csv(**params)

    # Create results directory
    folder_name = os.path.dirname(params['filepath_or_buffer'])

    # Missing values
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

    # Descriptive statistics
    df.describe().to_csv(os.path.join(folder_name, "statistics.csv"), sep=params['sep'], index=True)
    print("Compute descriptive statistics...\n")

    # Bar/box plot and/or histogram for each column
    for col in tqdm([col for col in df.columns if df[col].dtype != 'datetime64'], desc="Plotting box/bar plot of data columns..."):
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

    # Standardize data
    print("Standardize numeric data...", end="")
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = standardize_col(df[col])
    print("Done\n")
    
    # One hot encoding categorical variables
    print("One hot encoding...", end="")
    df_dummies = pd.get_dummies(df, columns=[col for col in df.columns if df[col].dtype in ['object', 'category']])
    print("Done\n")
    
    # Correlation
    print("Computing correlation...")
    corr = df_dummies.corr()
    corr.to_csv(os.path.join(folder_name, "correlations.csv"), sep=params['sep'], index=False)
    mask = 1 - np.tril(np.ones_like(corr))
    plt.figure(figsize=figsize)
    sns.heatmap(corr, mask=mask, vmin=-1, vmax=1, annot=True, cmap='coolwarm')
    plt.title("Correlation between variables\nCategorical variables are one-hot encoded")
    plt.savefig(os.path.join(folder_name, "correlations"))
    plt.close()

    # Save results
    new_csv_name = os.path.basename(params['filepath_or_buffer'])
    new_csv_name = new_csv_name[:new_csv_name.find('.csv')] + "_cleaned.csv"
    df_dummies.to_csv(os.path.join(folder_name, new_csv_name), sep=params['sep'], index=False)

    print("\nPrimary exploration of data is done.")
    
    zip_filename = "results"
    make_archive(zip_filename, 'zip', folder_name)
    return zip_filename


if __name__ == "__main__":

    # Sample csv for test
    csv_path = "https://raw.githubusercontent.com/ASNguyen8/ASNguyen8.github.io/master/docs/essence.csv"
    csv_sep = ";"
    col_dtypes = {'Prix': "float64", 'Volume': "float64", 'Prix_litre': "float64", 'TVA': "float64", 'Pays': "object"}
    parse_dates = ["Date"]