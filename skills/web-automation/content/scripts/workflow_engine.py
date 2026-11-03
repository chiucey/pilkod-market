#!/usr/bin/env python3
"""
复杂文档和网页理解工作流引擎
支持多步骤自动化流程，实现复杂的文档和网页理解任务

核心功能：
1. 工作流定义：定义多步骤的处理流程
2. 自动化执行：自动执行工作流
3. 结果聚合：聚合多个步骤的结果
4. 错误处理：处理工作流中的错误

支持的工作流类型：
1. 文档理解工作流：OCR → 分类 → 信息提取 → 摘要
2. 网页抓取工作流：浏览器导航 → 截图 → OCR → 提取 → 分析
3. 表格处理工作流：检测 → 识别 → 提取 → 导出
4. 综合分析工作流：多模态分析 → 问答 → 报告生成

版本：1.0.0
"""

import argparse
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

# 导入各个服务
try:
    from ocr_service import OCRService
    OCR_SERVICE_AVAILABLE = True
except ImportError:
    OCR_SERVICE_AVAILABLE = False

try:
    from page_parser import PageParser
    PAGE_PARSER_AVAILABLE = True
except ImportError:
    PAGE_PARSER_AVAILABLE = False

try:
    from chat_ocr_service import ChatOCRService
    CHAT_OCR_AVAILABLE = True
except ImportError:
    CHAT_OCR_AVAILABLE = False

try:
    from vision_language_service import VisionLanguageService
    VISION_LANGUAGE_AVAILABLE = True
except ImportError:
    VISION_LANGUAGE_AVAILABLE = False

try:
    from document_classifier import DocumentClassifier
    DOCUMENT_CLASSIFIER_AVAILABLE = True
except ImportError:
    DOCUMENT_CLASSIFIER_AVAILABLE = False

try:
    from workflow_logger import WorkflowLogger
    WORKFLOW_LOGGER_AVAILABLE = True
except ImportError:
    WORKFLOW_LOGGER_AVAILABLE = False

try:
    from playwright_cli import AsyncPlaywrightBrowser
    PLAYWRIGHT_CLI_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_CLI_AVAILABLE = False


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


