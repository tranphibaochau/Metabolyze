import pandas as pd
import sys
import os


def read_table_as_dataframe(input_file):
    try:
        df = pd.read_table(input_file, sep="\t")
        if len(df.columns) == 1 and len(df.columns[0].split(",")) > 1:
            df = pd.read_table(input_file, sep=",")
    except FileNotFoundError:
        print("File not found.")
    except pd.errors.EmptyDataError:
        print("Empty file.")
    except Exception as e:
        print("Error occurred:", e)
    return df


def calculate_impact_score(input_file):

    df = read_table_as_dataframe(input_file)
    if any("Log2FoldChange" in x for x in df.columns):
        pass
    else:
        raise ValueError("Log2FoldChange not found in input file: {}".format(input_file))
    if any("_combined_mean" in x for x in df.columns):
        pass
    else:
        raise ValueError("mean not found in input file: {}".format(input_file))
    if any("_ttest_pval" in x for x in df.columns):
        pass
    else:
        raise ValueError("mean not found in input file: {}".format(input_file))

    cols = [x for x in df.columns if x.endswith("Log2FoldChange")]
    for c in cols:
        group_comparison = "".join(c.split("Log2FoldChange")[0])
        col_impact_score = group_comparison + "impact_score"

        df[col_impact_score] = (2**abs(df[c]))*df[group_comparison+"combined_mean"]/(df[group_comparison+"ttest_pval"]) / 1000000

        df.fillna({col_impact_score: "NA"}, inplace=True)  # replace NaN values with NA for readability

    df.to_csv(f"{os.getcwd()}/output/impact_score/impact_score.quantified", sep="\t", index=False)
    return


input_file = sys.argv[1]
calculate_impact_score(input_file)
