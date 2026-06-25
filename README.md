<div align="center">

# CodeAnalysis AI

**Autonomous Python code quality analysis and refactoring engine**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-AST%20Powered-8b5cf6?style=flat-square)]()

Analyzes Python codebases using **Abstract Syntax Trees**, **graph theory**, and **software science metrics** — then autonomously refactors what it finds.

[Features](#features) · [Demo](#demo) · [Installation](#installation) · [How It Works](#how-it-works) · [Architecture](#architecture)

</div>

---

## What Is This?

Most code quality tools tell you *that* your code has problems. CodeAnalysis AI tells you *where*, *why*, and then **fixes it**.

Point it at any `.py` file or project folder. It will:

1. Calculate **Cyclomatic Complexity**, **Halstead metrics**, and **Maintainability Index** for every function
2. Build a **dependency graph** and detect circular dependencies, God Objects, and critical bridges using betweenness centrality
3. Generate **architectural critiques** ranked by severity
4. **Refactor the code** via AST transformations — guard clauses, docstring injection, PEP8 formatting
5. **Extract God Classes** into separate component files automatically
6. Write a **full README** and module documentation for the project

No external API calls. No cloud services. Runs entirely on your machine.

---

## Features

### Code Metrics Engine
- **Cyclomatic Complexity** (McCabe) — per-function, with spaghetti detection at CC > 15
- **Halstead Software Science** — effort, volume, estimated bug count
- **Maintainability Index** — 0–100 score combining all metrics
- **Lines of Code** breakdown — logical, physical, comment, blank
- **17-dimensional feature vector** for ML model prediction

### Architecture X-Ray
- Parses all `import` statements and builds a directed dependency graph with NetworkX
- Detects **circular dependencies** — every cycle flagged as an architectural violation
- Calculates **betweenness centrality** to find critical hub modules
- Applies **Martin's Instability Metric** (afferent / efferent coupling) to each module
- Classifies each module: God Object, Critical Bridge, Fragile, or Healthy
- Exports a **colored PNG** architecture diagram and **Mermaid.js** graph

### Autonomous Refactoring (AST-based)
- **Guard Clause Transformer** — converts nested if-else chains to early returns, reducing CC
- **Docstring Injector** — detects undocumented functions and injects structured templates
- **Magic Number Detector** — flags numeric literals that should be named constants
- **PEP8 Formatter** — runs autopep8 after AST transformations
- Creates a **timestamped backup** before any change; shows before/after diff

### God Class Extractor
- Detects classes exceeding the method threshold (default: 10)
- **Splits them into separate `bilesen_*.py` files** automatically
- Rewrites the original file with proper imports

### Project Documenter
- Scans an entire project folder recursively
- Generates a **full README.md** with module tables, complexity scores, and Mermaid diagrams
- Flags spaghetti functions inline in the documentation

---

## Demo

> Screenshot / GIF goes here — run the app and record a demo

```
streamlit run app.py
```

The web UI opens at `http://localhost:8501`. Drop in a file path or a project folder and hit Analyze.

---

## Installation

**Requirements:** Python 3.9+

```bash
git clone https://github.com/your-username/codeanalysis-ai.git
cd codeanalysis-ai
pip install -r requirements.txt
streamlit run app.py
```

### requirements.txt

```
streamlit>=1.40.0
radon>=6.0.1
networkx>=3.4.0
matplotlib>=3.9.0
autopep8>=2.3.1
joblib>=1.4.2
scikit-learn>=1.5.0
```

---

## How It Works

### Analysis Pipeline

```
Your .py file or project folder
         │
         ▼
┌─────────────────────┐
│   Code Scanner      │  radon + ast stdlib
│                     │  CC, Halstead, LOC,
│                     │  Maintainability Index
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Architecture X-Ray │  networkx
│                     │  Dependency graph,
│                     │  cycle detection,
│                     │  betweenness centrality
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Architecture Critic│  Rule engine
│                     │  Ranked critiques:
│                     │  CRITICAL / WARNING / INFO
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────────┐
│Refactor │  │  Documenter  │
│         │  │              │
│ • Guard │  │ • README.md  │
│   clause│  │ • Mermaid    │
│ • Docs  │  │   diagrams   │
│ • PEP8  │  │ • Class/fn   │
│         │  │   tables     │
└─────────┘  └──────────────┘
```

### AST Transformation Example

The Guard Clause Transformer rewrites deeply nested code at the syntax tree level — not with regex:

```python
# BEFORE — CC: 8, nesting depth: 4
def process_order(user, cart, payment):
    if user is not None:
        if cart:
            if payment.valid:
                if cart.total > 0:
                    return execute(user, cart, payment)

# AFTER — CC: 4, nesting depth: 1
def process_order(user, cart, payment):
    if user is None:
        return
    if not cart:
        return
    if not payment.valid:
        return
    if cart.total <= 0:
        return
    return execute(user, cart, payment)
```

### Severity Levels

| Level | Condition | Meaning |
|-------|-----------|---------|
| CRITICAL | CC > 15 | Spaghetti — untestable, high bug risk |
| CRITICAL | Class methods > 10 | God Class — violates Single Responsibility |
| CRITICAL | Circular dependency detected | Architectural violation |
| WARNING | CC 10–15 | High complexity, refactoring recommended |
| WARNING | Module instability > 0.85 | Fragile — too many outgoing dependencies |
| WARNING | Nesting depth > 4 | Deep nesting — guard clauses needed |
| INFO | Functions without docstrings | Documentation gap |

### Health Score Formula

```
Health = 100
  - (circular_dependencies × 15)
  - (god_objects × 10)
  - (critical_bridges × 5)
  - (fragile_modules × 3)
```

---

## Architecture

```
codeanalysis-ai/
├── app.py                  # Streamlit web UI
├── gelismis_ajan.py        # Main agent — orchestrates the pipeline
├── kod_tarayici.py         # Metrics engine (CC, Halstead, LOC, AST)
├── mimari_rontgen.py       # Architecture graph analysis
├── oto_tamirci.py          # AST-based auto-repair
└── requirements.txt
```

### Key Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `GelismisAjan` | `gelismis_ajan.py` | Top-level orchestrator |
| `KodTarayici` | `kod_tarayici.py` | Metrics calculation + ML feature vector |
| `MimariRontgen` | `mimari_rontgen.py` | Dependency graph + architectural analysis |
| `OtoTamirci` | `oto_tamirci.py` | File backup + AST transform + PEP8 |
| `GuardClauseTransformer` | `gelismis_ajan.py` | `ast.NodeTransformer` — if-else → early return |
| `AkilliDocstringEnjektoru` | `gelismis_ajan.py` | `ast.NodeTransformer` — docstring injection |
| `KomponentAyirici` | `gelismis_ajan.py` | God Class → separate files |
| `MimariElestirmen` | `gelismis_ajan.py` | Rule engine → ranked critiques |
| `BagimlilikHaritalayici` | `gelismis_ajan.py` | Mermaid diagram generator |

---

## Metrics Reference

### Cyclomatic Complexity (McCabe)
Counts the number of independent paths through a function. Each `if`, `for`, `while`, `except`, `and`, `or` adds 1.

| CC | Risk Level |
|----|-----------|
| 1–5 | Low — simple, testable |
| 6–10 | Moderate — acceptable |
| 11–15 | High — consider refactoring |
| > 15 | Critical — spaghetti code |

### Halstead Metrics
Derived from operator and operand counts in the token stream.

- **Volume** — size of the implementation
- **Difficulty** — how hard the code is to write or understand
- **Effort** — estimated mental effort in arbitrary units
- **Estimated Bugs** — `Volume / 3000` (Halstead's empirical formula)

### Martin's Instability Metric
```
Instability = efferent_coupling / (afferent_coupling + efferent_coupling)
```
A module with instability → 1.0 depends on many others but nothing depends on it. These are the most fragile modules in the system.

---

## Roadmap

- [ ] FastAPI backend — expose analysis as a REST API
- [ ] Claude AI integration — natural language explanations via Tool Use
- [ ] PostgreSQL — persist analysis history across sessions
- [ ] Multi-language support — JavaScript/TypeScript via tree-sitter
- [ ] GitHub Actions integration — analyze PRs automatically
- [ ] VS Code extension

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built with Python's `ast` module, `radon`, `networkx`, and `streamlit`

</div>
