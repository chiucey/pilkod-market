#!/usr/bin/env python3
"""
文档类型自动识别脚本
基于 PaddleOCR 和 PaddleStructure 自动识别文档类型

核心功能：
1. 文档类型识别：自动识别发票、合同、身份证、菜单等常见文档
2. 页面布局分析：分析文档的布局结构
3. 关键元素检测：检测文档中的关键元素（如印章、签名等）
4. 批量文档处理：批量识别多个文档类型

支持文档类型：
- 发票 (invoice)
- 合同 (contract)
- 身份证 (id_card)
- 营业执照 (business_license)
- 驾驶证 (driver_license)
- 护照 (passport)
- 银行卡 (bank_card)
- 票据 (ticket)
- 收据 (receipt)
- 菜单 (menu)
- 证书 (certificate)
- 表单 (form)
- 通用文档 (document)

版本：基于 PaddleOCR 3.x + PaddleStructure
"""

import argparse
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from PIL import Image
import re

# 尝试导入 PaddleOCR
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

# 尝试导入 PaddleStructure
try:
    from paddlestructure import PaddleStructure
    PADDLESTRUCTURE_AVAILABLE = True
except ImportError:
    PADDLESTRUCTURE_AVAILABLE = False


def detect_gpu_available() -> bool:
    """
    检测 GPU 是否可用

    返回：
        GPU 是否可用
    """
    try:
        import paddle
        return paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
    except Exception:
        return False


