#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试工作流的数据展开功能（不进行实际爬取）

该脚本用于测试workflow.py中的数据读取和展开逻辑，不执行实际的微博爬取
"""

import pandas as pd
from workflow import WeiboWorkflow

def test_data_expansion():
    """测试数据展开功能"""
    print("="*60)
    print("测试董事长微博数据采集工作流程 - 数据展开功能")
    print("="*60)
    
    # 创建工作流实例（不会实际运行爬虫）
    workflow = WeiboWorkflow(
        input_file='example_chairman_data.xlsx',
        output_file='test_output.xlsx',
        max_posts=5
    )
    
    # 1. 读取Excel
    print("\n1. 读取Excel文件...")
    df = workflow.read_excel()
    print(f"   读取到 {len(df)} 条记录")
    print("\n   数据预览:")
    print(df.to_string(index=False))
    
    # 2. 展开为公司-年度组合
    print("\n2. 展开为公司-年度组合...")
    expanded_records = workflow.expand_to_company_years(df)
    print(f"   展开得到 {len(expanded_records)} 个公司-年度组合")
    
    # 3. 显示展开结果
    print("\n3. 展开结果详情:")
    print("-" * 60)
    for i, record in enumerate(expanded_records, 1):
        print(f"   记录 {i}:")
        print(f"      公司: {record['company_name']}")
        print(f"      董事长: {record['chairman_name']}")
        print(f"      年份: {record['year']}")
        print(f"      关键词: {record['keyword']}")
        print()
    
    # 4. 统计信息
    print("\n4. 统计信息:")
    companies = set(r['company_name'] for r in expanded_records)
    years = set(r['year'] for r in expanded_records)
    print(f"   涉及公司数量: {len(companies)}")
    print(f"   涉及年份: {sorted(years)}")
    print(f"   总计需要爬取的关键词-年份组合数: {len(expanded_records)}")
    
    print("\n" + "="*60)
    print("数据展开测试完成！")
    print("="*60)
    
    print("\n提示:")
    print("  - 上述展开结果显示了将要爬取的所有关键词-年份组合")
    print("  - 实际运行workflow.py时，将对每个组合调用微博爬虫")
    print("  - 请确保已配置有效的微博Cookie后再运行实际爬取")

if __name__ == '__main__':
    try:
        test_data_expansion()
    except FileNotFoundError:
        print("错误: 找不到 example_chairman_data.xlsx 文件")
        print("请先运行: python create_example_input.py")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
