---
sidebar_position: 1
---

# Introduction

Welcome to the documentation for **OpenGIN Tracer**.

OpenGIN Tracer is an advanced data extraction pipeline designed to process PDF documents and extract structured table data using Generative AI (Gemini).

## What is OpenGIN Tracer?

OpenGIN Tracer automates the tedious task of manually copying data from PDF tables. It leverages a multi-agent architecture to:

1.  **Scan** PDFs and split them into manageable pages.
2.  **Extract** data from each page using Gemini 1.5 Flash.
3.  **Aggregate** the extracted data across all pages.
4.  **Export** the final results into structured formats like JSON or CSV.

## Key Features

- **GenAI-Powered Extraction**: Uses state-of-the-art LLMs to understand complex table structures.
- **Multi-Agent Architecture**: Modular design for better scalability and maintenance.
- **Automated Workflow**: End-to-end automation from PDF input to structured output.
- **Extensible**: easy to add new agents or extraction logic.

## Getting Started

Check out the [Usage](usage/cli) section to get started with the CLI, or explore the [Architecture](architecture/overview) to understand how it works under the hood.
