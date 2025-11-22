#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
董事长微博数据采集工作流程

该脚本基于输入的Excel文件（包含董事长任职信息），自动：
1. 读取Excel数据
2. 展开为公司-年度组合（2019-2023）
3. 为每个组合构造关键词："公司名称 董事长姓名"
4. 调用现有微博爬虫获取该年度的微博数据（最多5条）
5. 将结果与原始数据合并，输出为Excel/CSV

使用方法:
    python workflow.py --input input.xlsx --output output.xlsx
"""

import argparse
import os
import sys
import pandas as pd
import subprocess
import json
import time
import shutil
from datetime import datetime
from pathlib import Path


class WeiboWorkflow:
    """微博爬虫工作流程管理类"""
    
    def __init__(self, input_file, output_file, max_posts=5, target_years=None):
        """
        初始化工作流
        
        Args:
            input_file: 输入的Excel文件路径
            output_file: 输出的Excel/CSV文件路径
            max_posts: 每个公司-年度组合最多保留的微博数量（默认5条）
            target_years: 目标年份列表（默认2019-2023）
        """
        self.input_file = input_file
        self.output_file = output_file
        self.max_posts = max_posts
        self.target_years = target_years or list(range(2019, 2024))
        self.temp_dir = Path("temp_workflow")
        self.results = []
        
    def read_excel(self):
        """读取输入的Excel文件"""
        print(f"读取Excel文件: {self.input_file}")
        try:
            df = pd.read_excel(self.input_file)
            print(f"成功读取 {len(df)} 条记录")
            return df
        except Exception as e:
            print(f"读取Excel文件失败: {e}")
            sys.exit(1)
    
    def expand_to_company_years(self, df):
        """
        将原始数据展开为公司-年度组合
        
        Args:
            df: 原始DataFrame
            
        Returns:
            expanded_records: 展开后的记录列表，每个记录包含原始数据和对应年份
        """
        print("展开数据为公司-年度组合...")
        expanded_records = []
        
        for idx, row in df.iterrows():
            try:
                # 获取任期起始和终止年份
                start_year = int(row.get('起始年份', 0))
                end_year = int(row.get('终止年份', 9999))
                
                # 计算与目标年份的交集
                for year in self.target_years:
                    if start_year <= year <= end_year:
                        record = {
                            'original_data': row.to_dict(),
                            'year': year,
                            'company_name': row.get('公司名称', ''),
                            'chairman_name': row.get('姓名', ''),
                            'keyword': f"{row.get('公司名称', '')} {row.get('姓名', '')}"
                        }
                        expanded_records.append(record)
                        
            except (ValueError, TypeError) as e:
                print(f"警告: 第 {idx+1} 行数据解析失败: {e}")
                continue
        
        print(f"展开得到 {len(expanded_records)} 个公司-年度组合")
        return expanded_records
    
    def crawl_weibo(self, keyword, year):
        """
        调用Scrapy爬虫获取指定关键词和年份的微博数据
        
        Args:
            keyword: 搜索关键词
            year: 目标年份
            
        Returns:
            weibo_list: 微博数据列表
        """
        print(f"正在爬取: {keyword} ({year}年)")
        
        try:
            # 构造scrapy命令，使用命令行参数覆盖settings
            cmd = [
                'scrapy', 'crawl', 'search',
                '-s', f'KEYWORD_LIST=["{keyword}"]',
                '-s', f'START_DATE={year}-01-01',
                '-s', f'END_DATE={year}-12-31',
                '-s', f'LIMIT_RESULT={self.max_posts}',
                '-s', 'WEIBO_TYPE=0',
                '-s', 'CONTAIN_TYPE=0',
                '-s', 'LOG_LEVEL=ERROR'
            ]
            
            # 执行爬虫
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 读取爬取结果
            csv_file = Path('结果文件') / keyword / f'{keyword}.csv'
            if csv_file.exists():
                weibo_df = pd.read_csv(csv_file, encoding='utf-8-sig')
                weibo_list = weibo_df.to_dict('records')
                
                # 只保留前max_posts条
                weibo_list = weibo_list[:self.max_posts]
                
                print(f"成功获取 {len(weibo_list)} 条微博")
                return weibo_list
            else:
                print(f"未找到结果文件，可能没有相关微博")
                return []
                
        except subprocess.TimeoutExpired:
            print(f"爬取超时: {keyword} ({year})")
            return []
        except Exception as e:
            print(f"爬取失败: {keyword} ({year}), 错误: {e}")
            return []
    
    def process_records(self, expanded_records):
        """
        处理所有展开的记录，依次爬取微博数据
        
        Args:
            expanded_records: 展开后的记录列表
        """
        print(f"\n开始处理 {len(expanded_records)} 个公司-年度组合...")
        
        for i, record in enumerate(expanded_records):
            print(f"\n进度: [{i+1}/{len(expanded_records)}]")
            
            keyword = record['keyword']
            year = record['year']
            
            # 爬取微博数据
            weibo_list = self.crawl_weibo(keyword, year)
            
            # 将微博数据添加到记录中
            record['weibo_posts'] = weibo_list
            self.results.append(record)
            
            # 添加延迟，避免请求过快
            if i < len(expanded_records) - 1:
                time.sleep(2)
    
    def format_output(self):
        """
        将结果格式化为最终输出的DataFrame
        
        Returns:
            output_df: 输出的DataFrame
        """
        print("\n格式化输出数据...")
        
        output_rows = []
        
        for record in self.results:
            original_data = record['original_data']
            year = record['year']
            weibo_posts = record['weibo_posts']
            
            # 如果没有微博数据，也保留一行
            if not weibo_posts:
                row = original_data.copy()
                row['查询年份'] = year
                row['关键词'] = record['keyword']
                row['微博数量'] = 0
                # 添加空的微博字段
                for j in range(1, self.max_posts + 1):
                    row[f'微博{j}_内容'] = ''
                    row[f'微博{j}_发布时间'] = ''
                    row[f'微博{j}_转发数'] = ''
                    row[f'微博{j}_评论数'] = ''
                    row[f'微博{j}_点赞数'] = ''
                output_rows.append(row)
            else:
                # 方案：每个公司-年度一行，微博内容展开为多列
                row = original_data.copy()
                row['查询年份'] = year
                row['关键词'] = record['keyword']
                row['微博数量'] = len(weibo_posts)
                
                for j, weibo in enumerate(weibo_posts[:self.max_posts], 1):
                    row[f'微博{j}_内容'] = weibo.get('微博正文', '')
                    row[f'微博{j}_发布时间'] = weibo.get('发布时间', '')
                    row[f'微博{j}_转发数'] = weibo.get('转发数', '')
                    row[f'微博{j}_评论数'] = weibo.get('评论数', '')
                    row[f'微博{j}_点赞数'] = weibo.get('点赞数', '')
                
                # 填充空的微博字段
                for j in range(len(weibo_posts) + 1, self.max_posts + 1):
                    row[f'微博{j}_内容'] = ''
                    row[f'微博{j}_发布时间'] = ''
                    row[f'微博{j}_转发数'] = ''
                    row[f'微博{j}_评论数'] = ''
                    row[f'微博{j}_点赞数'] = ''
                
                output_rows.append(row)
        
        output_df = pd.DataFrame(output_rows)
        print(f"输出数据包含 {len(output_df)} 行")
        return output_df
    
    def save_output(self, output_df):
        """
        保存输出文件
        
        Args:
            output_df: 输出的DataFrame
        """
        print(f"\n保存结果到: {self.output_file}")
        
        try:
            if self.output_file.endswith('.csv'):
                output_df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            else:
                output_df.to_excel(self.output_file, index=False, engine='openpyxl')
            print("保存成功！")
        except Exception as e:
            print(f"保存失败: {e}")
            sys.exit(1)
    
    def cleanup(self):
        """清理临时文件"""
        print("\n清理临时文件...")
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        # 可选：清理结果文件夹
        # results_dir = Path('结果文件')
        # if results_dir.exists():
        #     shutil.rmtree(results_dir, ignore_errors=True)
    
    def run(self):
        """执行完整的工作流程"""
        print("="*60)
        print("董事长微博数据采集工作流程")
        print("="*60)
        
        try:
            # 1. 读取Excel
            df = self.read_excel()
            
            # 2. 展开为公司-年度组合
            expanded_records = self.expand_to_company_years(df)
            
            if not expanded_records:
                print("没有找到符合条件的记录！")
                sys.exit(1)
            
            # 3. 处理每个记录，爬取微博数据
            self.process_records(expanded_records)
            
            # 4. 格式化输出
            output_df = self.format_output()
            
            # 5. 保存结果
            self.save_output(output_df)
            
            print("\n"+"="*60)
            print("工作流程完成！")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n\n用户中断执行")
            sys.exit(1)
        finally:
            # 6. 清理临时文件
            self.cleanup()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='董事长微博数据采集工作流程',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python workflow.py --input chairman_data.xlsx --output result.xlsx
    python workflow.py --input chairman_data.xlsx --output result.csv --max-posts 3
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入的Excel文件路径，包含董事长任职信息'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='输出的Excel或CSV文件路径'
    )
    
    parser.add_argument(
        '--max-posts', '-m',
        type=int,
        default=5,
        help='每个公司-年度组合最多保留的微博数量（默认5条）'
    )
    
    parser.add_argument(
        '--years', '-y',
        nargs='+',
        type=int,
        help='目标年份列表（默认2019-2023），如: --years 2020 2021 2022'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    # 创建工作流实例并运行
    workflow = WeiboWorkflow(
        input_file=args.input,
        output_file=args.output,
        max_posts=args.max_posts,
        target_years=args.years
    )
    
    workflow.run()


if __name__ == '__main__':
    main()
