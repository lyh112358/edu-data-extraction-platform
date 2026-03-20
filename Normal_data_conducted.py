"""
数据预处理模块 - Normal_data_conducted.py
负责从MOOC平台和线下考试系统读取、清洗、合并学生数据

主要功能：
1. 读取多年级MOOC数据（支持不同年份格式）
2. 处理线下考试成绩数据
3. 合并MOOC和线下数据
4. 生成各学习阶段的特征数据
"""

import glob
import math
import os
import time
import re
import pandas as pd
import numpy as np
from datetime import datetime
import Calculate_method


def is_valid_time_string(time_str):
    """检查时间字符串格式是否有效"""
    try:
        datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return True
    except ValueError:
        return False


def add_cumulative_homework_grade(df):
    """计算所有作业成绩列的总和，添加到新列'作业总成绩'"""
    grade_cols = [col for col in df.columns if '作业成绩' in str(col)]

    if grade_cols:
        df['作业总成绩'] = df[grade_cols].sum(axis=1)
    else:
        df['作业总成绩'] = 0

    return df


# ================= 阶段列名定义 =================
# 定义15个学习阶段对应的列名

names1 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 11)] + [f'完成时间.{i}' for i in range(37, 41)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 2)] + [f'作业成绩{i}' for i in range(1, 2)] + ['grade', 'grade_label']
names2 = ['SID'] + [f'完成时间.{i}' for i in range(11, 22)] + [f'完成时间.{i}' for i in range(41, 44)] + [f'提交时间.{i}' for i in range(2, 4)] + [f'作业成绩{i}' for i in range(2, 4)] + ['grade', 'grade_label']
names12 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 22)] + [f'完成时间.{i}' for i in range(37, 44)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 4)] + [f'作业成绩{i}' for i in range(1, 4)] + ['grade', 'grade_label']
names3 = ['SID'] + [f'完成时间.{i}' for i in range(22, 24)] + [f'完成时间.{i}' for i in range(44, 45)] + [f'提交时间.{i}' for i in range(4, 4)] + [f'作业成绩{i}' for i in range(4, 4)] + ['grade', 'grade_label']
names123 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 24)] + [f'完成时间.{i}' for i in range(37, 45)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 4)] + [f'作业成绩{i}' for i in range(1, 4)] + ['grade', 'grade_label']
names23 = ['SID'] + [f'完成时间.{i}' for i in range(10, 23)] + [f'完成时间.{i}' for i in range(41, 45)] + [f'提交时间.{i}' for i in range(2, 4)] + [f'作业成绩{i}' for i in range(2, 4)] + ['grade', 'grade_label']
names4 = ['SID'] + [f'完成时间.{i}' for i in range(24, 28)] + [f'完成时间.{i}' for i in range(45, 48)] + [f'提交时间.{i}' for i in range(4, 8)] + [f'作业成绩{i}' for i in range(4, 8)] + ['grade', 'grade_label']
names34 = ['SID'] + [f'完成时间.{i}' for i in range(22, 28)] + [f'完成时间.{i}' for i in range(44, 48)] + [f'提交时间.{i}' for i in range(4, 8)] + [f'作业成绩{i}' for i in range(4, 8)] + ['grade', 'grade_label']
names1234 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 28)] + [f'完成时间.{i}' for i in range(37, 48)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 8)] + [f'作业成绩{i}' for i in range(1, 8)] + ['grade', 'grade_label']
names5 = ['SID'] + [f'完成时间.{i}' for i in range(28, 37)] + [f'完成时间.{i}' for i in range(48, 50)] + [f'提交时间.{i}' for i in range(8, 10)] + [f'作业成绩{i}' for i in range(8, 10)] + ['grade', 'grade_label']
names45 = ['SID'] + [f'完成时间.{i}' for i in range(24, 37)] + [f'完成时间.{i}' for i in range(45, 50)] + [f'提交时间.{i}' for i in range(4, 10)] + [f'作业成绩{i}' for i in range(4, 10)] + ['grade', 'grade_label']
names12345 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 37)] + [f'完成时间.{i}' for i in range(37, 50)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 10)] + [f'作业成绩{i}' for i in range(1, 10)] + ['grade', 'grade_label']
names6 = ['SID'] + [f'完成时间.{i}' for i in range(37, 37)] + [f'完成时间.{i}' for i in range(50, 50)] + [f'提交时间.{i}' for i in range(10, 10)] + [f'作业成绩{i}' for i in range(10, 10)] + ['grade', 'grade_label']
names56 = ['SID'] + [f'完成时间.{i}' for i in range(28, 37)] + [f'完成时间.{i}' for i in range(48, 50)] + [f'提交时间.{i}' for i in range(8, 10)] + [f'作业成绩{i}' for i in range(8, 10)] + ['grade', 'grade_label']
names123456 = ['SID', '完成时间'] + [f'完成时间.{i}' for i in range(1, 37)] + [f'完成时间.{i}' for i in range(37, 50)] + ['提交时间'] + ['作业成绩'] + [f'提交时间.{i}' for i in range(1, 10)] + [f'作业成绩{i}' for i in range(1, 10)] + ['grade', 'grade_label']


