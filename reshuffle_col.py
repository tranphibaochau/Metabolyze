import pandas as pd

def reshuffle_col(input_file):
    df = pd.read_table(input_file, sep="\t", index_col=0)
    df = df.reset_index(drop=True)
    metadata = df.columns[0:18]
    df1 = df[metadata]
    columns = [col for col in df.columns if col.startswith('S') and ("SRM" not in col) and ("ISTD" not in col)]
    print(columns)
    df2 = df.reindex(sorted([col for col in columns]), axis=1)
    df = pd.concat([df1, df2], axis=1)
    blanks = [col for col in df.columns if "Blank" in col]
    df[blanks] = 0
    df.to_csv("C:\\Users\\cpt289\\Downloads\\merged_skeletons_pre_flux.quantified", sep="\t", index=False)
reshuffle_col("C:\\Users\\cpt289\\Downloads\\merged_skeletons.quantified")