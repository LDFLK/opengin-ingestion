---
sidebar_position: 1
---

# Architecture Overview

OpenGIN Tracer is built on a **Multi-Agent System** architecture. This design separates concerns into distinct "Agents" that handle specific stages of the pipeline.

## High-Level Workflow

The pipeline follows a linear progression:

![Architecture Diagram](/img/architecture_diagram.jpeg)

## The Agents

The system comprises four main agents:

1.  **Agent 0 (Orchestrator)**: The master controller. It initiates pipelines, manages the file system, and coordinates the hand-offs between other agents.
2.  **Agent 1 (Scanner)**: The ingestion layer. It splits the PDF document into individual pages and sends them to the GenAI model for extraction.
3.  **Agent 2 (Aggregator)**: The consolidation layer. It takes the individual page results and combines them into cohesive datasets.
4.  **Agent 3 (Exporter)**: The output layer. It formats the aggregated data into the desired output format (e.g., flattened JSON, CSV).

For more details on each agent, see the [Agents](agents) page.