def cond_jointdata_MOOC(folder_path):
    """
    读取MOOC数据（适用于2020/2021年格式）

    处理流程：
    1. 读取Excel文件的多个sheet
    2. 提取任务点完成时间、作业成绩等
    3. 合并各sheet数据
    4. 转换时间为时间戳
    """
    folder_path += 'MOOC/'
    keys = ["学生综合完成情况", "任务点完成详情", "音视频观看详情", "作业统计"]
    frames = []
    grades = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            try:
                cla = pd.read_excel(file_path, sheet_name=None)
                print(f"Processing file: {file_name}")
                for key in keys:
                    if key == "学生综合完成情况":
                        cla[key].drop(['学习情况'], axis=1, inplace=True)
                        cla[key]['视频观看时长'] = cla[key]['视频观看时长'].fillna('').astype(str).str[:-2].astype(float)
                        cla[key]['任务点完成百分比'] = cla[key]['任务点完成百分比'].fillna('').astype(str).str[:-1].astype(float) / 100
                        cla[key]['课程视频进度'] = cla[key]['课程视频进度'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 37
                        cla[key]['章节测验进度'] = cla[key]['章节测验进度'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 13
                        cla[key]['任务完成数'] = cla[key]['任务完成数'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 50

                    elif key == "任务点完成详情":
                        cla[key] = pd.read_excel(file_path, sheet_name="任务点完成详情", skiprows=2)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        columns = list(cla[key].columns)
                        for i in range(1, len(columns)):
                            if "完成时间" not in columns[i]:
                                cla[key].drop(columns[i], axis=1, inplace=True)
                            else:
                                cla[key][columns[i]] = pd.to_datetime(cla[key][columns[i]])

                    elif key == "音视频观看详情":
                        cla[key] = pd.read_excel(file_path, sheet_name="音视频观看详情", skiprows=2)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        cla[key].set_index('SID', inplace=True)
                        columns = list(cla[key].columns)
                        for i in range(len(columns)):
                            if "反刍比" in columns[i]:
                                cla[key][columns[i]] = cla[key][columns[i]].fillna('').astype(str).str[:-1].astype(float) / 100
                            elif "观看时长" in columns[i]:
                                cla[key][columns[i]] = cla[key][columns[i]].fillna('').astype(str).str[:-2].astype(float)
                        columns = list(cla[key].columns)
                        cla[key]['sum_ruminant'] = 0
                        cla[key]['sum_video'] = 0
                        for i in range(len(columns)):
                            if "反刍比" in columns[i]:
                                cla[key]['sum_ruminant'] += cla[key][columns[i]]
                            elif "观看时长" in columns[i]:
                                cla[key]['sum_video'] += cla[key][columns[i]]
                        cla[key]['mean_ruminant'] = cla[key]['sum_ruminant'] / 37
                        cla[key]['mean_video'] = cla[key]['sum_video'] / 37

                    elif key == '作业统计':
                        cla[key] = pd.read_excel(file_path, sheet_name="作业统计", skiprows=1)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        cla[key].set_index('SID', inplace=True)
                        columns = list(cla[key].columns)
                        homework_cols = [col for col in columns if any(keyword in str(col) for keyword in ["成绩", "状态", "提交时间"])]
                        cla[key] = cla[key][homework_cols]
                        max_suffix = 0
                        for col in cla[key].columns:
                            match = re.search(r'\.(\d+)$', str(col))
                            if match:
                                max_suffix = max(max_suffix, int(match.group(1)))
                        status_cols_to_drop = []
                        for i in range(max_suffix + 1):
                            suffix = f'.{i}' if i > 0 else ''
                            grade_col = f'成绩{suffix}'
                            status_col = f'状态{suffix}'
                            time_col = f'提交时间{suffix}'
                            if grade_col in cla[key].columns and status_col in cla[key].columns:
                                cla[key][grade_col].fillna(0.0, inplace=True)
                                cla[key].loc[cla[key][status_col] == '未完成', grade_col] = 0.0
                                new_grade_name = f'作业成绩' if i == 0 else f'作业成绩{i}'
                                cla[key].rename(columns={grade_col: new_grade_name}, inplace=True)
                                status_cols_to_drop.append(status_col)
                            if time_col in cla[key].columns:
                                cla[key][time_col] = pd.to_datetime(cla[key][time_col], errors='coerce')
                        cla[key].drop(columns=status_cols_to_drop, inplace=True)

                class_merge = cla[keys[0]]
                for j in range(1, len(keys)):
                    class_merge = pd.merge(class_merge, cla[keys[j]], on='SID', suffixes=(keys[j - 1], keys[j]))
                class_merge.dropna(axis=1, thresh=1, inplace=True)
                frames.append(class_merge)

                sheet = pd.read_excel(file_path, sheet_name=r'成绩详情')
                grade = pd.DataFrame()
                grade['SID'] = sheet['SID']
                grade['MOOCgrade'] = sheet['综合成绩']
                grade['章节测验grade'] = sheet['章节测验(10%)']
                grade['课程音视频grade'] = sheet['课程音视频(10%)']
                grade['作业grade'] = sheet['作业(60%)']
                grade['讨论grade'] = sheet['讨论(10%)']
                grade['课程互动grade'] = sheet['课程互动(10%)']
                new_order = ['SID', 'MOOCgrade', '课程音视频grade', '章节测验grade', '讨论grade', '作业grade', '课程互动grade']
                grade = grade.reindex(columns=new_order)
                grades.append(grade)

            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    res = pd.concat(frames)
    res.fillna(0, inplace=True)
    res.set_index('SID', inplace=True)
    columns = list(res.columns)
    suml = res.shape[0]
    for j in range(1, len(columns)):
        if "时间" in columns[j]:
            a = []
            for i in range(0, suml):
                time_value = str(res.iloc[i][columns[j]])
                if is_valid_time_string(time_value):
                    a.append(pd.to_datetime(time_value).timestamp())
                else:
                    a.append(0)
            res[columns[j]] = a
    grades = pd.concat(grades)
    grades.dropna(inplace=True)
    merged_res = res.merge(grades, on='SID', how='inner')
    return merged_res


def cond_jointdata_MOOC_22_23(folder_path):
    """
    读取MOOC数据（适用于2022/2023年格式）

    与cond_jointdata_MOOC类似，但sheet名称不同
    """
    folder_path += 'MOOC/'
    keys = ["学生学习进度详情", "任务点完成详情", "音视频观看详情", "作业统计"]
    frames = []
    grades = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file_name)
            try:
                cla = pd.read_excel(file_path, sheet_name=None)
                print(f"Processing file: {file_name}")
                for key in keys:
                    if key == "学生学习进度详情":
                        cla[key].drop(['学习情况'], axis=1, inplace=True)
                        cla[key]['视频观看时长'] = cla[key]['视频观看时长'].fillna('').astype(str).str[:-2].astype(float)
                        cla[key]['任务点完成百分比'] = cla[key]['任务点完成百分比'].fillna('').astype(str).str[:-1].astype(float) / 100
                        cla[key]['课程视频进度'] = cla[key]['课程视频进度'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 37
                        cla[key]['章节测验进度'] = cla[key]['章节测验进度'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 13
                        cla[key]['任务完成数'] = cla[key]['任务完成数'].fillna('').astype(str).str.split('/', expand=True)[0].astype(float) / 50
                    elif key == "任务点完成详情":
                        cla[key] = pd.read_excel(file_path, sheet_name=key, skiprows=2)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        columns = list(cla[key].columns)
                        for i in range(1, len(columns)):
                            if "完成时间" not in columns[i]:
                                cla[key].drop(columns[i], axis=1, inplace=True)
                            else:
                                cla[key][columns[i]] = pd.to_datetime(cla[key][columns[i]])
                    elif key == "音视频观看详情":
                        cla[key] = pd.read_excel(file_path, sheet_name=key, skiprows=2)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        cla[key].set_index('SID', inplace=True)
                        columns = list(cla[key].columns)
                        for i in range(len(columns)):
                            if "反刍比" in columns[i]:
                                cla[key][columns[i]] = cla[key][columns[i]].fillna('').astype(str).str[:-1].astype(float) / 100
                            elif "观看时长" in columns[i]:
                                cla[key][columns[i]] = cla[key][columns[i]].fillna('').astype(str).str[:-2].astype(float)
                        columns = list(cla[key].columns)
                        cla[key]['sum_ruminant'] = 0
                        cla[key]['sum_video'] = 0
                        for i in range(len(columns)):
                            if "反刍比" in columns[i]:
                                cla[key]['sum_ruminant'] += cla[key][columns[i]]
                            elif "观看时长" in columns[i]:
                                cla[key]['sum_video'] += cla[key][columns[i]]
                        cla[key]['mean_ruminant'] = cla[key]['sum_ruminant'] / 37
                        cla[key]['mean_video'] = cla[key]['sum_video'] / 37
                    elif key == '作业统计':
                        cla[key] = pd.read_excel(file_path, sheet_name="作业统计", skiprows=1)
                        cla[key].dropna(axis=1, thresh=1, inplace=True)
                        cla[key].rename(columns={'Unnamed: 0': 'SID'}, inplace=True)
                        cla[key].set_index('SID', inplace=True)
                        columns = list(cla[key].columns)
                        homework_cols = [col for col in columns if any(keyword in str(col) for keyword in ["成绩", "状态", "提交时间"])]
                        cla[key] = cla[key][homework_cols]
                        max_suffix = 0
                        for col in cla[key].columns:
                            match = re.search(r'\.(\d+)$', str(col))
                            if match:
                                max_suffix = max(max_suffix, int(match.group(1)))
                        status_cols_to_drop = []
                        for i in range(max_suffix + 1):
                            suffix = f'.{i}' if i > 0 else ''
                            grade_col = f'成绩{suffix}'
                            status_col = f'状态{suffix}'
                            time_col = f'提交时间{suffix}'
                            if grade_col in cla[key].columns and status_col in cla[key].columns:
                                cla[key][grade_col].fillna(0.0, inplace=True)
                                cla[key].loc[cla[key][status_col] == '未完成', grade_col] = 0.0
                                new_grade_name = f'作业成绩' if i == 0 else f'作业成绩{i}'
                                cla[key].rename(columns={grade_col: new_grade_name}, inplace=True)
                                status_cols_to_drop.append(status_col)
                            if time_col in cla[key].columns:
                                cla[key][time_col] = pd.to_datetime(cla[key][time_col], errors='coerce')
                        cla[key].drop(columns=status_cols_to_drop, inplace=True)

                class_merge = cla[keys[0]]
                for j in range(1, len(keys)):
                    class_merge = pd.merge(class_merge, cla[keys[j]], on='SID', suffixes=(keys[j - 1], keys[j]))
                class_merge.dropna(axis=1, thresh=1, inplace=True)
                frames.append(class_merge)

                sheet = pd.read_excel(file_path, sheet_name=r'综合成绩')
                grade = pd.DataFrame()
                grade['SID'] = sheet['SID']
                grade['MOOCgrade'] = sheet['综合成绩']
                grade['章节测验grade'] = sheet['章节测验(10%)']
                grade['课程音视频grade'] = sheet['课程音视频(10%)']
                grade['作业grade'] = sheet['作业(60%)']
                grade['讨论grade'] = sheet['讨论(10%)']
                grade['课程互动grade'] = sheet['课程互动(10%)']
                new_order = ['SID', 'MOOCgrade', '课程音视频grade', '章节测验grade', '讨论grade', '作业grade', '课程互动grade']
                grade = grade.reindex(columns=new_order)
                grades.append(grade)

            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    res = pd.concat(frames)
    res.fillna(0, inplace=True)
    res.set_index('SID', inplace=True)
    columns = list(res.columns)
    suml = res.shape[0]
    for j in range(1, len(columns)):
        if "时间" in columns[j]:
            a = []
            for i in range(0, suml):
                time_value = str(res.iloc[i][columns[j]])
                if is_valid_time_string(time_value):
                    a.append(pd.to_datetime(time_value).timestamp())
                else:
                    a.append(0)
            res[columns[j]] = a
    res = res.drop(columns=[col for col in res.columns if '开始时间' in col or '结束时间' in col or 'Unnamed' in col or col in ['学校', '院系', '专业', '班级']])
    grades = pd.concat(grades)
    grades.dropna(inplace=True)
    merged_res = res.merge(grades, on='SID', how='inner')
    return merged_res


def keep_only_new_features(df, keep_sid=True):
    """筛选保留新特征列"""
    df = df.loc[:, ~df.columns.duplicated(keep='last')]
    keep_cols = [
        c for c in df.columns
        if (keep_sid and c == "SID")
        or c.startswith("LE")
        or c.startswith("LS")
        or c.startswith("LAcc")
        or c.startswith("RPI")
        or "完成video.%" in c or "完成chapter.%" in c
        or "完成homework.%" in c or "完成all.%" in c
        or c == "grade_label"
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]
    return df[keep_cols]


def merge_stage_copy(copy_df: pd.DataFrame, feat_df: pd.DataFrame) -> pd.DataFrame:
    """合并阶段数据，避免重复列覆盖"""
    dup_cols = [c for c in feat_df.columns if c != 'SID' and c in copy_df.columns]
    left = copy_df.drop(columns=dup_cols, errors='ignore')
    out = left.merge(feat_df, on='SID', how='left')
    return out


def cond_all_LELS_forJieduanxing_v20(cla_mooc, folder_path, Save_path):
    """
    生成各阶段学习特征（Jieduan版本）

    这是核心函数，完成以下工作：
    1. 按时间节点切分数据（6个独立阶段 + 9个累计阶段）
    2. 计算每个阶段的LE、LS、LAcc、RPI等特征
    3. 保存各阶段特征到CSV文件
    """
    os.makedirs(Save_path, exist_ok=True)

    exam_cols_1_2 = ['SID', '考试学生总用时比例含罚时第1次周考', '考试学生总用时比例含罚时第2次周考']
    exam_cols_all = ['SID', '考试学生总用时比例含罚时第1次周考', '考试学生总用时比例含罚时第2次周考', '考试学生总用时比例含罚时第3次周考', '考试学生总用时比例含罚时第4次周考']
    exam_cols_1_2_exist = [c for c in exam_cols_1_2 if c in cla_mooc.columns]
    exam_cols_all_exist = [c for c in exam_cols_all if c in cla_mooc.columns]

    # 根据年份设置时间截点
    if '2020' in folder_path:
        date_str1, date_str2, date_str3, date_str4, date_str5 = '2020-10-15 23:59:59', '2020-10-31 23:59:59', '2020-11-15 23:59:59', '2020-11-30 23:59:59', '2020-12-15 23:59:59'
    elif '2021' in folder_path:
        date_str1, date_str2, date_str3, date_str4, date_str5 = '2021-10-15 23:59:59', '2021-10-31 23:59:59', '2021-11-15 23:59:59', '2021-11-30 23:59:59', '2021-12-15 23:59:59'
    elif '2022' in folder_path:
        date_str1, date_str2, date_str3, date_str4, date_str5 = '2022-10-15 23:59:59', '2022-10-31 23:59:59', '2022-11-15 23:59:59', '2022-11-30 23:59:59', '2022-12-15 23:59:59'
    elif '2023' in folder_path:
        date_str1, date_str2, date_str3, date_str4, date_str5 = '2023-10-15 23:59:59', '2023-10-31 23:59:59', '2023-11-15 23:59:59', '2023-11-30 23:59:59', '2023-12-15 23:59:59'

    timestamp1 = int(datetime.strptime(date_str1, '%Y-%m-%d %H:%M:%S').timestamp())
    timestamp2 = int(datetime.strptime(date_str2, '%Y-%m-%d %H:%M:%S').timestamp())
    timestamp3 = int(datetime.strptime(date_str3, '%Y-%m-%d %H:%M:%S').timestamp())
    timestamp4 = int(datetime.strptime(date_str4, '%Y-%m-%d %H:%M:%S').timestamp())
    timestamp5 = int(datetime.strptime(date_str5, '%Y-%m-%d %H:%M:%S').timestamp())

    def ends_from_names(names):
        """根据列名列表计算视频/章节/作业的边界索引"""
        def idx_last(pred):
            idx = [i for i, c in enumerate(names) if pred(c)]
            return (max(idx) + 1) if idx else 1

        v_end = idx_last(lambda c: c.startswith('完成时间') and (c == '完成时间' or (c.startswith('完成时间.') and c.split('.')[-1].isdigit() and int(c.split('.')[-1]) <= 36)))
        c_end = idx_last(lambda c: c.startswith('完成时间.') and c.split('.')[-1].isdigit() and 37 <= int(c.split('.')[-1]) <= 49)
        h_end = idx_last(lambda c: c.startswith('提交时间'))
        c_end = max(c_end, v_end)
        h_end = max(h_end, c_end)
        return v_end, c_end, h_end

    def add_completion_columns(df, cutoff_ts, strict_scope=True):
        """添加完成率列"""
        video_set = ['完成时间'] + [f'完成时间.{i}' for i in range(1, 37)]
        chapter_set = [f'完成时间.{i}' for i in range(37, 50)]
        homework_set = ['提交时间'] + [f'提交时间.{i}' for i in range(1, 100)]

        v_cols = [c for c in df.columns if c in video_set]
        c_cols = [c for c in df.columns if c in chapter_set] if strict_scope else chapter_set
        h_cols = [c for c in df.columns if c in homework_set]
        cols = v_cols + c_cols + h_cols
        if not cols:
            return df

        df.loc[:, cols] = df.loc[:, cols].apply(pd.to_numeric, errors='coerce')
        valid_for_rate = df.loc[:, cols].where((df.loc[:, cols] > 0) & (df.loc[:, cols] <= float(cutoff_ts)))

        v_cnt = valid_for_rate[v_cols].gt(0).sum(axis=1) if v_cols else 0
        c_cnt = valid_for_rate[c_cols].gt(0).sum(axis=1) if c_cols else 0
        h_cnt = valid_for_rate[h_cols].gt(0).sum(axis=1) if h_cols else 0

        df.loc[:, cols] = df.loc[:, cols].clip(upper=float(cutoff_ts))
        v_den, c_den, h_den = 37, 13, 10
        all_den = v_den + c_den + h_den

        df['完成video.%'] = v_cnt / v_den
        df['完成chapter.%'] = c_cnt / c_den
        df['完成homework.%'] = h_cnt / h_den
        df['完成all.%'] = (v_cnt + c_cnt + h_cnt) / all_den
        return df

    def process_dataframe_for_lels(df, timestamp_value=math.inf):
        """处理时间序列数据"""
        ts_cols = [c for c in df.columns if '时间' in c]
        if not ts_cols:
            return df
        out = df.copy()
        out.loc[:, ts_cols] = out.loc[:, ts_cols].apply(pd.to_numeric, errors='coerce')
        out.loc[:, ts_cols] = out.loc[:, ts_cols].where(out.loc[:, ts_cols] > 0, np.nan)
        out.loc[:, ts_cols] = out.loc[:, ts_cols].clip(upper=float(timestamp_value))
        return out

    # 预计算离线LE/LS
    offline_candidates = [
        '考试学生总用时含罚时第1次周考', '考试学生总用时含罚时第2次周考',
        '考试学生总用时含罚时第3次周考', '考试学生总用时含罚时第4次周考',
        '考试学生总用时含罚时'
    ]
    off_cols = [c for c in offline_candidates if c in cla_mooc.columns]
    if len(off_cols) >= 1:
        cla_off_ts = cla_mooc[['SID'] + off_cols].copy()
        cla_mooc = Calculate_method.calculate_LE_offline(cla_off_ts, len(cla_off_ts.columns), cla_mooc)
        cla_mooc = Calculate_method.calculate_LS_offline(cla_off_ts, len(cla_off_ts.columns), cla_mooc)

    # ================= 阶段1处理 =================
    cla1_mooc = cla_mooc.loc[:, names1].copy()
    cla1_mooc_copy = cla1_mooc.copy(deep=True)
    cla1_mooc = add_completion_columns(cla1_mooc, cutoff_ts=timestamp1, strict_scope=True)
    cla1_mooc = process_dataframe_for_lels(cla1_mooc, timestamp_value=timestamp1)
    v_end, c_end, h_end = ends_from_names(names1)
    cla1_mooc = Calculate_method.calculate_LE(cla1_mooc, v_end, c_end, h_end, cla1_mooc)
    cla1_mooc = Calculate_method.calculate_LS(cla1_mooc, v_end, c_end, h_end, cla1_mooc)
    cla1_mooc = Calculate_method.calculate_LAcc_RPI(cla1_mooc, v_end, c_end, h_end, cla1_mooc)
    cla1_mooc = cla1_mooc.dropna(subset=['grade_label']).fillna(0)
    cla1_mooc = keep_only_new_features(cla1_mooc)
    cla1_Save_path = os.path.join(Save_path, 'Jieduan1.csv')
    cla1_mooc_copy = cla1_mooc_copy.merge(cla1_mooc, on="SID", how="left", suffixes=("", "_new"))
    cla1_mooc_copy.rename(columns={c: c.replace("_new", "") for c in cla1_mooc_copy.columns if c.endswith("_new")}, inplace=True)
    cla1_mooc_copy = merge_stage_copy(cla1_mooc_copy, cla1_mooc)
    cla1_mooc_copy = add_cumulative_homework_grade(cla1_mooc_copy)
    cla1_mooc_copy.set_index('SID', inplace=True)
    cla1_mooc_copy.to_csv(cla1_Save_path)

    # ================= 阶段2-6处理（类似结构） =================
    # 阶段2
    cla2_mooc = cla_mooc.loc[:, names2].copy()
    cla2_mooc_copy = cla2_mooc.copy(deep=True)
    cla2_mooc = add_completion_columns(cla2_mooc, cutoff_ts=timestamp2, strict_scope=True)
    cla2_mooc = process_dataframe_for_lels(cla2_mooc, timestamp_value=timestamp2)
    v_end, c_end, h_end = ends_from_names(names2)
    cla2_mooc = Calculate_method.calculate_LE(cla2_mooc, v_end, c_end, h_end, cla2_mooc)
    cla2_mooc = Calculate_method.calculate_LS(cla2_mooc, v_end, c_end, h_end, cla2_mooc)
    cla2_mooc = Calculate_method.calculate_LAcc_RPI(cla2_mooc, v_end, c_end, h_end, cla2_mooc)
    cla2_mooc = cla2_mooc.dropna(subset=['grade_label']).fillna(0)
    cla2_mooc = keep_only_new_features(cla2_mooc)
    cla2_Save_path = os.path.join(Save_path, 'Jieduan2.csv')
    cla2_mooc_copy = cla2_mooc_copy.merge(cla2_mooc, on="SID", how="left", suffixes=("", "_new"))
    cla2_mooc_copy.rename(columns={c: c.replace("_new", "") for c in cla2_mooc_copy.columns if c.endswith("_new")}, inplace=True)
    cla2_mooc_copy = merge_stage_copy(cla2_mooc_copy, cla2_mooc)
    cla2_mooc_copy = add_cumulative_homework_grade(cla2_mooc_copy)
    cla2_mooc_copy.set_index('SID', inplace=True)
    cla2_mooc_copy.to_csv(cla2_Save_path)

    # 阶段3-6（代码结构类似，详见原始文件）
    # 此处省略类似代码...


def cond_jointdata_MOOC_Universal(folder_path):
    """
    通用MOOC数据读取函数
    根据文件夹年份自动选择合适的读取函数
    """
    if '2020' in folder_path or '2021' in folder_path:
        return cond_jointdata_MOOC(folder_path)
    else:
        return cond_jointdata_MOOC_22_23(folder_path)


# 其他辅助函数可根据需要添加...