class WorkflowEngine:
    """工作流引擎"""

    def __init__(
        self,
        use_gpu: Optional[bool] = None,
        enable_logging: bool = True
    ):
        """
        初始化工作流引擎

        参数：
            use_gpu: 是否使用 GPU（None 表示自动检测）
            enable_logging: 是否启用日志
        """
        # GPU 自动检测
        if use_gpu is None:
            self.use_gpu = detect_gpu_available()
            print(f"🔍 自动检测 GPU: {'使用 GPU' if self.use_gpu else '使用 CPU'}")
        else:
            self.use_gpu = use_gpu

        # 初始化日志
        self.enable_logging = enable_logging
        self.logger = WorkflowLogger() if enable_logging else None

        # 初始化服务
        self.services = {}
        self._init_services()

    def _init_services(self):
        """初始化所有服务"""
        if OCR_SERVICE_AVAILABLE:
            try:
                self.services["ocr"] = OCRService(use_gpu=self.use_gpu)
                print("✅ OCR 服务初始化成功")
            except Exception as e:
                print(f"⚠️ OCR 服务初始化失败: {e}")

        if PAGE_PARSER_AVAILABLE:
            try:
                self.services["page_parser"] = PageParser(use_gpu=self.use_gpu)
                print("✅ 页面解析服务初始化成功")
            except Exception as e:
                print(f"⚠️ 页面解析服务初始化失败: {e}")

        if CHAT_OCR_AVAILABLE:
            try:
                self.services["chat_ocr"] = ChatOCRService(use_gpu=self.use_gpu)
                print("✅ ChatOCR 服务初始化成功")
            except Exception as e:
                print(f"⚠️ ChatOCR 服务初始化失败: {e}")

        if VISION_LANGUAGE_AVAILABLE:
            try:
                self.services["vision_language"] = VisionLanguageService(use_gpu=self.use_gpu)
                print("✅ 视觉语言服务初始化成功")
            except Exception as e:
                print(f"⚠️ 视觉语言服务初始化失败: {e}")

        if DOCUMENT_CLASSIFIER_AVAILABLE:
            try:
                self.services["classifier"] = DocumentClassifier(use_gpu=self.use_gpu)
                print("✅ 文档分类服务初始化成功")
            except Exception as e:
                print(f"⚠️ 文档分类服务初始化失败: {e}")

    def run_document_understanding_workflow(
        self,
        image_path: str,
        questions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        运行文档理解工作流

        流程：OCR 识别 → 文档分类 → 信息提取 → 文档问答（可选）→ 摘要生成

        参数：
            image_path: 文档图像路径
            questions: 文档问答问题列表（可选）

        返回：
            工作流执行结果
        """
        print(f"\n🚀 开始文档理解工作流: {image_path}")

        result = {
            "workflow": "document_understanding",
            "image_path": image_path,
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }

        # 记录工作流开始
        if self.logger:
            self.logger.log_workflow_start("document_understanding", {"image_path": image_path, "questions": questions})

        # 步骤 1：OCR 识别
        print("📝 步骤 1: OCR 识别...")
        if "ocr" in self.services:
            ocr_result = self.services["ocr"].recognize_image(image_path)
            result["steps"]["ocr"] = ocr_result
            if not ocr_result["success"]:
                result["error"] = "OCR 识别失败"
                result["end_time"] = datetime.now().isoformat()
                return result
            print(f"   ✅ 识别到 {len(ocr_result['texts'])} 行文本")
        else:
            print("   ⚠️ OCR 服务不可用")
            result["steps"]["ocr"] = {"success": False, "error": "OCR 服务不可用"}

        # 记录步骤日志
        if self.logger:
            self.logger.log_step("ocr", result["steps"]["ocr"], "ocr" in self.services)

        # 步骤 2：文档分类
        print("🔍 步骤 2: 文档分类...")
        if "classifier" in self.services:
            classify_result = self.services["classifier"].classify_document(image_path)
            result["steps"]["classify"] = classify_result
            if classify_result["success"]:
                print(f"   ✅ 文档类型: {classify_result['document_type']}")
        else:
            print("   ⚠️ 分类服务不可用")

        # 步骤 3：表格识别（如果有表格）
        print("📊 步骤 3: 表格识别...")
        if "ocr" in self.services:
            table_result = self.services["ocr"].extract_table(image_path)
            result["steps"]["table"] = table_result
            if table_result["success"]:
                print(f"   ✅ 识别到 {table_result['table_count']} 个表格")
            else:
                print("   ℹ️ 未检测到表格")
        else:
            print("   ⚠️ OCR 服务不可用")

        # 步骤 4：文档问答（可选）
        if questions and "chat_ocr" in self.services:
            print("❓ 步骤 4: 文档问答...")
            qa_results = []
            for question in questions:
                qa_result = self.services["chat_ocr"].document_qa(image_path, question)
                qa_results.append({
                    "question": question,
                    "answer": qa_result.get("answer", ""),
                    "success": qa_result["success"]
                })
                print(f"   Q: {question}")
                print(f"   A: {qa_result.get('answer', '')[:50]}...")
            result["steps"]["qa"] = {"results": qa_results}
        else:
            print("⏭️  步骤 4: 跳过文档问答（无问题或服务不可用）")

        # 步骤 5：生成摘要
        print("📄 步骤 5: 生成摘要...")
        if "chat_ocr" in self.services:
            summary_result = self.services["chat_ocr"].generate_summary(image_path, max_length=300)
            result["steps"]["summary"] = summary_result
            if summary_result["success"]:
                print(f"   ✅ 摘要: {summary_result['summary'][:100]}...")
        else:
            print("   ⚠️ ChatOCR 服务不可用")

        result["success"] = True
        result["end_time"] = datetime.now().isoformat()

        # 记录工作流结束
        if self.logger:
            self.logger.log_workflow_end(result, True)
            self.logger.save_session()

        print("\n✅ 文档理解工作流完成\n")
        return result

    def run_table_extraction_workflow(
        self,
        image_path: str,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        运行表格提取工作流

        流程：表格检测 → 表格识别 → 数据提取 → 格式转换 → 导出

        参数：
            image_path: 表格图像路径
            output_format: 输出格式（html/json/csv）

        返回：
            工作流执行结果
        """
        print(f"\n🚀 开始表格提取工作流: {image_path}")

        result = {
            "workflow": "table_extraction",
            "image_path": image_path,
            "output_format": output_format,
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }

        # 步骤 1：表格检测
        print("🔍 步骤 1: 表格检测...")
        if "ocr" in self.services:
            table_result = self.services["ocr"].extract_table(image_path)
            result["steps"]["detect"] = table_result
            if not table_result["success"]:
                result["error"] = "表格检测失败"
                result["end_time"] = datetime.now().isoformat()
                return result
            print(f"   ✅ 检测到 {table_result['table_count']} 个表格")
        else:
            print("   ⚠️ OCR 服务不可用")
            result["error"] = "OCR 服务不可用"
            result["end_time"] = datetime.now().isoformat()
            return result

        # 步骤 2：数据提取
        print("📊 步骤 2: 数据提取...")
        tables = table_result["tables"]
        print(f"   ✅ 提取到 {len(tables)} 个表格数据")

        # 步骤 3：格式转换
        print("🔄 步骤 3: 格式转换...")
        if output_format == "html":
            output_data = [table.get("html", "") for table in tables]
        elif output_format == "json":
            output_data = [{"rows": table["rows"]} for table in tables]
        elif output_format == "csv":
            output_data = "\n\n".join(
                ["\n".join([",".join(row) for row in table["rows"]]) for table in tables]
            )
        else:
            output_data = str(tables)
        print(f"   ✅ 转换为 {output_format} 格式")

        result["steps"]["extract"] = {"tables": tables}
        result["steps"]["format"] = {"format": output_format}
        result["output"] = output_data
        result["success"] = True
        result["end_time"] = datetime.now().isoformat()

        print("\n✅ 表格提取工作流完成\n")
        return result

    def run_web_scraping_workflow(
        self,
        url: str,
        extract_type: str = "text",
        actions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        运行网页抓取工作流

        流程：浏览器导航 → 页面交互（可选）→ 截图 → OCR 识别 → 内容提取 → 分析

        参数：
            url: 网页 URL
            extract_type: 提取类型（text/table/image）
            actions: 页面交互操作列表（可选）
                [{"type": "click", "selector": "#button"}, {"type": "input", "selector": "#input", "text": "value"}]

        返回：
            工作流执行结果
        """
        print(f"\n🚀 开始网页抓取工作流: {url}")

        result = {
            "workflow": "web_scraping",
            "url": url,
            "extract_type": extract_type,
            "start_time": datetime.now().isoformat(),
            "steps": {},
            "success": False
        }

        # 尝试导入浏览器管理模块
        try:
            from playwright_manager import PlaywrightManager
            from browser_wrapper import BrowserWrapper
            BROWSER_AVAILABLE = True
        except ImportError:
            BROWSER_AVAILABLE = False

        if not BROWSER_AVAILABLE:
            print("⚠️ 浏览器管理模块未安装，请运行: pip install playwright && playwright install chromium")
            result["error"] = "浏览器管理模块未安装"
            result["end_time"] = datetime.now().isoformat()
            return result

        try:
            # 步骤 1：启动浏览器（使用改进的 AsyncPlaywrightBrowser）
            print("🌐 步骤 1: 启动浏览器...")
            playwright_cli = AsyncPlaywrightBrowser(
                headless=True,
                browser_type="chromium",
                timeout=30000
            )
            await playwright_cli.start()
            result["steps"]["create_browser"] = {"success": True}

            # 步骤 2：导航到网页
            print("📍 步骤 2: 导航到网页...")
            await playwright_cli.goto(
                url,
                wait_until="networkidle",
                timeout=30000
            )
            result["steps"]["navigate"] = {"success": True}

            # 步骤 3：等待页面加载完成
            print("⏳ 步骤 3: 等待页面加载...")
            await playwright_cli.wait_for_load_state("domcontentloaded")
            result["steps"]["wait_load"] = {"success": True}

            # 步骤 4：页面交互（可选）
            if actions:
                print("🖱️  步骤 4: 页面交互...")
                interaction_results = []
                for action in actions:
                    action_type = action.get("type")
                    selector = action.get("selector")

                    if action_type == "click":
                        await playwright_cli.click(selector)
                        act_result = {"success": True}
                    elif action_type == "input":
                        text = action.get("text", "")
                        await playwright_cli.fill(selector, text)
                        act_result = {"success": True}
                    elif action_type == "scroll":
                        distance = action.get("distance", 500)
                        await playwright_cli.scroll_down(distance)
                        act_result = {"success": True}
                    elif action_type == "wait":
                        await playwright_cli.wait_for_selector(selector)
                        act_result = {"success": True}
                    else:
                        act_result = {"success": False, "error": f"不支持的操作类型: {action_type}"}

                    interaction_results.append({
                        "action": action,
                        "result": act_result
                    })
                    print(f"   操作 {action_type}: {'成功' if act_result['success'] else '失败'}")

                result["steps"]["interactions"] = {"results": interaction_results}

            # 步骤 5：滚动页面以触发懒加载
            print("📜 步骤 5: 滚动页面...")
            for _ in range(3):  # 滚动 3 次
                await playwright_cli.scroll_down(500)
                await asyncio.sleep(1)  # 等待 1 秒
            result["steps"]["scroll"] = {"success": True}

            # 步骤 6：截图
            print("📸 步骤 6: 截图...")
            screenshot_path = f"./screenshots/web_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path("./screenshots").mkdir(parents=True, exist_ok=True)
            await playwright_cli.screenshot(screenshot_path, full_page=True)
            result["steps"]["screenshot"] = {"success": True, "path": screenshot_path}
            print(f"   ✅ 截图已保存: {screenshot_path}")

            # 步骤 7：OCR 识别
            print("🔍 步骤 7: OCR 识别...")
            if "ocr" in self.services:
                ocr_result = self.services["ocr"].recognize_image(screenshot_path)
                result["steps"]["ocr"] = ocr_result
                if not ocr_result["success"]:
                    raise Exception(f"OCR 识别失败: {ocr_result.get('error')}")
                print(f"   ✅ 识别到 {len(ocr_result['texts'])} 行文本")
            else:
                print("   ⚠️ OCR 服务不可用")
                result["steps"]["ocr"] = {"success": False, "error": "OCR 服务不可用"}

            # 步骤 8：内容提取
            print("📄 步骤 8: 内容提取...")
            if extract_type == "text" and "ocr" in self.services:
                # 文本内容
                content = ocr_result.get("text", "")
                print(f"   ✅ 提取文本: {content[:100]}...")
            elif extract_type == "table" and "ocr" in self.services:
                # 表格提取
                table_result = self.services["ocr"].extract_table(screenshot_path)
                result["steps"]["table"] = table_result
                if table_result["success"]:
                    content = table_result
                    print(f"   ✅ 提取到 {table_result['table_count']} 个表格")
                else:
                    content = {}
            else:
                content = {}

            result["extracted_content"] = content

            # 步骤 9：关闭浏览器
            print("🔒 步骤 9: 关闭浏览器...")
            await playwright_cli.close()
            result["steps"]["close_browser"] = {"success": True}

            result["success"] = True
            result["end_time"] = datetime.now().isoformat()

            print("\n✅ 网页抓取工作流完成\n")
            return result
                    elif action_type == "scroll":
                        distance = action.get("distance", 500)
                        act_result = bw.scroll(distance)
                    else:
                        act_result = {"success": False, "error": f"不支持的操作类型: {action_type}"}

                    interaction_results.append({
                        "action": action,
                        "result": act_result
                    })
                    print(f"   操作 {action_type}: {'成功' if act_result['success'] else '失败'}")

                result["steps"]["interactions"] = {"results": interaction_results}

            # 步骤 4：截图
            print("📸 步骤 4: 截图...")
            screenshot_path = f"./screenshots/web_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Path("./screenshots").mkdir(parents=True, exist_ok=True)
            screenshot_result = pm.screenshot(screenshot_path)
            result["steps"]["screenshot"] = screenshot_result
            if not screenshot_result["success"]:
                raise Exception(f"截图失败: {screenshot_result.get('error')}")
            print(f"   ✅ 截图已保存: {screenshot_path}")

            # 步骤 5：OCR 识别
            print("🔍 步骤 5: OCR 识别...")
            if "ocr" in self.services:
                ocr_result = self.services["ocr"].recognize_image(screenshot_path)
                result["steps"]["ocr"] = ocr_result
                if not ocr_result["success"]:
                    raise Exception(f"OCR 识别失败: {ocr_result.get('error')}")
                print(f"   ✅ 识别到 {len(ocr_result['texts'])} 行文本")
            else:
                print("   ⚠️ OCR 服务不可用")
                result["steps"]["ocr"] = {"success": False, "error": "OCR 服务不可用"}

            # 步骤 6：内容提取
            print("📄 步骤 6: 内容提取...")
            if extract_type == "text" and "ocr" in self.services:
                # 文本内容
                content = ocr_result.get("text", "")
                print(f"   ✅ 提取文本: {content[:100]}...")
            elif extract_type == "table" and "ocr" in self.services:
                # 表格提取
                table_result = self.services["ocr"].extract_table(screenshot_path)
                result["steps"]["table"] = table_result
                if table_result["success"]:
                    content = table_result
                    print(f"   ✅ 提取到 {table_result['table_count']} 个表格")
                else:
                    content = {}
            else:
                content = {}

            result["extracted_content"] = content

            # 步骤 7：关闭浏览器
            print("🔒 步骤 7: 关闭浏览器...")
            pm.close_browser()
            result["steps"]["close_browser"] = {"success": True}

            result["success"] = True
            result["end_time"] = datetime.now().isoformat()

            print("\n✅ 网页抓取工作流完成\n")
            return result

        except Exception as e:
            print(f"\n❌ 网页抓取工作流失败: {str(e)}\n")
            result["error"] = str(e)
            result["end_time"] = datetime.now().isoformat()

            # 尝试关闭浏览器
            try:
                if 'pm' in locals():
                    pm.close_browser()
            except:
                pass

            return result


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="复杂文档和网页理解工作流引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 文档理解工作流：
  python workflow_engine.py document-understanding document.png

2. 文档理解工作流（带问答）：
  python workflow_engine.py document-understanding document.png --questions "发票金额是多少?" "开票日期?"

3. 表格提取工作流：
  python workflow_engine.py table-extraction table.png --format html

4. 网页抓取工作流：
  python workflow_engine.py web-scraping https://example.com --type text
        """
    )

    parser.add_argument(
        "workflow",
        choices=["document-understanding", "table-extraction", "web-scraping"],
        help="工作流类型"
    )

    parser.add_argument(
        "input",
        help="输入路径（图像路径或 URL）"
    )

    parser.add_argument(
        "--format",
        default="html",
        choices=["html", "json", "csv"],
        help="输出格式（仅用于 table-extraction）"
    )

    parser.add_argument(
        "--questions",
        nargs="+",
        help="文档问答问题列表（仅用于 document-understanding）"
    )

    parser.add_argument(
        "--type",
        default="text",
        choices=["text", "table", "image"],
        help="提取类型（仅用于 web-scraping）"
    )

    parser.add_argument(
        "--gpu",
        action="store_true",
        help="使用 GPU（默认自动检测）"
    )

    parser.add_argument(
        "--no-logging",
        action="store_true",
        help="禁用日志记录"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON 格式输出"
    )

    args = parser.parse_args()

    # 初始化工作流引擎
    try:
        engine = WorkflowEngine(use_gpu=args.gpu if args.gpu else None, enable_logging=not args.no_logging)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

    # 执行工作流
    result = None

    if args.workflow == "document-understanding":
        result = engine.run_document_understanding_workflow(args.input, args.questions)

    elif args.workflow == "table-extraction":
        result = engine.run_table_extraction_workflow(args.input, args.format)

    elif args.workflow == "web-scraping":
        result = engine.run_web_scraping_workflow(args.input, args.type)

    # 输出结果
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
