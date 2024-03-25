import pandas as pd
import numpy as np
from collections import defaultdict


def get_group_names(group_ids, original_name=True):
    groups = pd.read_table(group_ids, sep="\t")
    group_dict = defaultdict(list)
    unique_groups = [x for x in groups.Group.unique() if x !="Blank"]
    if original_name:
        for n in unique_groups:
            original_column_names = groups.loc[groups.Group == n].File.values.tolist()
            group_dict[n] = original_column_names
    else:
        for n in unique_groups:
            ids = groups.loc[groups.Group == n].id.values.tolist()
            group_dict[n] = ids
    return group_dict

