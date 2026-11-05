#!/usr/bin/env node
"use strict";

// Small, credential-free bridge for helper scripts. The Connector owns auth,
// endpoint selection, and the exact tool schema; callers must pass a tool name
// returned by `mcode-tools connector tools`.
const { execFileSync } = require("node:child_process");

function assertToolName(toolName) {
  if (typeof toolName !== "string" || !/^connector__tencentdocs__[A-Za-z0-9][A-Za-z0-9_.-]*$/.test(toolName)) {
    throw new Error("必须传入工具发现结果中的完整 tencentdocs Connector 工具名");
  }
}

function assertSuccess(result) {
  if (!result || typeof result !== "object" || Array.isArray(result)) return;
  const failedCode = ["code", "errcode", "error_code", "retcode", "ret", "errno"].find((key) => {
    if (!(key in result) || result[key] === null) return false;
    return !["0", "200", "ok", "success"].includes(String(result[key]).toLowerCase());
  });
  const hasError = ["error", "err_msg"].some((key) => result[key] !== undefined && result[key] !== null && result[key] !== false && result[key] !== "" && result[key] !== 0);
  if (result.isError === true || result.success === false || hasError || failedCode || /^(error|failed|failure|denied)$/i.test(String(result.status || ""))) {
    const detail = result.message || result.msg || result.err_msg || result.error_description || result.error || (failedCode ? `${failedCode}=${result[failedCode]}` : "工具返回失败状态");
    throw new Error(`Connector 调用失败: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
  }
}

// Normalize the JSON result or standard tool-result envelope. Never turn an
// unreadable/failed response into an empty business object.
function parseConnectorResult(output) {
  let result;
  try { result = typeof output === "string" ? JSON.parse(output) : output; }
  catch { throw new Error("Connector 未返回有效 JSON，请检查工具调用结果"); }
  for (let depth = 0; depth < 8; depth += 1) {
    if (result === null || typeof result !== "object") throw new Error("Connector 返回值必须是 JSON 对象或数组");
    assertSuccess(result);
    if (result.structuredContent && typeof result.structuredContent === "object") {
      result = result.structuredContent;
      continue;
    }
    if (Array.isArray(result.content) && result.content.every((item) => item && typeof item.type === "string")) {
      const text = result.content.filter((item) => item.type === "text").map((item) => item.text).join("\n");
      try { result = JSON.parse(text); }
      catch { throw new Error("Connector 工具结果中缺少有效 JSON 内容"); }
      continue;
    }
    if (result.data && typeof result.data === "object" && ["code", "errcode", "error_code", "retcode", "ret", "success", "status"].some((key) => key in result)) {
      result = result.data;
      continue;
    }
    return result;
  }
  throw new Error("Connector 返回结果嵌套过深");
}

function callConnector(toolName, args) {
  assertToolName(toolName);
  if (!args || typeof args !== "object" || Array.isArray(args)) throw new Error("Connector 参数必须为 JSON 对象");
  const output = execFileSync(
    "mcode-tools",
    ["connector", "call", toolName, "--args-file", "-"],
    { encoding: "utf8", input: JSON.stringify(args), stdio: ["pipe", "pipe", "pipe"], timeout: 120000, maxBuffer: 16 * 1024 * 1024 },
  );
  parseConnectorResult(output);
  return output.trim();
}

module.exports = { assertToolName, callConnector, parseConnectorResult };
