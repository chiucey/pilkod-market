"""文件解析模块：统一提取 docx/pdf/xlsx/xls/txt 文本。"""

import os

import docx
import openpyxl
import pdfplumber
import xlrd


def _warn(file_path: str, message: str) -> None:
    """打印统一格式的告警日志。"""
    print(f"[WARN] 文件解析告警: {file_path} | {message}")


def _read_docx(file_path: str) -> str:
    """读取 .docx：提取所有非空段落文本。"""
    document = docx.Document(file_path)
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
    return "\n".join(paragraphs)


def _read_pdf(file_path: str) -> str:
    """
    读取 .pdf：提取全部页面可识别文本。
    若为扫描件/图片型 PDF，pdfplumber 通常提取为空，此时返回空字符串。
    """
    texts: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = (page.extract_text() or "").strip()
            if page_text:
                texts.append(page_text)
    return "\n".join(texts).strip()


def _read_xlsx(file_path: str) -> str:
    """读取 .xlsx：遍历所有工作表和单元格，提取非空值并用空格拼接。"""
    values: list[str] = []
    workbook = openpyxl.load_workbook(file_path, data_only=True, read_only=True)
    try:
        for sheet in workbook.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell is None:
                        continue
                    text = str(cell).strip()
                    if text:
                        values.append(text)
    finally:
        workbook.close()
    return " ".join(values)


def _read_xls(file_path: str) -> str:
    """读取 .xls：使用 xlrd 遍历所有单元格，提取非空值并用空格拼接。"""
    values: list[str] = []
    workbook = xlrd.open_workbook(file_path)
    for sheet_idx in range(workbook.nsheets):
        sheet = workbook.sheet_by_index(sheet_idx)
        for row_idx in range(sheet.nrows):
            for col_idx in range(sheet.ncols):
                cell_value = sheet.cell_value(row_idx, col_idx)
                text = str(cell_value).strip()
                if text:
                    values.append(text)
    return " ".join(values)


def _read_txt(file_path: str) -> str:
    """读取 .txt：优先 UTF-8，失败后回退 GBK。"""
    encodings = ("utf-8", "gbk")
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # 文本编码都不匹配，最后再尝试忽略错误读取，降低失败率
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(file_path: str, max_chars: int = 2000) -> str:
    """
    根据文件扩展名提取文本内容。
    支持：.docx, .pdf, .xlsx, .xls, .txt
    提取前 max_chars 字符，用于大模型分析和全文检索。
    若文件无法解析或为扫描件，返回空字符串。
    """
    if not file_path:
        _warn(file_path, "文件路径为空")
        return ""
    if not os.path.exists(file_path):
        _warn(file_path, "文件不存在")
        return ""

    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext == ".docx":
            text = _read_docx(file_path)
        elif ext == ".pdf":
            text = _read_pdf(file_path)
        elif ext == ".xlsx":
            text = _read_xlsx(file_path)
        elif ext == ".xls":
            text = _read_xls(file_path)
        elif ext == ".txt":
            text = _read_txt(file_path)
        else:
            _warn(file_path, f"不支持的文件类型: {ext}")
            return ""

        # PDF 扫描件常见场景：可读文本为空，按要求返回空字符串
        if not text or not text.strip():
            _warn(file_path, "未提取到有效文本（可能是扫描件或空文件）")
            return ""

        return text.strip()[:max_chars]
    except Exception as exc:  # noqa: BLE001
        _warn(file_path, f"解析异常: {exc}")
        return ""

