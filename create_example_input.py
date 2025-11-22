#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建示例输入Excel文件

该脚本用于生成一个示例的输入Excel文件，包含董事长任职信息
"""

import pandas as pd

# 创建示例数据
data = {
    '个人ID': [30587115, 30587116, 30587117],
    '股票代码': ['688001', '000001', '600000'],
    '公司名称': ['华兴源创', '平安银行', '浦发银行'],
    '姓名': ['陈文源', '谢永林', '郑杨'],
    '职务': ['董事长', '董事长', '董事长'],
    '性别': ['男', '男', '男'],
    '出生日期': ['196811', '196401', '196512'],
    '学历': ['', '博士', '硕士'],
    '国籍': ['中国', '中国', '中国'],
    '起始年份': [2018, 2019, 2020],
    '终止年份': [2024, 2023, 2024],
    '任期区间': ['2018-2024', '2019-2023', '2020-2024']
}

df = pd.DataFrame(data)

# 保存为Excel文件
output_file = 'example_chairman_data.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"示例输入文件已创建: {output_file}")
print(f"\n数据内容:")
print(df.to_string(index=False))
