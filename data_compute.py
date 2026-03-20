"""
数据计算模块 - data_compute.py
基于MOOC和离线成绩数据，计算多个学习阶段的特征指标

主要功能：
1. 读取预处理好的合并数据文件
2. 按照不同阶段（周/月/累计）切分数据
3. 计算各类学习特征：LE、LS、固定加权相关等
4. 输出各阶段特征文件和汇总文件
"""

import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
import os
import warnings

warnings.filterwarnings('ignore')

# ================= 配置区域 =================
# 输入文件路径（预处理好的合并数据）
INPUT_FILE = 'Source_Data_Only_TEST.csv'

# 输出目录
OUTPUT_DIR = 'Calculated_Stages_Output'

# 汇总文件名
SUMMARY_FILE = 'All_Stages_Summary.csv'
# ===========================================


# ================= 阶段列定义 =================
# 定义各阶段包含的列名，格式：[SID, 完成时间列, 提交时间列, 作业成绩列, ...]

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

STAGES_MAP = {
    'Jieduan1': names1, 'Jieduan2': names2, 'Jieduan12': names12,
    'Jieduan3': names3, 'Jieduan23': names23, 'Jieduan123': names123,
    'Jieduan4': names4, 'Jieduan34': names34, 'Jieduan1234': names1234,
    'Jieduan5': names5, 'Jieduan45': names45, 'Jieduan12345': names12345,
    'Jieduan6': names6, 'Jieduan56': names56, 'Jieduan123456': names123456
}


