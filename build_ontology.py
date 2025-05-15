"""
build_ontology.py

1. Reads raw text (from PDF→text)
2. Uses spaCy + Textacy to extract S–P–O triples
3. Normalizes predicates via a synonym map
4. Keeps only a manual allow‐list of predicates (plus rdf:type for “is a”)
5. Builds an RDFLib graph with explicit class/property declarations
6. Writes out Turtle and JSON-LD
"""
import networkx as nx
import matplotlib.pyplot as plt
import re
import spacy
import textacy.extract
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
INPUT_TEXT = "full_text.txt"
OUTPUT_TTL = "ontology_manual.ttl"
OUTPUT_JSONLD = "ontology_manual.jsonld"
BASE_URI = "http://example.org/"

# Canonical predicates you want in your final ontology
PREDICATE_ALLOW = {
    "located_in",
    "threatens",
    "improves",
    "reduces",
    "generates",
    "supports",
}

# Map common verb forms → your canonical predicates
PREDICATE_SYNONYMS = {
    "locate": "located_in",
    "located in": "located_in",
    "threaten": "threatens",
    "improve": "improves",
    "reduce": "reduces",
    "generate": "generates",
    "produce": "generates",
    "support": "supports",
}

# variants of “is a” to map to rdf:type
ISA_VARIANTS = {"is", "is a", "is_an", "is an"}
# ───────────────────────────────────────────────────────────────────────────────


def clean_id(text: str) -> str:
    """Lowercase, collapse whitespace→underscore, strip non-[a-z0-9_]."""
    t = text.strip().lower()
    t = re.sub(r"\s+", "_", t)
    return re.sub(r"[^a-z0-9_]", "", t)


def normalize(node):
    """Turn a Span or list-of-Tokens into a plain string."""
    if hasattr(node, "text"):
        return node.text
    try:
        return " ".join(tok.text for tok in node)
    except Exception:
        return str(node)


def extract_triples(doc):
    """Return list of (subj, verb, obj) triples from Textacy."""
    return list(textacy.extract.subject_verb_object_triples(doc))


def main():
    # 1) Load spaCy & raw text
    nlp = spacy.load("en_core_web_sm")
    text = open(INPUT_TEXT, encoding="utf8").read()
    doc = nlp(text)

    # 2) Extract raw triples
    raw_triples = extract_triples(doc)
    print(f"🔍 Extracted {len(raw_triples)} raw triples")

    # 3) Prepare RDF graph
    EX = Namespace(BASE_URI)
    g = Graph()
    g.bind("ex", EX)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)

    classes, properties, kept = set(), set(), 0

    # 4) Process & filter triples
    for subj, verb, obj in raw_triples:
        subj_txt = normalize(subj)
        verb_txt = normalize(verb).strip().lower()
        obj_txt = normalize(obj)

        # Clean identifiers
        s_id = clean_id(subj_txt)
        o_id = clean_id(obj_txt)
        s_uri = URIRef(EX + s_id)

        # Map “is a” → rdf:type
        if verb_txt in ISA_VARIANTS:
            p_uri = RDF.type
            o_uri = URIRef(EX + o_id)
            classes.add(o_id)
        else:
            # map synonyms to canonical
            canon = PREDICATE_SYNONYMS.get(verb_txt, verb_txt)
            p_id = clean_id(canon)
            if p_id not in PREDICATE_ALLOW:
                continue
            p_uri = URIRef(EX + p_id)
            o_uri = URIRef(EX + o_id)
            properties.add(p_id)

        # add triple
        g.add((s_uri, p_uri, o_uri))
        kept += 1

    print(f"✅ Kept {kept} filtered triples")

    # 5) Declare classes & properties
    for cls in sorted(classes):
        g.add((URIRef(EX + cls), RDF.type, RDFS.Class))
    for prop in sorted(properties):
        g.add((URIRef(EX + prop), RDF.type, RDF.Property))

    # 6) Serialize
    g.serialize(destination=OUTPUT_TTL, format="turtle")
    g.serialize(destination=OUTPUT_JSONLD, format="json-ld")
    print(f"📦 Wrote {OUTPUT_TTL} and {OUTPUT_JSONLD}")


# ─── Graph visualization ────────────────────────────────────────────────────
# 1) Re-load the TTL into a fresh RDFLib graph
viz_g = Graph()
viz_g.parse(OUTPUT_TTL, format="turtle")

# 2) Build a NetworkX DiGraph
G = nx.DiGraph()
for s, p, o in viz_g:
    subj = s.split("/")[-1]
    pred = p.split("/")[-1]
    obj = o.split("/")[-1]
    G.add_edge(subj, obj, label=pred)

# 3) Compute layout & draw
pos = nx.spring_layout(G, k=1.5, iterations=50)
plt.figure(figsize=(12, 12))
nx.draw_networkx_nodes(G, pos, node_size=300)
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=10, width=1)
nx.draw_networkx_edge_labels(
    G, pos, edge_labels=nx.get_edge_attributes(G, "label"), font_size=6
)

# 4) Save out a PNG
plt.axis("off")
plt.tight_layout()
plt.savefig("ontology_graph.png", dpi=300, bbox_inches="tight")
print("→ Ontology graph saved to ontology_graph.png")

if __name__ == "__main__":
    main()
