"""
学习分析计算模块 - Calculate_method.py
提供多种学习行为特征的量化计算方法

主要功能：
- LE (Learning Engagement): 学习参与度，基于完成时间的早晚
- LS (Learning Stability): 学习稳定性，基于时间间隔的熵值
- LAcc (Learning Acceleration): 学习加速度，基于差距的二阶差分
- RPI (Relative Procrastination Index): 相对拖延指数，基于与中位数的偏差
- 离线考试相关的LE/LS计算
"""

import pandas as pd
import numpy as np


def calculate_LE(cla, size1=38, size2=51, size3=61, cla_yuan=None):
    """
    计算学习参与度 (Learning Engagement)

    原理：LE = (max - x) / (max - min)
    - 完成时间越早，LE值越高
    - 分别计算视频(LE_video)、章节(LE_chapter)、作业(LE_homework)三类
    """
    df = cla.copy(deep=True)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 按列区间分割数据：视频(1~size1)、章节(size1~size2)、作业(size2~size3)
    values1 = df.iloc[:, 1:size1] if size1 > 1 else pd.DataFrame()
    values2 = df.iloc[:, size1:size2] if size2 > size1 else pd.DataFrame()
    values3 = df.iloc[:, size2:size3] if size3 > size2 else pd.DataFrame()

    def calc_le_for_range(values):
        if values.empty or values.shape[1] == 0:
            return pd.Series(0.0, index=df.index)

        max_values = values.max(axis=0)
        min_values = values[values > 0].min(axis=0).fillna(0)
        diff = max_values - min_values

        normalized = pd.DataFrame(index=values.index)
        for col in values.columns:
            if diff[col] > 0:
                normalized[col] = np.where(values[col] > 0,
                                          (max_values[col] - values[col]) / diff[col],
                                          0)
            else:
                normalized[col] = 0

        le = normalized.mean(axis=1)
        max_le = le.max()
        return le / max_le if max_le > 0 else le

    df['LE_video'] = calc_le_for_range(values1).values if not values1.empty else 0
    df['LE_chapter'] = calc_le_for_range(values2).values if not values2.empty else 0
    df['LE_homework'] = calc_le_for_range(values3).values if not values3.empty else 0

    # 计算综合LE
    active_count = sum([1 if not values1.empty and values1.shape[1] > 0 else 0,
                       1 if not values2.empty and values2.shape[1] > 0 else 0,
                       1 if not values3.empty and values3.shape[1] > 0 else 0])

    if active_count > 0:
        df['LE_all'] = (df['LE_video'] + df['LE_chapter'] + df['LE_homework']) / active_count
    else:
        df['LE_all'] = 0

    result_cols = ['SID', 'LE_video', 'LE_chapter', 'LE_homework', 'LE_all']

    # 可选择与原数据合并或直接返回
    if cla_yuan is not None:
        for col in ['LE_video', 'LE_chapter', 'LE_homework', 'LE_all']:
            if col in cla_yuan.columns:
                cla_yuan = cla_yuan.drop(columns=[col])
        return cla_yuan.merge(df[result_cols], on='SID', how='left')
    else:
        return cla.merge(df[result_cols], on='SID', how='left')


