# LLM Eval Dashboard

React frontend for visualizing LLM evaluation runs.

## Prerequisites

- Node.js 18+
- API server running (see below)

## Setup

```bash
npm install
```

## Development

Start the dev server:

```bash
npm run dev
```

Opens at http://localhost:5173

## API Server

The frontend connects to the FastAPI backend at `http://localhost:8000`. Start it from the project root:

```bash
uv run uvicorn src.api.server:app --reload
```

## Features

- **Run List** - View all evaluation runs with pass/fail counts
- **Run Detail** - Click a run to inspect individual test results, prompts, and responses

## Build

```bash
npm run build
```

Output goes to `dist/`.
