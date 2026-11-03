#!/usr/bin/env python3
"""
OpenClaw + RunningHub Connection Helper

This script provides utilities for:
1. Connecting to RunningHub with API key
2. Testing the connection
3. Listing available nodes
4. Creating workflows from templates
"""

import argparse
import json
import os
import sys
import subprocess
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


@dataclass
class ConnectionConfig:
    api_key: str
    base_url: str = "https://api.runninghub.com"
    timeout: int = 30


class RunningHubClient:
    """Client for interacting with RunningHub API"""

    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to RunningHub API"""
        url = f"{self.config.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                timeout=self.config.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        result = self._request("GET", "/api/v1/user/profile")
        if result.get("success"):
            print(f"✓ Connected successfully!")
            print(f"  User: {result.get('data', {}).get('name', 'N/A')}")
            return True
        else:
            print(f"✗ Connection failed: {result.get('error', 'Unknown error')}")
            return False

    def get_nodes(self) -> List[Dict[str, Any]]:
        """Get list of available node types"""
        result = self._request("GET", "/api/v1/nodes")
        if result.get("success"):
            return result.get("data", {}).get("nodes", [])
        return []

    def list_workflows(self, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """List all workflows"""
        result = self._request("GET", f"/api/v1/workflows?page={page}&limit={limit}")
        if result.get("success"):
            return result.get("data", {}).get("workflows", [])
        return []

    def create_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """Create a new workflow and return its ID"""
        result = self._request("POST", "/api/v1/workflows", json=workflow)
        if result.get("success"):
            wf_id = result.get("data", {}).get("workflow", {}).get("id")
            print(f"✓ Workflow created: {wf_id}")
            return wf_id
        else:
            print(f"✗ Failed to create workflow: {result.get('error')}")
            return None

    def run_workflow(self, workflow_id: str, inputs: Dict[str, Any] = None) -> Optional[str]:
        """Run a workflow and return the run ID"""
        payload = {"inputs": inputs or {}, "async": True}
        result = self._request("POST", f"/api/v1/workflows/{workflow_id}/run", json=payload)
        if result.get("success"):
            run_id = result.get("data", {}).get("run_id")
            print(f"✓ Workflow started: {run_id}")
            return run_id
        else:
            print(f"✗ Failed to run workflow: {result.get('error')}")
            return None

    def get_workflow_status(self, workflow_id: str, run_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        return self._request("GET", f"/api/v1/workflows/{workflow_id}/runs/{run_id}")


class OpenClawHelper:
    """Helper for OpenClaw CLI operations"""

    @staticmethod
    def check_installed() -> bool:
        """Check if OpenClaw is installed"""
        try:
            result = subprocess.run(
                ["openclaw", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ OpenClaw is installed: {result.stdout.strip()}")
                return True
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        print("✗ OpenClaw is not installed")
        return False

    @staticmethod
    def connect_runninghub(api_key: str) -> bool:
        """Connect OpenClaw to RunningHub"""
        try:
            result = subprocess.run(
                ["openclaw", "runninghub", "connect", "--api-key", api_key],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"✓ Connected to RunningHub via OpenClaw")
                return True
            else:
                print(f"✗ Failed to connect: {result.stderr}")
                return False
        except subprocess.SubprocessError as e:
            print(f"✗ Connection error: {e}")
            return False

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Get OpenClaw connection status"""
        try:
            result = subprocess.run(
                ["openclaw", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return {"connected": False}

    @staticmethod
    def list_nodes() -> List[Dict[str, Any]]:
        """List available RunningHub nodes via OpenClaw"""
        try:
            result = subprocess.run(
                ["openclaw", "runninghub", "nodes", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return []


class WorkflowBuilder:
    """Builder for creating workflow configurations"""

    def __init__(self):
        self.workflow = {
            "name": "",
            "description": "",
            "nodes": [],
            "connections": []
        }
        self.node_counter = 0

    def set_basic_info(self, name: str, description: str = "") -> "WorkflowBuilder":
        self.workflow["name"] = name
        self.workflow["description"] = description
        return self

    def add_trigger(self, trigger_type: str = "manual", config: Dict = None) -> str:
        """Add a trigger node and return its ID"""
        self.node_counter += 1
        node_id = f"trigger_{self.node_counter}"
        node = {
            "id": node_id,
            "type": "trigger",
            "name": "触发器",
            "config": {
                "trigger_type": trigger_type,
                **(config or {})
            }
        }
        self.workflow["nodes"].append(node)
        return node_id

    def add_llm(self, node_id: str, model: str, prompt: str,
                system_prompt: str = "", config: Dict = None) -> str:
        """Add an LLM node"""
        self.node_counter += 1
        llm_id = f"llm_{self.node_counter}"
        node = {
            "id": llm_id,
            "type": "llm",
            "name": "大语言模型",
            "config": {
                "model": model,
                "prompt": prompt,
                "system_prompt": system_prompt,
                **(config or {})
            }
        }
        self.workflow["nodes"].append(node)
        self.workflow["connections"].append({"from": node_id, "to": llm_id})
        return llm_id

    def add_image_node(self, node_id: str, model: str, prompt: str,
                       config: Dict = None) -> str:
        """Add an image generation node"""
        self.node_counter += 1
        image_id = f"image_{self.node_counter}"
        node = {
            "id": image_id,
            "type": "image",
            "name": "图像生成",
            "config": {
                "model": model,
                "prompt": prompt,
                **(config or {})
            }
        }
        self.workflow["nodes"].append(node)
        self.workflow["connections"].append({"from": node_id, "to": image_id})
        return image_id

    def add_output(self, node_id: str, output_type: str = "json",
                   fields: List[Dict] = None) -> str:
        """Add an output node"""
        self.node_counter += 1
        output_id = f"output_{self.node_counter}"
        node = {
            "id": output_id,
            "type": "output",
            "name": "输出",
            "config": {
                "format": output_type,
                "fields": fields or []
            }
        }
        self.workflow["nodes"].append(node)
        self.workflow["connections"].append({"from": node_id, "to": output_id})
        return output_id

    def build(self) -> Dict[str, Any]:
        """Build and return the workflow configuration"""
        return self.workflow.copy()


def parse_workflow_description(description: str) -> Dict[str, Any]:
    """
    Parse natural language workflow description into a workflow config.
    This is a simplified parser - in production, you might use an LLM for this.
    """
    description = description.lower()

    workflow = WorkflowBuilder()

    # Simple keyword-based detection
    if any(word in description for word in ["图像", "图片", "image", "生成"]):
        # Text to image workflow
        workflow.set_basic_info("文本到图像生成", "自动从文本生成图像")

        trigger_id = workflow.add_trigger("manual", {
            "inputs": [{"name": "topic", "type": "string", "label": "主题"}]
        })

        llm_id = workflow.add_llm(
            trigger_id,
            "gpt-4",
            "为主题「{{trigger_1.inputs.topic}}」生成图像提示词",
            "你是图像提示词优化专家"
        )

        image_id = workflow.add_image_node(
            llm_id,
            "dall-e-3",
            "{{llm_1.output}}",
            {"size": "1024x1024", "quality": "hd"}
        )

        workflow.add_output(image_id, "json", [
            {"source": "llm_1.output", "label": "提示词"},
            {"source": "image_1.output.image_url", "label": "图像"}
        ])

    elif any(word in description for word in ["聊天", "对话", "chat", "assistant"]):
        # Chatbot workflow
        workflow.set_basic_info("AI 对话助手", "具有上下文记忆的对话机器人")

        trigger_id = workflow.add_trigger("webhook", {
            "inputs": [
                {"name": "session_id", "type": "string"},
                {"name": "message", "type": "string"}
            ]
        })

        llm_id = workflow.add_llm(
            trigger_id,
            "gpt-4",
            "{{trigger_1.inputs.message}}",
            "你是一个专业友好的AI助手"
        )

        workflow.add_output(llm_id, "json", [
            {"source": "llm_1.output", "label": "response"}
        ])

    elif any(word in description for word in ["批量", "batch", "多个"]):
        # Batch processing workflow
        workflow.set_basic_info("批量内容处理", "批量处理多条数据")

        trigger_id = workflow.add_trigger("webhook", {
            "inputs": [{"name": "items", "type": "array"}]
        })

        llm_id = workflow.add_llm(
            trigger_id,
            "gpt-4",
            "分析并处理：{{loop_1.current_item}}",
            "你是数据处理专家"
        )

        workflow.add_output(llm_id, "json")

    else:
        # Default simple workflow
        workflow.set_basic_info("AI 处理工作流", "简单 AI 处理流程")

        trigger_id = workflow.add_trigger("manual")

        workflow.add_llm(
            trigger_id,
            "gpt-4",
            "{{trigger_1.inputs.topic}}",
            "你是专业助手"
        )

    return workflow.build()


def main():
    parser = argparse.ArgumentParser(description="OpenClaw + RunningHub Connection Helper")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to RunningHub")
    connect_parser.add_argument("--api-key", required=True, help="RunningHub API Key")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test connection")
    test_parser.add_argument("--api-key", required=True, help="RunningHub API Key")

    # Nodes command
    nodes_parser = subparsers.add_parser("nodes", help="List available nodes")
    nodes_parser.add_argument("--api-key", help="RunningHub API Key (optional if using OpenClaw)")

    # Build workflow command
    build_parser = subparsers.add_parser("build", help="Build workflow from description")
    build_parser.add_argument("--description", required=True, help="Workflow description")
    build_parser.add_argument("--output", help="Output file path")

    # Create workflow command
    create_parser = subparsers.add_parser("create", help="Create a workflow")
    create_parser.add_argument("--api-key", required=True, help="RunningHub API Key")
    create_parser.add_argument("--file", help="Workflow JSON file")

    args = parser.parse_args()

    if args.command == "connect":
        print("Connecting to RunningHub...")
        if OpenClawHelper.check_installed():
            success = OpenClawHelper.connect_runninghub(args.api_key)
            sys.exit(0 if success else 1)
        else:
            print("OpenClaw not found. Using direct API connection...")
            client = RunningHubClient(ConnectionConfig(args.api_key))
            success = client.test_connection()
            sys.exit(0 if success else 1)

    elif args.command == "test":
        print("Testing connection...")
        client = RunningHubClient(ConnectionConfig(args.api_key))
        success = client.test_connection()
        sys.exit(0 if success else 1)

    elif args.command == "nodes":
        print("Fetching available nodes...")
        if args.api_key:
            client = RunningHubClient(ConnectionConfig(args.api_key))
            nodes = client.get_nodes()
        elif OpenClawHelper.check_installed():
            nodes = OpenClawHelper.list_nodes()
        else:
            print("Error: API key required for direct connection")
            sys.exit(1)

        if nodes:
            print(f"\nAvailable {len(nodes)} node types:")
            for node in nodes:
                print(f"  - {node.get('type')}: {node.get('name', 'N/A')}")
        else:
            print("No nodes found")

    elif args.command == "build":
        print("Building workflow from description...")
        workflow = parse_workflow_description(args.description)
        print(json.dumps(workflow, indent=2, ensure_ascii=False))

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(workflow, f, indent=2, ensure_ascii=False)
            print(f"\nWorkflow saved to: {args.output}")

    elif args.command == "create":
        print("Creating workflow...")
        if not args.file:
            print("Error: --file required")
            sys.exit(1)

        with open(args.file, "r", encoding="utf-8") as f:
            workflow_data = json.load(f)

        client = RunningHubClient(ConnectionConfig(args.api_key))
        wf_id = client.create_workflow(workflow_data)
        sys.exit(0 if wf_id else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
