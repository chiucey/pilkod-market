---
name: abp-cli
description: ABP CLI commands - generate-proxy, install-libs, add-package-ref, new-module, install-module, update, clean, suite generate. Use when running ABP CLI commands, generating proxies, installing libraries, or using ABP Suite.
---

# ABP CLI Commands

> **Docs**: <https://abp.io/docs/latest/cli>

## Installation

```bash
# Install ABP CLI
dotnet tool install -g Volo.Abp.Cli

# Update ABP CLI
dotnet tool update -g Volo.Abp.Cli

# Check version
abp --version
```

## Generate Client Proxies

Generate type-safe client proxies from API definitions.

```bash
# Angular (host must be running)
abp generate-proxy -t ng

# C# client proxies
abp generate-proxy -t csharp -u https://localhost:44300

# Integration services only (microservices)
abp generate-proxy -t csharp -u https://localhost:44300 -st integration

# JavaScript
abp generate-proxy -t js -u https://localhost:44300

# Skip adding to module (Angular)
abp generate-proxy -t ng --skip-add-to-module

# Specify output folder
abp generate-proxy -t csharp -u https://localhost:44300 -o ./app/proxies
```

## Install Client-Side Libraries

```bash
# Install NPM packages for MVC/Blazor Server
abp install-libs

# Install in specific directory
abp install-libs -d ./ui
```

## Add Package Reference

```bash
# Add project reference with module dependency
abp add-package-ref Acme.BookStore.Domain
abp add-package-ref Acme.BookStore.Domain -t Acme.BookStore.Application

# Add NuGet package
abp add-package Volo.Abp.Caching.StackExchangeRedis

# Add package with specific module dependency
abp add-package Volo.Abp.AspNetCore.Mvc.UI.Theme.LeptonXLite -t Volo.Abp.AspNetCore.Mvc.UI.Theme.LeptonXLite.AspNetCore.Mvc
```

## Module Operations

```bash
# Create new module in solution
abp new-module Acme.OrderManagement -t module:ddd

# Create module without DDD structure
abp new-module Acme.SimpleModule

# Install published module
abp install-module Volo.Blogging

# Install module from specific NuGet source
abp install-module Volo.Blogging -s https://api.nuget.org/v3/index.json

# Create and install module in one step
abp new-module Acme.ProductManagement -t module:ddd -i
```

## Update & Clean

```bash
# Update all ABP packages
abp update

# Update to specific version
abp update --version 8.0.0

# Update only framework packages
abp update --include-framework-packages

# Clean solution (delete bin/obj folders)
abp clean

# Clean specific project
abp clean --project-path ./src/MyProject.Domain
```

## ABP Suite (CRUD Generation)

Generate CRUD pages from entity JSON (created via Suite UI):

```bash
# Generate CRUD from entity file
abp suite generate --entity .suite/entities/Book.json --solution ./Acme.BookStore.sln

# Generate with UI framework
abp suite generate --entity .suite/entities/Book.json --ui-framework mvc --solution ./Acme.BookStore.sln

# Available UI frameworks: mvc, blazor, angular, blazor-server

# Generate all entities
abp suite generate --all --solution ./Acme.BookStore.sln
```

## Create Solutions

```bash
# MVC Razor Pages
abp new BookStore -t app -u mvc

# Blazor WebAssembly
abp new BookStore -t app -u blazor

# Angular
abp new BookStore -t app -u angular

# Blazor Server
abp new BookStore -t app -u blazor-server

# Microservice Solution
abp new BookStore -t microservice

# Monolithic Layered Application
abp new BookStore -t app

# Application Module
abp new-module MyModule -t module

# Empty ASP.NET Core
abp new BookStore -t app --no-frontend
```

## Solution Templates

| Template | Command | Description |
| --- | --- | --- |
| Application | `abp new BookStore -t app` | Layered architecture |
| Microservice | `abp new BookStore -t microservice` | Distributed system |
| Module | `abp new-module MyModule` | Reusable module |
| Console | `abp new MyConsole -t console` | Console application |

## UI Framework Options

| Framework | Flag | Description |
| --- | --- | --- |
| MVC | `-u mvc` | ASP.NET Core MVC with Razor Pages |
| Blazor WASM | `-u blazor` | Blazor WebAssembly |
| Blazor Server | `-u blazor-server` | Blazor Server |
| Angular | `-u angular` | Angular SPA |
| No UI | `--no-frontend` | API only |

## Database Provider Options

```bash
# Entity Framework Core with SQL Server (default)
abp new BookStore -t app -d ef

# Entity Framework Core with PostgreSQL
abp new BookStore -t app -d ef -p npgsql

# MongoDB
abp new BookStore -t app -d mongodb
```

## Help Command

```bash
# General help
abp help

# Specific command help
abp help new
abp help generate-proxy
abp help install-module
```

## Quick Reference

| Task | Command |
| --- | --- |
| Angular proxies | `abp generate-proxy -t ng` |
| C# proxies | `abp generate-proxy -t csharp -u URL` |
| JS proxies | `abp generate-proxy -t js -u URL` |
| Install JS libs | `abp install-libs` |
| Add reference | `abp add-package-ref PackageName` |
| Add NuGet package | `abp add-package PackageName` |
| Create module | `abp new-module ModuleName` |
| Install module | `abp install-module ModuleName` |
| Update packages | `abp update` |
| Clean solution | `abp clean` |
| Suite CRUD | `abp suite generate -e entity.json -s solution.sln` |
| Get help | `abp help [command]` |
