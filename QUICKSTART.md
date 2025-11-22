# 董事长微博数据采集工作流 - 快速开始

## 概述

本工作流实现了基于Excel文件中的董事长任职信息，自动批量爬取微博数据的完整解决方案。

## 使用场景

您有一个包含多家公司董事长任职信息的Excel表格，想要：
- 按年份（2019-2023）爬取每个公司董事长相关的微博
- 关键词格式：公司名称 + 董事长姓名
- 每个公司-年度保留前5条微博
- 将结果与原始数据合并输出

## 快速开始（5步）

### 第1步：准备环境

```bash
# 克隆项目（如果还没有）
git clone https://github.com/dhqdbb/weibo-search.git
cd weibo-search

# 安装依赖
pip install -r requirements.txt
```

### 第2步：配置Cookie

**重要：必须配置有效的微博Cookie才能爬取数据**

1. 打开浏览器，访问 https://weibo.com/ 并登录
2. 按F12打开开发者工具
3. 在Network标签中找到任意请求的Headers
4. 复制Cookie值
5. 编辑 `weibo/settings.py` 文件，在第15行附近找到：

```python
'cookie': 'your_cookie_here',
```

将 `your_cookie_here` 替换为你复制的Cookie值。

### 第3步：准备输入Excel文件

您的Excel文件应包含以下列（列名必须完全匹配）：

| 列名 | 必需 | 说明 |
|------|------|------|
| 个人ID | 否 | 董事长个人唯一标识 |
| 股票代码 | 否 | 公司股票代码 |
| 公司名称 | **是** | 公司名称 |
| 姓名 | **是** | 董事长姓名 |
| 起始年份 | **是** | 任期起始年份（如2018） |
| 终止年份 | **是** | 任期终止年份（如2024） |
| 其他列 | 否 | 保留所有其他列 |

**示例：**

如果没有现成的Excel文件，可以运行以下命令生成示例文件：

```bash
python create_example_input.py
```

这会生成 `example_chairman_data.xlsx`。

### 第4步：测试数据展开（可选但推荐）

在实际爬取前，先测试数据展开逻辑：

```bash
python test_workflow.py
```

这会显示将要爬取的所有关键词-年份组合，但不会实际访问微博。

### 第5步：运行工作流

```bash
python workflow.py --input 你的输入文件.xlsx --output 输出文件.xlsx
```

示例：

```bash
# 使用示例数据
python workflow.py --input example_chairman_data.xlsx --output result.xlsx

# 使用自己的数据
python workflow.py --input chairman_data.xlsx --output result.csv

# 只保留每个公司-年度的前3条微博
python workflow.py --input chairman_data.xlsx --output result.xlsx --max-posts 3

# 只查询2020-2022年
python workflow.py --input chairman_data.xlsx --output result.xlsx --years 2020 2021 2022
```

## 输出说明

输出文件包含：
1. 原始Excel的所有列
2. 新增列：
   - **查询年份**：当前记录对应的年份
   - **关键词**：使用的搜索关键词
   - **微博数量**：实际获取到的微博数量
   - **微博1_内容** 至 **微博5_内容**
   - **微博1_发布时间** 至 **微博5_发布时间**
   - **微博1_转发数** 至 **微博5_转发数**
   - **微博1_评论数** 至 **微博5_评论数**
   - **微博1_点赞数** 至 **微博5_点赞数**

每个公司-年度组合对应输出文件中的一行。

## 执行时间估算

- 每个关键词-年份组合大约需要：15-30秒（取决于结果数量和网络速度）
- 例如：3家公司 × 5年 = 15个组合，预计耗时：5-10分钟

## 注意事项

1. **Cookie有效性**：Cookie可能过期，如果爬取失败请重新获取
2. **访问频率**：程序在请求间有延迟，避免被封禁
3. **数据完整性**：如果某年没有微博，仍会保留记录但微博字段为空
4. **中断恢复**：当前版本不支持断点续传，中断后需重新运行

## 常见问题

**Q: 提示"cookie无效或已过期"怎么办？**  
A: 重新获取Cookie并更新到 `weibo/settings.py`。

**Q: 某些公司-年度没有获取到微博？**  
A: 正常现象，可能确实没有相关微博，或微博已被删除。

**Q: 如何只查询特定年份？**  
A: 使用 `--years` 参数，如：`--years 2020 2022`

**Q: 可以修改关键词格式吗？**  
A: 可以，编辑 `workflow.py` 的第73行，修改 `keyword` 的生成逻辑。

## 完整文档

详细文档请参考：[WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)

## 示例输出

原始输入（3条记录）：

```
个人ID    | 公司名称 | 姓名   | 起始年份 | 终止年份
30587115  | 华兴源创 | 陈文源 | 2018     | 2024
30587116  | 平安银行 | 谢永林 | 2019     | 2023
```

展开后（14个公司-年度组合）：

```
华兴源创 陈文源 2019
华兴源创 陈文源 2020
华兴源创 陈文源 2021
华兴源创 陈文源 2022
华兴源创 陈文源 2023
平安银行 谢永林 2019
平安银行 谢永林 2020
...
```

最终输出（14行，包含原始列+微博数据列）。

## 技术支持

如有问题，请在GitHub上提issue：
https://github.com/dhqdbb/weibo-search/issues

---

**祝您使用愉快！**
