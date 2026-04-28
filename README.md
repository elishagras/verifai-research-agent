# VerifAI

Autonomous competitive intelligence research agent with transparent confidence scoring and contradiction detection.

## Features
- Multi-step iterative research with gap detection
- Source triangulation confidence scoring (High/Medium/Low)
- Contradiction detection between sources
- Source quality ratings (⭐⭐⭐ High / ⭐⭐ Medium / ⭐ Low)
- Dual research modes: Deep (iterative) and Broad (parallel)

## How It Works
1. User asks a research question
2. Agent searches the web using Tavily API
3. Analyzes results and identifies knowledge gaps
4. Reformulates queries to fill gaps (iterative mode)
5. Generates structured report with confidence scores
6. Flags contradictions between sources
7. Rates source credibility

## Tech Stack
- Python
- Claude AI (Anthropic) - reasoning and synthesis
- Tavily Search API - web retrieval
- Streamlit - user interface

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
streamlit run app.py
```

## Project Structure
- `agent.py` - Core research loop and gap detection
- `confidence.py` - Source triangulation scoring
- `contradiction.py` - Cross-source disagreement detection
- `source_quality.py` - Domain-based credibility ratings
- `app.py` - Streamlit web interface

## Acknowledgments
Built with assistance from Claude AI (Anthropic) for code implementation and technical architecture design.

---

**Author:** Elisha Gras  
**Course:** AI for Engineering Managers Final Project  
**Date:** April 2026
