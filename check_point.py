import pandas as pd
import math

# 读取 testcode.xlsx（包含 label 真实标签和 cavfd 模型推理结果）
df = pd.read_excel("testcode.xlsx")

TP = FP = TN = FN = 0
for i in range(len(df)):
    label = int(df['label'][i])
    cavfd = str(df['cavfd'][i])

    pred_yes = '"yes"' in cavfd or 'yes' in cavfd.lower()
    pred_no = '"no"' in cavfd or 'no' in cavfd.lower()

    if label == 1:  # 实际为漏洞
        if pred_yes:
            TP += 1
        elif pred_no:
            FN += 1
    else:  # 实际为安全
        if pred_yes:
            FP += 1
        elif pred_no:
            TN += 1

print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")

precision = TP / (TP + FP) if (TP + FP) > 0 else 0
recall = TP / (TP + FN) if (TP + FN) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
mcc = ((TP*TN)-(FP*FN))/math.sqrt((TP+FP)*(TP+FN)*(TN+FN)*(TN+FP)) if (TP+FP)*(TP+FN)*(TN+FP)*(TN+FN) > 0 else 0

print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"MCC: {mcc:.4f}")

# ============================================================
# 原有逻辑（读取 fin.csv + leak.xlsx）
# ============================================================
# import pandas as pd
# import math
# from config import Config
#
# df = pd.read_csv(Config.OUTPUT_CSV)
#
# # 假设所有label=1（全为漏洞）
# TP = FP = TN = FN = 0
# for i in range(len(df)):
#     cavfd = str(df['cavfd'][i])
#     if '"yes"' in cavfd:
#         TP += 1  # 正确识别漏洞
#     elif '"no"' in cavfd:
#         FN += 1  # 漏报（实际漏洞但判为非漏洞）
#     elif 'likely' in cavfd:
#         TP += 0.5  # 模糊结果算半条TP
#         FN += 0.5
#     # unknown 不计入
#
# print(f"TP: {TP}, FP: {FP}, TN: {TN}, FN: {FN}")
# mcc = ((TP*TN)-(FP*FN))/math.sqrt((TP+FP)*(TP+FN)*(TN+FN)*(TN+FP)) if (TP+FP)*(TP+FN)*(TN+FP)*(TN+FN) > 0 else 0
# print(f"MCC: {mcc:.4f}")
