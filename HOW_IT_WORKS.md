# How the Global 50 Ontology Extraction Pipeline Works

This document explains in simple terms how each part of the pipeline operates, from PDF to visual graph.

---

## 1. Text Extraction

1. **Goal**: Get all the textual content out of the PDF report.
2. **Tool**: `pdfplumber`, a Python library for reading PDF pages.
3. **Process**:
   - Open the PDF file.
   - Loop through each page.
   - Extract the text in reading order.
   - Combine all pages into a single `.txt` file (called `full_text.txt`).

> **Why?**  
> We need raw text so that subsequent steps can analyze natural language.

---

## 2. Triple Extraction (S–P–O)

1. **Goal**: Identify basic fact triples of the form **Subject → Predicate → Object**.
2. **Tools**:
   - **spaCy**: Splits text into sentences, tokens, and part‐of‐speech tags.
   - **Textacy**: Uses spaCy’s analysis to pull out subject‑verb‑object triples.
3. **Process**:
   - Load the cleaned text into spaCy’s language model.
   - Run the Textacy extractor to find every (subject, verb, object) in each sentence.
   - Collect thousands of raw triples (no filtering yet).

> **Why?**  
> Triples capture the simplest statements in the report, such as “Amazon is a Company” or “Climate change threatens biodiversity.”

---

## 3. Filtering & Normalization

1. **Goal**: Keep only the most meaningful relations and standardize names.
2. **Techniques**:
   - **“Is a” → rdf:type**: Every phrase like “X is a Y” becomes a class assignment.
   - **Manual allow‑list**: Only six domain‑relevant predicates are kept (e.g. `located_in`, `threatens`).
   - **Synonym mapping**: Variants like “locate”, “located in” → unified to `located_in`.
   - **Identifier cleaning**: Lowercasing, removing punctuation, spaces → underscores.

> **Why?**  
> We want a crisp, business‑ready ontology with only the facts that matter.

---

## 4. Ontology Building

1. **Goal**: Assemble filtered triples into a formal graph structure.
2. **Tool**: **RDFLib**, a Python library for RDF graphs.
3. **Process**:
   - Create a new RDF graph.
   - Add each filtered triple as one RDF statement (`subject predicate object .` in TTL).
   - Declare each object from an “is a” triple as an `rdfs:Class`.
   - Declare each used predicate as an `rdf:Property`.
   - Save the graph in two formats:
     - **Turtle (.ttl)**: Human‑readable text form.
     - **JSON-LD (.jsonld)**: JSON form for web/JavaScript use.

> **Why?**  
> RDF is the standard for ontologies. These files can be loaded by other tools and databases.

---

## 5. Visualization

1. **Goal**: Produce a visual diagram of the ontology.
2. **Tools**:
   - **NetworkX**: Builds a directed graph from the RDF triples.
   - **Matplotlib**: Draws the graph as a PNG image.
3. **Process**:
   - Load the Turtle file back into RDFLib.
   - Convert each triple into a node–edge in NetworkX.
   - Compute a layout (spring layout).
   - Draw nodes (concepts) and directed edges (relations) with labels.
   - Save the result as `ontology_graph.png`.

> **Why?**  
> A picture helps stakeholders quickly see the key concepts and how they connect.

---

### Summary Flow

```
PDF → full_text.txt → raw_triples → filtered_triples →
   RDF graph → ontology_manual.ttl/jsonld → PNG graph
```

Each step uses widely‑adopted Python libraries, runs with one command, and produces clear, shareable outputs.

---
