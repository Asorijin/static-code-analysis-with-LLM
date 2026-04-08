import pandas as pd
import math
from config import Config

df = pd.read_csv(Config.OUTPUT_CSV)

# 假设所有label=1（全为漏洞）
TP = FP = TN = FN = 0
for i in range(len(df)):
    cavfd = str(df['cavfd'][i])
    if '"yes"' in cavfd:
        TP += 1  # 正确识别漏洞
    elif '"no"' in cavfd:
        FN += 1  # 漏报（实际漏洞但判为非漏洞）
    elif 'likely' in cavfd:
        TP += 0.5  # 模糊结果算半条TP
        FN += 0.5
    # unknown 不计入

print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
mcc = ((TP*TN)-(FP*FN))/math.sqrt((TP+FP)*(TP+FN)*(TN+FN)*(TN+FP)) if (TP+FP)*(TP+FN)*(TN+FP)*(TN+FN) > 0 else 0
print(f"MCC: {mcc:.4f}")
