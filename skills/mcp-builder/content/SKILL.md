---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
---

# MCP Server Development Guide

Create MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools.

## High-Level Workflow

Creating a high-quality MCP server involves four main phases:

### Phase 1: Deep Research and Planning

1. **API Coverage vs. Workflow Tools**
   - Balance comprehensive API endpoint coverage with specialized workflow tools
   - When uncertain, prioritize comprehensive API coverage

2. **Tool Naming and Discoverability**
   - Use consistent prefixes (e.g., `github_create_issue`, `github_list_repos`)
   - Use action-oriented naming

3. **Context Management**
   - Design tools that return focused, relevant data
   - Support pagination where applicable

4. **Actionable Error Messages**
   - Error messages should guide agents toward solutions

### Phase 2: Implementation

#### Project Structure

**TypeScript (Recommended):**
- Use `@modelcontextprotocol/sdk`
- Streamable HTTP for remote servers
- stdio for local servers

**Python:**
- Use `mcp` package
- FastMCP for simplified development

#### Core Infrastructure

Create shared utilities:
- API client with authentication
- Error handling helpers
- Response formatting
- Pagination support

#### Implementing Tools

**Input Schema:**
- Use Zod (TypeScript) or Pydantic (Python)
- Include constraints and clear descriptions

**Tool Description:**
- Concise summary of functionality
- Parameter descriptions
- Return type schema

**Implementation:**
- Async/await for I/O operations
- Proper error handling
- Support pagination

### Phase 3: Testing

1. Test each tool individually
2. Test tool combinations
3. Verify error handling
4. Check performance

### Phase 4: Documentation

- Clear README with installation
- Usage examples
- API reference
- Authentication instructions

## Resources

- MCP Specification: https://modelcontextprotocol.io
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
