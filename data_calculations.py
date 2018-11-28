import pandas as pd
import numpy as np



def standard_deviation(df, data_column, n):  
    df = df.join(pd.Series(df[data_column].rolling(n).std(), name = str(n) + ' Period Std Dev'))
    return df  

def ratio(df, var, ma):
    label = str(var) + '/' + str(ma) + ' Ratio'
    df[label] = round((df[var] / df[ma]), 2)
    return df

def MA(df, variable, n):  
    MA = pd.Series(df[variable].rolling(n).mean(), name = str(variable) + ' ' + str(n) + ' MA')
    df = df.join(MA)  
    return df

def Median(df, variable, n):  
    med = pd.Series(df[variable].rolling(n).median(), name = 'Median')
    df = df.join(med)  
    return df