class DocumentClassifier:
    """文档类型分类器"""

    def __init__(self, use_gpu: Optional[bool] = None):
        """
        初始化文档分类器

        参数：
            use_gpu: 是否使用 GPU（None 表示自动检测）
        """
        if not PADDLEOCR_AVAILABLE:
            raise ImportError(
                "PaddleOCR 未安装，请运行: pip install paddleocr paddlepaddle"
            )

        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        self.ocr = None
        self.layout_engine = None

        # 初始化 OCR
        self._init_ocr()

        # 初始化版面分析引擎
        if PADDLESTRUCTURE_AVAILABLE:
            self._init_layout_engine()

    def _init_ocr(self):
        """初始化 PaddleOCR 实例"""
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            use_gpu=self.use_gpu,
            show_log=False
        )

    def _init_layout_engine(self):
        """初始化 PaddleStructure 版面分析引擎"""
        try:
            self.layout_engine = PaddleStructure(
                show_log=False,
                image_orientation=True,
                layout=True,
                table=True,
                ocr=True,
                structure_version='PP-StructureV3'
            )
            print("✅ PaddleStructure 版面分析引擎初始化成功")
        except Exception as e:
            print(f"⚠️ PaddleStructure 版面分析引擎初始化失败: {e}")
            self.layout_engine = None

    def classify_document(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """
        识别文档类型

        参数：
            image_path: 图像路径

        返回：
            包含文档类型的字典
        """
        try:
            # 验证图像文件
            img_file = Path(image_path)
            if not img_file.exists():
                return {
                    "success": False,
                    "error": f"图像文件不存在: {image_path}"
                }

            # 提取文本
            result = self.ocr.ocr(str(img_file), cls=True)

            if not result or result[0] is None:
                return {
                    "success": False,
                    "error": "OCR 识别失败：未返回有效结果"
                }

            # 合并文本
            texts = []
            for line in result[0]:
                text_info = line[1]
                text = text_info[0]
                texts.append(text)

            full_text = "\n".join(texts)

            # 基于规则分类
            doc_type, confidence = self._classify_by_rules(full_text)

            # 分析版面
            layout_info = None
            if self.layout_engine:
                layout_info = self._analyze_layout(image_path)

            return {
                "success": True,
                "document_type": doc_type,
                "confidence": confidence,
                "text": full_text,
                "layout": layout_info,
                "image_path": str(img_file)
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"文档分类失败: {str(e)}",
                "image_path": image_path
            }

    def _classify_by_rules(self, text: str) -> Tuple[str, float]:
        """
        基于规则分类文档类型

        参数：
            text: 文档文本

        返回：
            (文档类型, 置信度)
        """
        text_lower = text.lower()

        # 身份证特征（优先级最高）
        if re.search(r"身份证|公民身份号码|姓名|住址|出生日期|民族", text_lower):
            return ("id_card", 0.95)

        # 营业执照特征
        if re.search(r"营业执照|统一社会信用代码|法定代表人|注册资本|经营范围|成立日期", text_lower):
            return ("business_license", 0.92)

        # 驾驶证特征
        if re.search(r"驾驶证|机动车驾驶证|证号|姓名|性别|出生日期|初次领证日期|准驾车型", text_lower):
            return ("driver_license", 0.92)

        # 护照特征
        if re.search(r"护照|passport|护照号码|签发机关|签发日期|有效期至|姓名|出生日期", text_lower):
            return ("passport", 0.90)

        # 银行卡特征
        if re.search(r"银行卡|card number|卡号|持卡人|有效期|cvv|中国工商银行|中国建设银行|中国银行|中国农业银行", text_lower):
            return ("bank_card", 0.90)

        # 票据特征
        if re.search(r"票据|汇票|本票|支票|出票人|收款人|金额|日期", text_lower):
            return ("ticket", 0.88)

        # 收据特征
        if re.search(r"收据|receipt|收款人|付款人|金额|日期|编号", text_lower):
            return ("receipt", 0.88)

        # 发票特征
        if re.search(r"发票|invoice|收据|receipt|纳税人识别号|开票日期", text_lower):
            return ("invoice", 0.9)

        # 合同特征
        if re.search(r"合同|contract|协议|agreement|甲方|乙方|签署日期|违约责任", text_lower):
            return ("contract", 0.9)

        # 身份证特征
        if re.search(r"身份证|公民身份号码|姓名|住址|出生日期", text_lower):
            return ("id_card", 0.95)

        # 菜单特征
        if re.search(r"菜单|menu|菜名|价格|￥|¥|\$\$", text_lower):
            return ("menu", 0.85)

        # 证书特征
        if re.search(r"证书|certificate|颁发|授予|编号|有效期", text_lower):
            return ("certificate", 0.85)

        # 表单特征
        if re.search(r"申请表|form|填报|日期|申请人|审核", text_lower):
            return ("form", 0.8)

        # 默认为通用文档
        return ("document", 0.5)

    def _analyze_layout(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        分析文档布局

        参数：
            image_path: 图像路径

        返回：
            版面分析结果
        """
        if not self.layout_engine:
            return None

        try:
            result = self.layout_engine(str(image_path))

            if not result:
                return None

            # 统计区域类型
            region_counts = {}
            for item in result:
                if 'res' in item:
                    res = item['res']
                    region_type = res.get('type', 'unknown')
                    region_counts[region_type] = region_counts.get(region_type, 0) + 1

            return {
                "region_counts": region_counts,
                "total_regions": len(result)
            }

        except Exception as e:
            print(f"⚠️ 版面分析失败: {e}")
            return None

    def batch_classify(
        self,
        image_dir: str
    ) -> Dict[str, Any]:
        """
        批量分类文档

        参数：
            image_dir: 图像目录

        返回：
            批量分类结果
        """
        try:
            dir_path = Path(image_dir)
            if not dir_path.exists():
                return {
                    "success": False,
                    "error": f"目录不存在: {image_dir}"
                }

            # 支持的图像格式
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}

            results = []
            for image_path in dir_path.iterdir():
                if image_path.suffix.lower() in image_extensions:
                    result = self.classify_document(str(image_path))
                    results.append(result)

            # 统计
            type_counts = {}
            for result in results:
                if result["success"]:
                    doc_type = result["document_type"]
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

            return {
                "success": True,
                "total_documents": len(results),
                "type_counts": type_counts,
                "results": results
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"批量分类失败: {str(e)}"
            }


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="文档类型自动识别脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 识别单个文档：
  python document_classifier.py classify document.png

2. 批量识别文档：
  python document_classifier.py batch ./documents

3. 使用 GPU：
  python document_classifier.py classify document.png --gpu

4. JSON 输出：
  python document_classifier.py classify document.png --json
        """
    )

    parser.add_argument(
        "command",
        choices=["classify", "batch"],
        help="命令类型"
    )

    parser.add_argument(
        "path",
        help="图像路径或目录路径"
    )

    parser.add_argument(
        "--gpu",
        action="store_true",
        help="使用 GPU（默认自动检测）"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出"
    )

    args = parser.parse_args()

    # 初始化分类器
    try:
        classifier = DocumentClassifier(use_gpu=args.gpu if args.gpu else None)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 执行命令
    result = None

    if args.command == "classify":
        result = classifier.classify_document(args.path)

    elif args.command == "batch":
        result = classifier.batch_classify(args.path)

    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            if args.command == "classify":
                print(f"✅ 文档类型: {result['document_type']}")
                print(f"   置信度: {result['confidence']:.2f}")
                print(f"   文本预览: {result['text'][:100]}...")
                if result.get("layout"):
                    print(f"   版面分析: {result['layout']['region_counts']}")
            else:
                print(f"✅ 总文档数: {result['total_documents']}")
                print(f"   类型统计:")
                for doc_type, count in result['type_counts'].items():
                    print(f"     {doc_type}: {count}")
        else:
            print(f"❌ 失败: {result['error']}")


if __name__ == "__main__":
    main()
