#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    from pyvis.network import Network
except Exception:
    sys.stderr.write("Missing dependency 'pyvis'. Install it with: pip install pyvis\n")
    raise

def _read_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "Learners": [{"learner_id": "A101"}, {"learner_id": "A102"}],
            "Content": [
                {"content_id": "C101", "title": "Loops"},
                {"content_id": "C102", "title": "Functions"},
                {"content_id": "C103", "title": "Conditionals"},
            ],
            "Progress": [
                {"learner_id": "A101", "content_id": "C101", "mastery": 0.8, "completion": 0.9},
                {"learner_id": "A101", "content_id": "C102", "mastery": 0.4, "completion": 0.6},
                {"learner_id": "A102", "content_id": "C103", "mastery": 0.95, "completion": 0.9},
            ],
        }

def build_graph(schema: dict) -> Network:
    net = Network(height="700px", width="100%", bgcolor="#ffffff", font_color="black")

    # Learners
    for node in schema.get("Learners", []):
        lid = node.get("learner_id")
        net.add_node(lid, label=f"Learner: {lid}", color="#6baed6", shape="dot", size=20)

    # Content
    for node in schema.get("Content", []):
        cid = node.get("content_id")
        title = node.get("title", cid)
        net.add_node(cid, label=f"Content: {title}", color="#74c476", shape="box", size=18)

    # Progress edges
    for p in schema.get("Progress", []):
        learner = p.get("learner_id")
        content = p.get("content_id")
        if not learner or not content:
            continue
        label = f"mastery={p.get('mastery', 0)} | completion={p.get('completion', 0)}"
        net.add_edge(learner, content, label=label, color="#fd8d3c", value=3, arrows="to")

    net.repulsion(node_distance=180, central_gravity=0.3, spring_length=150, spring_strength=0.05)
    return net

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", default="data/knowledge/schema.json")
    ap.add_argument("--out", default="data/knowledge/learning_graph_div.html")
    args = ap.parse_args()

    schema = _read_json(Path(args.schema))
    net = build_graph(schema)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    net.write_html(args.out)
    print(f"[OK] Learning graph generated → {args.out}")

if __name__ == "__main__":
    main()