class StageCalculator:
    """阶段计算器：处理单个阶段的数据转换和特征计算"""

    def __init__(self, full_df):
        self.full_df = full_df.copy()
        if 'SID' in self.full_df.columns:
            self.full_df['SID'] = self.full_df['SID'].astype(str)

        # 初始化时计算全局成绩和标签
        self.calculate_global_grade_and_label()

    def calculate_global_grade_and_label(self):
        """
        计算综合成绩和二分类标签

        计算公式：grade = MOOCgrade * 0.4 + offlinegrade
        标签逻辑：grade排名前50%为正类(1)，后50%为负类(0)
        """
        print(">>> 正在计算全局成绩与标签...")

        # 确保基础列存在
        if 'MOOCgrade' not in self.full_df.columns:
            print("警告: 'MOOCgrade' 列不存在，默认补0")
            self.full_df['MOOCgrade'] = 0
        if 'offlinegrade' not in self.full_df.columns:
            print("警告: 'offlinegrade' 列不存在，默认补0")
            self.full_df['offlinegrade'] = 0

        self.full_df['MOOCgrade'] = pd.to_numeric(self.full_df['MOOCgrade'], errors='coerce').fillna(0)
        self.full_df['offlinegrade'] = pd.to_numeric(self.full_df['offlinegrade'], errors='coerce').fillna(0)

        # 计算综合成绩
        self.full_df['grade'] = self.full_df['MOOCgrade'] * 0.4 + self.full_df['offlinegrade']

        # 计算二分类标签
        if self.full_df['grade'].sum() == 0:
            self.full_df['grade_label'] = 0
        else:
            rank = self.full_df['grade'].rank(pct=True, method='average')
            self.full_df['grade_label'] = (rank >= 0.5).astype(int)

        print(f"   -> 成绩计算完成. 均值: {self.full_df['grade'].mean():.2f}")
        print(f"   -> 标签计算完成. 正类比例: {self.full_df['grade_label'].mean():.2%}")

    def get_boundary_indices(self, cols):
        """获取各类型列的边界索引"""
        def idx_last(pred):
            idx = [i for i, c in enumerate(cols) if pred(c)]
            return (max(idx) + 1) if idx else 1

        # 完成时间列边界
        v_end = idx_last(lambda c: c.startswith('完成时间') and (c == '完成时间' or (c.startswith('完成时间.') and c.split('.')[-1].isdigit() and int(c.split('.')[-1]) <= 36)))
        c_end = idx_last(lambda c: c.startswith('完成时间.') and c.split('.')[-1].isdigit() and 37 <= int(c.split('.')[-1]) <= 49)
        h_end = idx_last(lambda c: c.startswith('提交时间'))

        c_end = max(c_end, v_end)
        h_end = max(h_end, c_end)
        return v_end, c_end, h_end

    def calculate_LE(self, df_stage, v_end, c_end, h_end):
        """计算学习参与度特征"""
        vals_v = df_stage.iloc[:, 1:v_end]
        vals_c = df_stage.iloc[:, v_end:c_end]
        vals_h = df_stage.iloc[:, c_end:h_end]

        def process_part(vals):
            if vals.empty: return vals
            max_v = vals.max(axis=0)
            min_v = vals.replace(0, np.nan).min(axis=0).fillna(0)
            diff = max_v - min_v
            diff[diff == 0] = 1
            res = vals.copy()
            for col in vals.columns:
                res[col] = np.where(res[col] != 0, (max_v[col] - res[col]) / diff[col], 0)
            return res

        processed_v = process_part(vals_v)
        processed_c = process_part(vals_c)
        processed_h = process_part(vals_h)

        cnt_v = max(processed_v.shape[1], 1)
        cnt_c = max(processed_c.shape[1], 1)
        cnt_h = max(processed_h.shape[1], 1)
        cnt_all = max(processed_v.shape[1] + processed_c.shape[1] + processed_h.shape[1], 1)

        df_stage['LE_video'] = processed_v.sum(axis=1) / cnt_v
        df_stage['LE_chapter'] = processed_c.sum(axis=1) / cnt_c
        df_stage['LE_homework'] = processed_h.sum(axis=1) / cnt_h
        df_stage['LE_all'] = (processed_v.sum(axis=1) + processed_c.sum(axis=1) + processed_h.sum(axis=1)) / cnt_all

        for col in ['LE_video', 'LE_chapter', 'LE_homework', 'LE_all']:
            df_stage[col] = df_stage[col] / (df_stage[col].max() + 1e-9)

        return df_stage

    def calculate_LS(self, df_stage, v_end, c_end, h_end):
        """计算学习稳定性特征"""
        ranges = [(1, v_end), (v_end, c_end), (c_end, h_end)]
        cols_to_calc = list(df_stage.columns[1:h_end])
        temp_df = df_stage[cols_to_calc].copy()
        ls_sums = []

        current_idx = 0
        for start, end in ranges:
            width = end - start
            if width <= 0:
                ls_sums.append(pd.Series(0, index=df_stage.index))
                continue

            subset = temp_df.iloc[:, current_idx : current_idx + width].values
            subset.sort(axis=1)
            subset_df = pd.DataFrame(subset)
            diff_df = subset_df.diff(axis=1).fillna(0).clip(lower=0)
            mask = (subset_df != 0)
            final_block = diff_df * mask.astype(int)

            row_sum = final_block.sum(axis=1).replace(0, 1)
            prob = final_block.div(row_sum, axis=0)
            entropy = -prob * np.log(prob + 1e-9)
            entropy = entropy.where(prob > 0, 0)

            ls_val = entropy.sum(axis=1)
            ls_sums.append(ls_val)
            current_idx += width

        df_stage['LS_video'] = ls_sums[0]
        df_stage['LS_chapter'] = ls_sums[1]
        df_stage['LS_homework'] = ls_sums[2]
        df_stage['LS_all'] = ls_sums[0] + ls_sums[1] + ls_sums[2]

        for col in ['LS_video', 'LS_chapter', 'LS_homework', 'LS_all']:
            df_stage[col] = df_stage[col] / (df_stage[col].max() + 1e-9)

        return df_stage

    def calculate_offline(self, df_stage):
        """计算离线考试相关特征"""
        all_off_cols = [
            '考试学生总用时含罚时第1次周考', '考试学生总用时含罚时第2次周考',
            '考试学生总用时含罚时第3次周考', '考试学生总用时含罚时第4次周考',
            '考试学生总用时含罚时'
        ]
        exist_cols = [c for c in all_off_cols if c in self.full_df.columns]

        if not exist_cols:
            df_stage['LE_score_off'] = 0
            df_stage['LS_score_off'] = 0
            return df_stage

        df_off = self.full_df.loc[df_stage.index, exist_cols].copy()
        df_off = df_off.apply(pd.to_numeric, errors='coerce').fillna(0)

        # LE计算
        max_v = df_off.max(axis=0)
        min_v = df_off.replace(0, np.nan).min(axis=0).fillna(0)
        diff = max_v - min_v
        diff[diff==0] = 1
        df_le = df_off.copy()
        for col in df_off.columns:
            df_le[col] = np.where(df_le[col]!=0, (max_v[col]-df_le[col])/diff[col], 0)
        df_stage['LE_score_off'] = df_le.sum(axis=1) / len(exist_cols)

        # LS计算
        vals = df_off.values
        vals.sort(axis=1)
        diff_ls = pd.DataFrame(vals).diff(axis=1).fillna(0).clip(lower=0)
        row_sum = diff_ls.sum(axis=1).replace(0, 1)
        prob = diff_ls.div(row_sum, axis=0)
        ent = -prob * np.log(prob + 1e-9).where(prob>0, 0)
        df_stage['LS_score_off'] = ent.sum(axis=1)

        df_stage['LE_score_off'] /= (df_stage['LE_score_off'].max() + 1e-9)
        df_stage['LS_score_off'] /= (df_stage['LS_score_off'].max() + 1e-9)
        return df_stage

    def calculate_fixed(self, df_stage):
        """
        计算相关性加权特征

        基于各特征与最终成绩的相关性（Spearman/Pearson）
        计算加权组合特征
        """
        if 'grade_label' not in df_stage.columns:
            print("  -> 跳过Fixed计算: 缺少grade_label")
            return df_stage

        y = df_stage['grade_label']

        if y.std() == 0:
            print("  -> 警告: grade_label是常数，相关性将为0")

        feats = ['LE_video', 'LE_chapter', 'LE_homework', 'LS_video', 'LS_chapter', 'LS_homework', 'LE_score_off', 'LS_score_off']

        s_w = {}
        p_w = {}

        for f in feats:
            if f in df_stage.columns:
                x = df_stage[f].fillna(0)
                if y.std() > 0 and x.std() > 0:
                    s, _ = spearmanr(x, y)
                    p, _ = pearsonr(x, y)
                    s_w[f] = 0 if np.isnan(s) else s
                    p_w[f] = 0 if np.isnan(p) else p
                else:
                    s_w[f] = 0
                    p_w[f] = 0
            else:
                s_w[f] = 0
                p_w[f] = 0

        # 加权求和
        df_stage['LE_Fixed_Spearman'] = s_w['LE_video']*df_stage.get('LE_video',0) + s_w['LE_chapter']*df_stage.get('LE_chapter',0) + s_w['LE_homework']*df_stage.get('LE_homework',0)
        df_stage['LS_Fixed_Spearman'] = s_w['LS_video']*df_stage.get('LS_video',0) + s_w['LS_chapter']*df_stage.get('LS_chapter',0) + s_w['LS_homework']*df_stage.get('LS_homework',0)

        df_stage['LE_Fixed_Spearman_withoffline'] = df_stage['LE_Fixed_Spearman'] + s_w['LE_score_off']*df_stage.get('LE_score_off',0)
        df_stage['LS_Fixed_Spearman_withoffline'] = df_stage['LS_Fixed_Spearman'] + s_w['LS_score_off']*df_stage.get('LS_score_off',0)

        df_stage['LE_Fixed_Person'] = p_w['LE_video']*df_stage.get('LE_video',0) + p_w['LE_chapter']*df_stage.get('LE_chapter',0) + p_w['LE_homework']*df_stage.get('LE_homework',0)
        df_stage['LS_Fixed_Person'] = p_w['LS_video']*df_stage.get('LS_video',0) + p_w['LS_chapter']*df_stage.get('LS_chapter',0) + p_w['LS_homework']*df_stage.get('LS_homework',0)

        df_stage['LE_Fixed_Person_withoffline'] = df_stage['LE_Fixed_Person'] + p_w['LE_score_off']*df_stage.get('LE_score_off',0)
        df_stage['LS_Fixed_Person_withoffline'] = df_stage['LS_Fixed_Person'] + p_w['LS_score_off']*df_stage.get('LS_score_off',0)

        fix_cols = ['LE_Fixed_Spearman', 'LS_Fixed_Spearman', 'LE_Fixed_Spearman_withoffline', 'LS_Fixed_Spearman_withoffline',
                    'LE_Fixed_Person', 'LS_Fixed_Person', 'LE_Fixed_Person_withoffline', 'LS_Fixed_Person_withoffline']

        for c in fix_cols:
            df_stage[c] = df_stage[c] / (df_stage[c].max() + 1e-9)

        return df_stage

    def process_stages(self, output_dir):
        """处理所有阶段的数据"""
        os.makedirs(output_dir, exist_ok=True)
        all_stages_summary = []

        for stage_name, cols in STAGES_MAP.items():
            print(f"正在处理阶段: {stage_name} ...")

            # 筛选有效列
            valid_cols = [c for c in cols if c in self.full_df.columns]

            # 创建阶段DataFrame
            df_stage = self.full_df[['SID']].copy()

            for c in valid_cols:
                if c != 'SID':
                    df_stage[c] = self.full_df[c]

            # 添加全局grade和grade_label
            df_stage['grade'] = self.full_df['grade']
            df_stage['grade_label'] = self.full_df['grade_label']

            # 补全缺失列
            for c in cols:
                if c not in df_stage.columns:
                    df_stage[c] = 0

            # 按定义顺序排列
            df_stage = df_stage[cols]

            # 转数值
            exclude = ['SID']
            for c in df_stage.columns:
                if c not in exclude:
                    df_stage[c] = pd.to_numeric(df_stage[c], errors='coerce').fillna(0)

            # 计算特征
            v_end, c_end, h_end = self.get_boundary_indices(cols)

            df_stage = self.calculate_LE(df_stage, v_end, c_end, h_end)
            df_stage = self.calculate_LS(df_stage, v_end, c_end, h_end)
            df_stage = self.calculate_offline(df_stage)
            df_stage = self.calculate_fixed(df_stage)

            # 保存
            output_path = os.path.join(output_dir, f"{stage_name}.csv")
            df_stage.to_csv(output_path, index=False)

            # 汇总
            feature_cols = [c for c in df_stage.columns if c.startswith('LE_') or c.startswith('LS_')]
            summary_df = df_stage[['SID'] + feature_cols].copy()
            summary_df['Stage'] = stage_name
            summary_df['grade_label'] = df_stage['grade_label']
            all_stages_summary.append(summary_df)

        return all_stages_summary


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"错误: 找不到输入文件 {INPUT_FILE}")
        return

    print("正在读取源数据...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"源数据形状: {df.shape}")
    except Exception as e:
        print(f"读取失败: {e}")
        return

    calc = StageCalculator(df)
    summaries = calc.process_stages(OUTPUT_DIR)

    if summaries:
        print("正在合并汇总文件...")
        final_summary = pd.concat(summaries, ignore_index=True)
        final_summary.to_csv(SUMMARY_FILE, index=False)
        print(f"完成! \n1. 各阶段文件: {os.path.abspath(OUTPUT_DIR)} \n2. 汇总文件: {os.path.abspath(SUMMARY_FILE)}")
    else:
        print("未生成任何数据。")


if __name__ == '__main__':
    main()