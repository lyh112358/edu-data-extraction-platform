"""
数据处理模块 - Data_handler.py
负责读取多年级的MOOC数据，生成不同阶段的统计数据

功能说明：
- 遍历指定年份的数据文件夹
- 读取MOOC子文件夹中的Excel成绩文件
- 调用数据处理模块生成各阶段（周/月）的统计数据
"""

import os
import traceback

print("=" * 60)
print(">>> Data_handler.py 启动中...")
print("=" * 60)

script_dir = os.path.dirname(os.path.abspath(__file__))

# 数据年份文件夹列表（可根据实际需要增删年份）
file_paths = [
    os.path.join(script_dir, 'data2020'),
    os.path.join(script_dir, 'data2021'),
    os.path.join(script_dir, 'data2022'),
    os.path.join(script_dir, 'data2023'),
    os.path.join(script_dir, 'data2024'),
    os.path.join(script_dir, 'data2025'),
]


def main():
    import Normal_data_conducted as cond

    # 输出目录：result_20_25 文件夹
    base_output = os.path.join(script_dir, 'result_20_25')
    os.makedirs(base_output, exist_ok=True)

    print(f"输出目录: {os.path.abspath(base_output)}")
    print()

    success_count = 0

    # 遍历每个年份文件夹
    for folder_path in file_paths:
        year_name = os.path.basename(folder_path)
        print("=" * 50)
        print(f"正在处理: {year_name}")
        print("=" * 50)

        # 检查年份文件夹是否存在
        if not os.path.exists(folder_path):
            print(f"  [跳过] 文件夹不存在")
            continue

        # 检查MOOC子文件夹
        mooc_path = os.path.join(folder_path, 'MOOC')
        if not os.path.exists(mooc_path):
            print(f"  [跳过] MOOC文件夹不存在")
            continue

        # 筛选有效的Excel文件（排除临时文件）
        xlsx_files = [f for f in os.listdir(mooc_path) if f.endswith('.xlsx') and not f.startswith('~$')]
        if not xlsx_files:
            print(f"  [跳过] 没有找到Excel文件")
            continue

        try:
            print("  正在读取MOOC数据...")
            df = cond.cond_jointdata_MOOC_Universal(folder_path)

            if df.empty:
                print(f"  [错误] 未提取到数据")
                continue

            # 创建年份输出目录
            save_dir = os.path.join(base_output, year_name)
            os.makedirs(save_dir, exist_ok=True)

            # 生成阶段文件
            print("  正在生成阶段数据...")
            cond.cond_all_LELS_forJieduanxing_v20(df, folder_path, save_dir)

            success_count += 1

        except Exception as e:
            print(f"  [错误] {e}")
            traceback.print_exc()

        print()

    print("=" * 60)
    print(f"处理完成: 成功处理 {success_count}/{len(file_paths)} 个年份文件夹")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"严重错误: {e}")
        traceback.print_exc()