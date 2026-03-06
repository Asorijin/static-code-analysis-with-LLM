import pandas as pd
import math

df = pd.read_csv('fin.csv')
df_xlsx = pd.read_excel('./leak.xlsx', engine='openpyxl')

TP = 0.0
FP = 0.0
TN = 0.0
FN = 0.0
for i in range(0,len(df)):
    if ('"yes"' in (df['cavfd'][i])) and (df_xlsx['label'][i] == 1):
        TP += 1.0
    elif ('"yes"' in (df['cavfd'][i])) and (df_xlsx['label'][i] == 0):
        FP += 1.0
    elif ('"no"' in (df['cavfd'][i])) and (df_xlsx['label'][i] == 0):
        TN += 1.0
    else:
        FN += 1.0
print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
print(((TP*TN)-(FP*FN))/math.sqrt( (TP+FP)*(TP+FN)*(TN+FN)*(TN+FP) ) )




