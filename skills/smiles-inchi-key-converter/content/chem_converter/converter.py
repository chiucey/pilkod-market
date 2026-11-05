"""
Chem-Converter 核心转换模块
跨平台支持：Windows、Linux、macOS
"""

import os
import sys
import re
import tempfile
import subprocess
import shutil
import pandas as pd
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


def find_openbabel() -> Optional[str]:
    """自动检测OpenBabel可执行文件路径"""
    # 1. 检查环境变量
    obabel_env = os.environ.get('OBABEL_PATH')
    if obabel_env and os.path.exists(obabel_env):
        return obabel_env

    # 2. 检查PATH中的obabel
    obabel_in_path = shutil.which('obabel')
    if obabel_in_path:
        return obabel_in_path

    # 3. Windows常见路径 (用户级Anaconda/Miniconda)
    if sys.platform == 'win32':
        import glob as _glob
        # 搜索用户目录下的常见conda安装路径
        user_home = os.environ.get('USERPROFILE', os.environ.get('HOME', 'C:\\'))
        search_patterns = [
            rf"{user_home}\**\obabel.exe",
            r"C:\ProgramData\Anaconda3\Library\bin\obabel.exe",
            r"C:\ProgramData\miniconda3\Library\bin\obabel.exe",
            r"C:\Users\Public\Anaconda3\Library\bin\obabel.exe",
            r"C:\Users\Public\miniconda3\Library\bin\obabel.exe",
            r"C:\Anaconda3\Library\bin\obabel.exe",
            r"C:\miniconda3\Library\bin\obabel.exe",
        ]
        for pattern in search_patterns:
            if '*' in pattern:
                matches = _glob.glob(pattern, recursive=True)
                if matches:
                    return matches[0]
            elif os.path.exists(pattern):
                return pattern

    # 4. Linux/macOS常见路径
    possible_paths = [
        '/usr/bin/obabel',
        '/usr/local/bin/obabel',
        '/opt/homebrew/bin/obabel',
        '/opt/openbabel/bin/obabel',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


# 全局OpenBabel路径
OBABEL_PATH = find_openbabel()


def check_openbabel() -> Tuple[bool, str]:
    """检查OpenBabel是否可用"""
    if OBABEL_PATH is None:
        return False, "OpenBabel not found. Please install and ensure 'obabel' is in PATH."
    try:
        result = subprocess.run(
            [OBABEL_PATH, '--version'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, f"OpenBabel error: {result.stderr}"
    except Exception as e:
        return False, str(e)


def _run_obabel(input_data: str, input_format: str, output_format: str) -> Optional[str]:
    """通用OpenBabel转换调用"""
    if OBABEL_PATH is None:
        return None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.tmp', delete=False, encoding='utf-8') as f:
            f.write(input_data)
            input_file = f.name

        try:
            result = subprocess.run(
                [OBABEL_PATH, input_file, f'-i{input_format}', f'-o{output_format}'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        finally:
            if os.path.exists(input_file):
                os.unlink(input_file)
    except:
        return None


def smiles_to_inchi(smiles: str) -> Optional[str]:
    """SMILES → InChI"""
    if not smiles or pd.isna(smiles):
        return None
    try:
        output = _run_obabel(str(smiles), 'smi', 'inchi')
        if output and 'InChI=' in output:
            return output.split('InChI=')[1].split('\n')[0].strip()
        return None
    except:
        return None


def smiles_to_inchikey(smiles: str) -> Optional[str]:
    """SMILES → InChIKey"""
    if not smiles or pd.isna(smiles):
        return None
    try:
        return _run_obabel(str(smiles), 'smi', 'inchikey')
    except:
        return None


def inchi_to_smiles(inchi: str) -> Optional[str]:
    """InChI → SMILES"""
    if not inchi or pd.isna(inchi):
        return None
    try:
        inchi_str = str(inchi)
        if not inchi_str.startswith('InChI='):
            inchi_str = 'InChI=' + inchi_str
        output = _run_obabel(inchi_str, 'inchi', 'smi')
        if output:
            return output.split('\n')[0].strip()
        return None
    except:
        return None


def inchi_to_inchikey(inchi: str) -> Optional[str]:
    """InChI → InChIKey"""
    if not inchi or pd.isna(inchi):
        return None
    try:
        inchi_str = str(inchi)
        if not inchi_str.startswith('InChI='):
            inchi_str = 'InChI=' + inchi_str
        return _run_obabel(inchi_str, 'inchi', 'inchikey')
    except:
        return None


def inchikey_to_inchi(inchikey: str) -> Optional[str]:
    """InChIKey → InChI (验证格式，返回说明)"""
    if not inchikey or pd.isna(inchikey):
        return None
    # InChIKey是哈希值，无法本地反向推导
    # 仅验证格式
    if validate_inchikey(inchikey):
        return f"Note: InChIKey '{inchikey}' format is valid. Local reverse lookup not supported."
    return None


def validate_inchikey(inchikey: str) -> bool:
    """验证InChIKey格式 (14-10-1)"""
    if not inchikey or pd.isna(inchikey):
        return False
    parts = str(inchikey).split('-')
    if len(parts) != 3:
        return False
    return len(parts[0]) == 14 and len(parts[1]) == 10 and len(parts[2]) == 1


def batch_convert(
    input_file: str,
    output_file: str,
    smiles_col: Optional[str] = None,
    inchi_col: Optional[str] = None,
    convert_direction: str = "smiles_to_inchikey",
    max_workers: int = 5
) -> dict:
    """
    批量转换Excel文件中的化学标识符

    Args:
        input_file: 输入Excel文件路径
        output_file: 输出Excel文件路径
        smiles_col: SMILES列名（自动检测如未指定）
        inchi_col: InChI列名（自动检测如未指定）
        convert_direction: 转换方向
            - "smiles_to_inchikey": SMILES → InChI + InChIKey
            - "inchi_to_smiles": InChI → SMILES
        max_workers: 并行线程数
    """
    print(f"Reading: {input_file}")
    df = pd.read_excel(input_file)
    print(f"Total rows: {len(df)}")

    results_inchi = [None] * len(df)
    results_inchikey = [None] * len(df)
    results_smiles = [None] * len(df)

    def convert_smiles_row(idx_smiles_tuple):
        idx, smiles = idx_smiles_tuple
        inchi = smiles_to_inchi(smiles)
        inchikey = smiles_to_inchikey(smiles)
        return idx, inchi, inchikey

    def convert_inchi_row(idx_inchi_tuple):
        idx, inchi = idx_inchi_tuple
        smiles = inchi_to_smiles(inchi)
        return idx, smiles

    if convert_direction == "smiles_to_inchikey":
        # 自动检测SMILES列
        if smiles_col is None:
            for col in ['SMILES', 'SMILES(neutral form)', 'smiles', 'Smiles', 'SMILES']:
                if col in df.columns:
                    smiles_col = col
                    break

        if smiles_col is None:
            raise ValueError(f"SMILES column not found. Available columns: {df.columns.tolist()}")

        print(f"Using SMILES column: {smiles_col}")
        print(f"Converting SMILES → InChI + InChIKey...")

        smiles_list = [(i, s) for i, s in enumerate(df[smiles_col].tolist())]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(convert_smiles_row, item): item[0] for item in smiles_list}
            completed = 0
            for future in as_completed(futures):
                idx, inchi, inchikey = future.result()
                results_inchi[idx] = inchi
                results_inchikey[idx] = inchikey
                completed += 1
                if completed % 100 == 0:
                    valid = sum(1 for r in results_inchi if r is not None)
                    print(f"  Progress: {completed}/{len(df)} (Success: {valid})")

        # 添加结果列
        smiles_idx = df.columns.get_loc(smiles_col)
        df.insert(smiles_idx + 1, 'InChI', results_inchi)
        df.insert(smiles_idx + 2, 'InChIKey', results_inchikey)

        valid_count = sum(1 for r in results_inchi if r is not None)
        print(f"Done! Success: {valid_count}/{len(df)} ({valid_count/len(df)*100:.1f}%)")

    elif convert_direction == "inchi_to_smiles":
        # 自动检测InChI列
        if inchi_col is None:
            for col in ['InChI', 'InChI string', 'inchi', 'InChi']:
                if col in df.columns:
                    inchi_col = col
                    break

        if inchi_col is None:
            raise ValueError(f"InChI column not found. Available columns: {df.columns.tolist()}")

        print(f"Using InChI column: {inchi_col}")
        print(f"Converting InChI → SMILES...")

        inchi_list = [(i, s) for i, s in enumerate(df[inchi_col].tolist())]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(convert_inchi_row, item): item[0] for item in inchi_list}
            completed = 0
            for future in as_completed(futures):
                idx, smiles = future.result()
                results_smiles[idx] = smiles
                completed += 1
                if completed % 100 == 0:
                    valid = sum(1 for r in results_smiles if r is not None)
                    print(f"  Progress: {completed}/{len(df)} (Success: {valid})")

        # 添加结果列
        inchi_idx = df.columns.get_loc(inchi_col)
        df.insert(inchi_idx + 1, 'SMILES', results_smiles)

        valid_count = sum(1 for r in results_smiles if r is not None)
        print(f"Done! Success: {valid_count}/{len(df)} ({valid_count/len(df)*100:.1f}%)")

    else:
        raise ValueError(f"Unknown direction: {convert_direction}")

    print(f"Saving: {output_file}")
    df.to_excel(output_file, index=False)
    return {"total": len(df), "success": valid_count, "output_file": output_file}


def interactive_mode():
    """交互式转换模式"""
    print("=" * 55)
    print("   Chem-Converter: Local Chemical ID Converter")
    print("=" * 55)
    print()

    # 检查OpenBabel
    ok, msg = check_openbabel()
    if not ok:
        print(f"WARNING: {msg}")
        print()
    else:
        print(f"OpenBabel: {msg}")
    print()

    print("Supported conversions:")
    print("  1. SMILES → InChI + InChIKey")
    print("  2. InChI → SMILES + InChIKey")
    print("  3. Validate InChIKey format")
    print("  4. Check OpenBabel status")
    print("  0. Exit")
    print()

    while True:
        choice = input("Select (0-4): ").strip()

        if choice == '0':
            print("Goodbye!")
            break

        elif choice == '1':
            smiles = input("  SMILES: ").strip()
            if smiles:
                inchi = smiles_to_inchi(smiles)
                inchikey = smiles_to_inchikey(smiles)
                print(f"  SMILES: {smiles}")
                if inchi:
                    print(f"  InChI: InChI={inchi}")
                if inchikey:
                    print(f"  InChIKey: {inchikey}")
                if not inchi and not inchikey:
                    print("  [FAILED] Check if SMILES is valid")

        elif choice == '2':
            inchi = input("  InChI: ").strip()
            if inchi:
                smiles = inchi_to_smiles(inchi)
                inchikey = inchi_to_inchikey(inchi)
                print(f"  InChI: {inchi}")
                if smiles:
                    print(f"  SMILES: {smiles}")
                if inchikey:
                    print(f"  InChIKey: {inchikey}")
                if not smiles and not inchikey:
                    print("  [FAILED] Check if InChI is valid")

        elif choice == '3':
            inchikey = input("  InChIKey: ").strip()
            if inchikey:
                valid = validate_inchikey(inchikey)
                if valid:
                    print(f"  Valid InChIKey: {inchikey}")
                    print(f"  Note: InChIKey is a hash, cannot reverse locally")
                else:
                    print(f"  Invalid format. Expected: XXXXX-XXXXXXX-X (14-10-1)")

        elif choice == '4':
            ok, msg = check_openbabel()
            if ok:
                print(f"  OK: {msg}")
            else:
                print(f"  ERROR: {msg}")

        else:
            print("  Invalid choice")

        print()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Chem-Converter: Local SMILES/InChI/InChIKey converter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m chem_converter --smiles "CCO"
  python -m chem_converter --inchi "InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"
  python -m chem_converter --check
  python -m chem_converter --interactive
        """
    )

    parser.add_argument('--smiles', '-s', help='SMILES string')
    parser.add_argument('--inchi', help='InChI string')
    parser.add_argument('--inchikey', '-i', help='InChIKey (validate only)')
    parser.add_argument('--check', action='store_true', help='Check OpenBabel status')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    if args.check:
        ok, msg = check_openbabel()
        if ok:
            print(f"OK: {msg}")
        else:
            print(f"ERROR: {msg}")
        return

    if args.smiles:
        smiles = args.smiles
        inchi = smiles_to_inchi(smiles)
        inchikey = smiles_to_inchikey(smiles)
        print(f"SMILES: {smiles}")
        if inchi:
            print(f"InChI: InChI={inchi}")
        if inchikey:
            print(f"InChIKey: {inchikey}")
        if not inchi and not inchikey:
            print("FAILED")
        return

    if args.inchi:
        inchi = args.inchi
        smiles = inchi_to_smiles(inchi)
        inchikey = inchi_to_inchikey(inchi)
        print(f"InChI: {inchi}")
        if smiles:
            print(f"SMILES: {smiles}")
        if inchikey:
            print(f"InChIKey: {inchikey}")
        if not smiles and not inchikey:
            print("FAILED")
        return

    if args.inchikey:
        inchikey = args.inchikey
        valid = validate_inchikey(inchikey)
        print(f"InChIKey: {inchikey}")
        if valid:
            print("Format: VALID (14-10-1)")
            print("Note: Cannot reverse locally")
        else:
            print("Format: INVALID (expected: XXXXX-XXXXXXX-X)")
        return

    interactive_mode()


if __name__ == "__main__":
    main()
