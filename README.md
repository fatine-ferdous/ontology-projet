# 📘 Global 50 Ontology Extraction Pipeline

This project takes **The-Global-50-2025-Eng.pdf** → extracts all text → learns S–P–O triples via spaCy+Textacy → builds an RDFLib ontology in Turtle & JSON-LD → and finally visualizes it as a graph PNG.

## 🔧 Prerequisites

- **Python** ≥ 3.7

---

## 1. Clone & Setup

```bash
# 1. Upgrade pip & install dependencies
pip install --upgrade pip setuptools wheel

# 2. Install all required Python libraries
pip install pdfplumber spacy textacy rdflib networkx matplotlib

# 3. Download spaCy English model
python -m spacy download en_core_web_sm
```

---

## 2. Step 1: Extract Text from PDF

**Script:** `extract_text.py`

```python
#!/usr/bin/env python3
# extract_text.py
# Extracts all text from a PDF using pdfplumber

```

Run it:

```bash
python extract_text.py
```

---

## 3. Step 2: Build & Visualize the Ontology

**Script:** `build_ontology.py`

```python

# build_ontology.py
# Extracts S–P–O triples, filters them, builds an RDF graph, and visualizes

```

Run the pipeline:

```bash
python extract_text.py
python build_ontology.py
```

Outputs:

- `full_text.txt`
- `ontology_manual.ttl`
- `ontology_manual.jsonld`
- `ontology_graph.png`