def calculate_LS(cla, size1=38, size2=51, size3=61, cla_yuan=None):
    """
    计算学习稳定性 (Learning Stability)

    原理：基于时间间隔的熵值
    - 时间间隔分布越均匀，熵值越高，稳定性越好
    - 间隔差异大（忽快忽慢），熵值低，稳定性差
    """
    df = cla.copy(deep=True)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    def calc_entropy(values):
        """计算信息熵"""
        if values.empty or values.shape[1] < 2:
            return pd.Series(0.0, index=values.index)

        result = []
        for idx in values.index:
            row = values.loc[idx].values.astype(float)
            row_sorted = np.sort(row)
            positive = row_sorted[row_sorted > 0]

            if len(positive) < 2:
                result.append(0.0)
                continue

            # 计算相邻间隔
            diffs = np.diff(positive)
            diffs = diffs[diffs > 0]

            if len(diffs) == 0 or diffs.sum() == 0:
                result.append(0.0)
                continue

            # 计算概率分布和熵值
            probs = diffs / diffs.sum()
            entropy = -np.sum(probs * np.log(probs + 1e-10))
            result.append(entropy)

        series = pd.Series(result, index=values.index)
        max_val = series.max()
        return series / max_val if max_val > 0 else series

    values1 = df.iloc[:, 1:size1] if size1 > 1 else pd.DataFrame()
    values2 = df.iloc[:, size1:size2] if size2 > size1 else pd.DataFrame()
    values3 = df.iloc[:, size2:size3] if size3 > size2 else pd.DataFrame()

    df['LS_video'] = calc_entropy(values1).values if not values1.empty and values1.shape[1] >= 2 else 0
    df['LS_chapter'] = calc_entropy(values2).values if not values2.empty and values2.shape[1] >= 2 else 0
    df['LS_homework'] = calc_entropy(values3).values if not values3.empty and values3.shape[1] >= 2 else 0

    active_count = sum([1 if not values1.empty and values1.shape[1] >= 2 else 0,
                       1 if not values2.empty and values2.shape[1] >= 2 else 0,
                       1 if not values3.empty and values3.shape[1] >= 2 else 0])

    if active_count > 0:
        df['LS_all'] = (df['LS_video'] + df['LS_chapter'] + df['LS_homework']) / active_count
    else:
        df['LS_all'] = 0

    result_cols = ['SID', 'LS_video', 'LS_chapter', 'LS_homework', 'LS_all']

    if cla_yuan is not None:
        for col in ['LS_video', 'LS_chapter', 'LS_homework', 'LS_all']:
            if col in cla_yuan.columns:
                cla_yuan = cla_yuan.drop(columns=[col])
        return cla_yuan.merge(df[result_cols], on='SID', how='left')
    else:
        return cla.merge(df[result_cols], on='SID', how='left')


def calculate_LAcc_RPI(cla, size1=38, size2=51, size3=61, cla_yuan=None):
    """
    计算学习加速度(LAcc)和相对拖延指数(RPI)

    LAcc原理：
    - 基于与最快者差距的二阶差分
    - 反映学习速度的变化趋势

    RPI原理：
    - 基于与中位数偏差的累积
    - 反映学习节奏是超前还是落后于平均水平
    """
    df = cla.copy(deep=True)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    names = ['video', 'chapter', 'homework']
    ranges = [(1, size1), (size1, size2), (size2, size3)]

    for name in names:
        df[f'LAcc_{name}'] = 0.0
        df[f'RPI_{name}'] = 0.0

    for (start, end), name in zip(ranges, names):
        if end <= start:
            continue

        sub_df = df.iloc[:, start:end].copy()
        if sub_df.shape[1] < 1:
            continue

        # 处理0值：用最大值*1.1替代（表示未完成状态）
        for col in sub_df.columns:
            max_val = sub_df[col].max()
            if max_val > 0:
                sub_df.loc[sub_df[col] == 0, col] = max_val * 1.1

        # LAcc: 二阶差分计算加速度
        if sub_df.shape[1] >= 3:
            min_vals = sub_df.min(axis=0)
            gap = sub_df.subtract(min_vals, axis=1)
            velocity = gap.diff(axis=1).fillna(0)
            acceleration = velocity.diff(axis=1).fillna(0)
            raw_lacc = acceleration.mean(axis=1)

            min_lacc, max_lacc = raw_lacc.min(), raw_lacc.max()
            if max_lacc != min_lacc:
                df[f'LAcc_{name}'] = ((raw_lacc - min_lacc) / (max_lacc - min_lacc)).values

        # RPI: 与中位数偏差
        medians = sub_df.median(axis=0)
        deviations = sub_df.subtract(medians, axis=1)
        raw_rpi = deviations.sum(axis=1)

        max_abs = abs(raw_rpi).max()
        if max_abs > 0:
            df[f'RPI_{name}'] = (raw_rpi / max_abs).values

    # 计算综合指标
    active_count = sum([1 if size1 > 1 else 0,
                       1 if size2 > size1 else 0,
                       1 if size3 > size2 else 0])

    if active_count > 0:
        df['LAcc_all'] = (df['LAcc_video'] + df['LAcc_chapter'] + df['LAcc_homework']) / active_count
        df['RPI_all'] = (df['RPI_video'] + df['RPI_chapter'] + df['RPI_homework']) / active_count
    else:
        df['LAcc_all'] = 0
        df['RPI_all'] = 0

    # 处理异常值
    result_cols = ['SID'] + [f'LAcc_{n}' for n in names] + ['LAcc_all'] + [f'RPI_{n}' for n in names] + ['RPI_all']

    for col in result_cols:
        if col != 'SID' and col in df.columns:
            df[col] = df[col].replace([np.inf, -np.inf], 0).fillna(0)

    if cla_yuan is not None:
        cols_to_drop = [c for c in result_cols if c != 'SID' and c in cla_yuan.columns]
        if cols_to_drop:
            cla_yuan = cla_yuan.drop(columns=cols_to_drop)
        return cla_yuan.merge(df[result_cols], on='SID', how='left')
    else:
        return cla.merge(df[result_cols], on='SID', how='left')


