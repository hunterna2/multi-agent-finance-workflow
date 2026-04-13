# Multi-Agent Financial Analysis Workflow

A stateful multi-agent system built with **LangGraph** + Azure OpenAI that simulates a full finance team (Researcher, Analyst, Compliance Officer, and Executive Reporter).

Give the system one natural-language prompt (e.g. “Analyze Q1 loan trends and check for compliance risks”) and it automatically routes the task through the four specialized agents, gathers data, runs analysis, checks regulatory rules, and delivers a polished executive report.

## Features
- 4 collaborating specialized agents
- Tool calling for market data and compliance checks
- Linear orchestration with LangGraph
- Professional banking-style executive reports with clear sections
- Built for easy extension and Azure deployment

## Quick Start

1. Copy the example config:
   ```bash
   cp .env.example .env