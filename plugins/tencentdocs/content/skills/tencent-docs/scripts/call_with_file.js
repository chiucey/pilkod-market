#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const { callConnector } = require("./connector_call.js");

// Usage: node call_with_file.js <discovered-tool> <args.json> <field> <text|base64> <file>
// Serializes file contents directly into Connector stdin, never through the model context.
function main() {
  const [tool, argsFile, field, mode, file, ...extra] = process.argv.slice(2);
  if (!tool || !argsFile || !/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(field || "") ||
      !["text", "base64"].includes(mode) || !file || extra.length) {
    throw new Error("Usage: node call_with_file.js <discovered-tool> <args.json> <field> <text|base64> <file>");
  }
  const args = JSON.parse(fs.readFileSync(argsFile, "utf8"));
  if (args === null || typeof args !== "object" || Array.isArray(args)) throw new Error("args must be a JSON object");
  if (Object.hasOwn(args, field)) throw new Error(`args already contains ${field}; remove it before injecting file content`);
  args[field] = fs.readFileSync(file).toString(mode === "text" ? "utf8" : "base64");
  console.log(callConnector(tool, args));
}
try { main(); } catch (error) { console.error(`ERROR: ${error.message}`); process.exitCode = 1; }
