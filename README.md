# 学习行为特征分析系统

一套用于分析和量化学生学习行为特征的Python工具，基于MOOC平台和线下考试成绩数据，计算多种学习指标。

## 功能特性

本项目提供以下核心分析功能：

### 学习参与度 (Learning Engagement, LE)
- **原理**：`LE = (max - x) / (max - min)`
- **含义**：完成时间越早，LE值越高
- **分类**：视频完成度(LE_video)、章节完成度(LE_chapter)、作业完成度(LE_homework)

### 学习稳定性 (Learning Stability, LS)
- **原理**：基于时间间隔分布的信息熵
- **含义**：学习节奏越均匀稳定，熵值越高
- **分类**：视频稳定性(LS_video)、章节稳定性(LS_chapter)、作业稳定性(LS_homework)

### 学习加速度 (Learning Acceleration, LAcc)
- **原理**：基于与最快者差距的二阶差分
- **含义**：反映学习速度的变化趋势

### 相对拖延指数 (Relative Procrastination Index, RPI)
- **原理**：基于与中位数偏差的累积
- **含义**：反映学习节奏是超前还是落后于平均水平

### 相关性加权特征
- 基于Spearman和Pearson相关系数计算加权组合特征
- 可选是否包含线下考试成绩

## 文件结构

```
├── Data_handler.py           # 数据处理入口，按年份批量处理MOOC数据
├── Normal_data_conducted.py  # 数据预处理核心，读取和清洗MOOC/线下数据
├── Calculate_method.py       # 核心计算方法，定义LE/LS/LAcc/RPI等计算函数
├── data_compute.py           # 数据计算主程序，按阶段切分并计算特征
└── README.md                 # 本文件
```

## 依赖环境

- Python 3.8+
- pandas
- numpy
- scipy

安装依赖：
```bash
pip install pandas numpy scipy
```

## 快速开始

### 1. 数据准备

确保数据文件符合以下格式要求：

**输入数据格式（CSV）**：
| SID | 完成时间 | 完成时间.1 | ... | 提交时间 | 作业成绩 | MOOCgrade | offlinegrade |
|-----|----------|------------|-----|----------|----------|-----------|--------------|

- `SID`：学生唯一标识
- `完成时间`系列：任务点的完成时间戳
- `提交时间`系列：作业提交时间戳
- `作业成绩`系列：作业得分
- `MOOCgrade`：MOOC综合成绩
- `offlinegrade`：线下考试成绩

### 2. 基本使用

```python
from Calculate_method import calculate_LE, calculate_LS, calculate_LAcc_RPI
import pandas as pd

# 读取数据
df = pd.read_csv('your_data.csv')

# 计算学习参与度
df = calculate_LE(df, size1=38, size2=51, size3=61)

# 计算学习稳定性
df = calculate_LS(df, size1=38, size2=51, size3=61)

# 计算学习加速度和拖延指数
df = calculate_LAcc_RPI(df, size1=38, size2=51, size3=61)
```

### 3. 批量阶段计算

```python
from data_compute import StageCalculator
import pandas as pd

# 读取数据
df = pd.read_csv('Source_Data.csv')

# 初始化计算器
calc = StageCalculator(df)

# 处理所有阶段
summaries = calc.process_stages('output_directory')

# 保存汇总
import pandas as pd
final_summary = pd.concat(summaries, ignore_index=True)
final_summary.to_csv('All_Stages_Summary.csv', index=False)
```

## 计算参数说明

### calculate_LE / calculate_LS / calculate_LAcc_RPI

| 参数 | 类型 | 说明 |
|------|------|------|
| cla | DataFrame | 输入数据 |
| size1 | int | 视频任务点数量（默认38） |
| size2 | int | 章节任务点累计（默认51） |
| size3 | int | 作业任务点累计（默认61） |
| cla_yuan | DataFrame | 可选，原始数据用于合并 |

### 综合成绩计算

```
grade = MOOCgrade * 0.4 + offlinegrade
grade_label = (grade排名 >= 50%) ? 1 : 0
```

## 输出特征说明

| 特征名 | 说明 | 取值范围 |
|--------|------|----------|
| LE_video | 视频学习参与度 | [0, 1] |
| LE_chapter | 章节学习参与度 | [0, 1] |
| LE_homework | 作业学习参与度 | [0, 1] |
| LE_all | 综合学习参与度 | [0, 1] |
| LS_video | 视频学习稳定性 | [0, 1] |
| LS_chapter | 章节学习稳定性 | [0, 1] |
| LS_homework | 作业学习稳定性 | [0, 1] |
| LS_all | 综合学习稳定性 | [0, 1] |
| LAcc_all | 综合学习加速度 | [0, 1] |
| RPI_all | 综合相对拖延指数 | [-1, 1] |

## 应用场景

- **学业预警**：通过学习行为特征识别潜在学业困难学生
- **教学分析**：分析不同阶段学生的学习行为模式
- **成绩预测**：基于早期学习行为预测最终成绩
- **个性化干预**：针对不同学习特征提供差异化指导

## 注意事项

1. 数据隐私：请确保处理的数据已获得合法授权
2. 数据质量：输入数据中0值会被视为"未完成"状态
3. 参数调整：根据实际数据结构调整size1/size2/size3参数

## 软件著作权

本仓库对应软件著作权申请 **《教育数据提取与处理平台 1.0》**，用于学习行为特征的提取、清洗与阶段化计算。申请材料与源代码归档另存于私有备份，不在本仓库公开。

## 关联仓库

| 仓库 | 关系 |
|---|---|
| [`used-datasets`](https://github.com/lyh112358/used-datasets) | 已脱敏的建模表（`ml-early-warning/private`） |
| [`ksem2026-kinematic-risk-ensemble`](https://github.com/lyh112358/ksem2026-kinematic-risk-ensemble) | 使用本平台特征的下游论文实现 |

## 许可证

MIT License

## 贡献指南

欢迎提交Issue和Pull Request！