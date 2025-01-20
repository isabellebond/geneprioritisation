import pandas as pd

def sep_cells(df, column, sep = '; '):
    """
    Separate cells in a dataframe column by a separator
    """
    df = df.copy()
    df.loc[:,column] = df[column].str.split(sep)
    df = df.explode(column)
    #drop na values
    df = df.dropna()
    
    return df