def calculate_LE_offline(cla, size1=4, cla_yuan=None):
    """计算离线考试的学习参与度（保留兼容性）"""
    df = cla.copy(deep=True)

    for col in df.columns[1:size1]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    values1 = df.iloc[:, 1:size1]
    if values1.empty:
        if cla_yuan is not None:
            cla_yuan['LE_score_off'] = 0
            return cla_yuan
        return cla

    max_values = values1.max(axis=0)
    min_values = values1[values1 > 0].min(axis=0).fillna(0)
    diff = max_values - min_values

    normalized = pd.DataFrame(index=df.index)
    for col in values1.columns:
        if diff[col] > 0:
            normalized[col] = np.where(values1[col] > 0,
                                      (max_values[col] - values1[col]) / diff[col],
                                      0)
        else:
            normalized[col] = 0

    le = normalized.mean(axis=1)
    max_le = le.max()
    df['LE_score_off'] = le / max_le if max_le > 0 else 0

    if cla_yuan is not None:
        if 'LE_score_off' in cla_yuan.columns:
            cla_yuan = cla_yuan.drop(columns=['LE_score_off'])
        return cla_yuan.merge(df[['SID', 'LE_score_off']], on='SID', how='left')
    return cla


def calculate_LS_offline(cla, size1=4, cla_yuan=None):
    """计算离线考试的学习稳定性（保留兼容性）"""
    df = cla.copy(deep=True)

    for col in df.columns[1:size1]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    values1 = df.iloc[:, 1:size1]
    if values1.empty or values1.shape[1] < 2:
        if cla_yuan is not None:
            cla_yuan['LS_score_off'] = 0
            return cla_yuan
        return cla

    result = []
    for idx in values1.index:
        row = values1.loc[idx].values.astype(float)
        row_sorted = np.sort(row)
        positive = row_sorted[row_sorted > 0]

        if len(positive) < 2:
            result.append(0.0)
            continue

        diffs = np.diff(positive)
        diffs = diffs[diffs > 0]

        if len(diffs) == 0 or diffs.sum() == 0:
            result.append(0.0)
            continue

        probs = diffs / diffs.sum()
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        result.append(entropy)

    series = pd.Series(result, index=values1.index)
    max_val = series.max()
    df['LS_score_off'] = series / max_val if max_val > 0 else 0

    if cla_yuan is not None:
        if 'LS_score_off' in cla_yuan.columns:
            cla_yuan = cla_yuan.drop(columns=['LS_score_off'])
        return cla_yuan.merge(df[['SID', 'LS_score_off']], on='SID', how='left')
    return cla


def Get_Fixed_Spearman_one_cohort(cla):
    """计算Spearman加权特征（保留兼容性）"""
    return cla


def Get_Fixed_Person_one_cohort(cla):
    """计算Pearson加权特征（保留兼容性）"""
    return cla