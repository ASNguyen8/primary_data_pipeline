# primary_data_pipeline

The purpose of this Python pipeline is to provide a quick an shallow way to explore data from an existing .csv file. Throughout basic plots of data per column, one can perform univariate analysis, notice the proportion of missing values or compute basic statistics (mean, standart deviation, min, max, etc.).
Also, it's thought to return plots, statistics and a "cleaned" csv file (standardized, one-hot encoded and without missing values) in a newly created folder.

This pipeline is meant to be as general as possible. Hence, csv separator, data dtypes or any specification for data will not be taken into consideration. For columns that only contain string values, the pipeline doesn't adapt the size of the y-axis labels of barplots according to the size of the longest string in column. Default size of the plot is (12, 8).

Further improvement will be added in the future, such as :
 - automatize the detection of csv separator;
 - (if possible without paying) deploy the application to a web server;