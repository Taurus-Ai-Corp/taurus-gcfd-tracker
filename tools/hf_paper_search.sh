#!/usr/bin/env bash
# hf_paper_search.sh — Search HF daily papers + arXiv for bio-quantum research
# TAURUS AI Corp — Global Bio-Foundry
#
# Searches both HF daily_papers API and arXiv API for quantum biology,
# Posner molecules, and neuro-coherence research papers.

set -euo pipefail

show_help() {
    cat <<'HELP'
hf_paper_search.sh — Search HF & arXiv for bio-quantum research papers

USAGE:
    ./hf_paper_search.sh <query> [limit]
    ./hf_paper_search.sh --presets
    ./hf_paper_search.sh --arxiv <query> [limit]
    ./hf_paper_search.sh --both <query> [limit]

ARGUMENTS:
    query       Search terms (e.g. "quantum coherence biology")
    limit       Max results (default: 10)

OPTIONS:
    --presets   Search all bio-quantum preset terms
    --arxiv     Search arXiv API only (broader coverage, older papers)
    --both      Search both HF daily papers AND arXiv
    --days N    Only show HF papers from last N days (default: 30)
    --help      Show this help message

PRESET QUERIES (--presets):
    Posner molecule, quantum coherence biology, neural oscillation,
    theta-gamma coupling, EEG phase synchronization, quantum brain,
    calcium phosphate quantum, room temperature quantum, decoherence biology

OUTPUT:
    NDJSON — one JSON object per line:
      source, id/arxiv_id, title, summary, published, upvotes, url

EXAMPLES:
    # Search HF daily papers
    ./hf_paper_search.sh "quantum biology"

    # Search arXiv for older papers
    ./hf_paper_search.sh --arxiv "Posner molecule quantum" 20

    # Run all presets on both sources
    ./hf_paper_search.sh --both --presets | jq -s 'unique_by(.title) | sort_by(.published) | reverse'

    # Filter for high-impact papers
    ./hf_paper_search.sh "EEG" 50 | jq 'select(.upvotes > 5)'
HELP
    exit 0
}

LIMIT=10
QUERY=""
USE_PRESETS=false
SOURCE="hf"  # hf, arxiv, both
DAYS=30

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) show_help ;;
        --presets) USE_PRESETS=true; shift ;;
        --arxiv) SOURCE="arxiv"; shift ;;
        --both) SOURCE="both"; shift ;;
        --days) DAYS="$2"; shift 2 ;;
        *)
            if [[ -z "$QUERY" ]]; then
                QUERY="$1"
            else
                LIMIT="$1"
            fi
            shift
            ;;
    esac
done

search_hf_papers() {
    local query="$1"
    local limit="$2"

    local url="https://huggingface.co/api/daily_papers?limit=${limit}"

    local response
    if [[ -n "${HF_TOKEN:-}" ]]; then
        response=$(curl -s -H "Authorization: Bearer ${HF_TOKEN}" "$url")
    else
        response=$(curl -s "$url")
    fi

    echo "$response" | python3 -c "
import sys, json
from datetime import datetime, timedelta, timezone

data = json.load(sys.stdin)
query_terms = '${query}'.lower().split()
cutoff = datetime.now(timezone.utc) - timedelta(days=${DAYS})

for p in data:
    paper = p.get('paper', {})
    title = paper.get('title', '').lower()
    summary = paper.get('summary', '').lower()

    # Keyword match
    if not any(term in title or term in summary for term in query_terms):
        continue

    out = {
        'source': 'huggingface',
        'id': paper.get('id', ''),
        'title': paper.get('title', ''),
        'summary': paper.get('ai_summary', paper.get('summary', ''))[:300],
        'published': p.get('publishedAt', ''),
        'upvotes': paper.get('upvotes', 0),
        'url': f\"https://huggingface.co/papers/{paper.get('id', '')}\",
        'keywords': paper.get('ai_keywords', []),
        'github': paper.get('githubRepo', '')
    }
    print(json.dumps(out))
"
}

search_arxiv() {
    local query="$1"
    local limit="$2"
    local encoded_query
    encoded_query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")

    local url="http://export.arxiv.org/api/query?search_query=all:${encoded_query}&start=0&max_results=${limit}&sortBy=submittedDate&sortOrder=descending"

    local response
    response=$(curl -s --retry 2 --retry-delay 3 "$url")

    if [[ -z "$response" ]]; then
        >&2 echo "[arxiv] Empty response (rate limited?). Try again in a few seconds."
        return 0
    fi

    echo "$response" | python3 -c "
import sys, json, xml.etree.ElementTree as ET

ns = {'atom': 'http://www.w3.org/2005/Atom'}
tree = ET.parse(sys.stdin)
root = tree.getroot()

for entry in root.findall('atom:entry', ns):
    arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1] if entry.find('atom:id', ns) is not None else ''
    title = entry.find('atom:title', ns).text.strip().replace('\n', ' ') if entry.find('atom:title', ns) is not None else ''
    summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')[:300] if entry.find('atom:summary', ns) is not None else ''
    published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ''

    authors = []
    for author in entry.findall('atom:author', ns):
        name = author.find('atom:name', ns)
        if name is not None:
            authors.append(name.text)

    categories = []
    for cat in entry.findall('atom:category', ns):
        categories.append(cat.get('term', ''))

    out = {
        'source': 'arxiv',
        'id': arxiv_id,
        'title': title,
        'summary': summary,
        'published': published,
        'authors': authors[:5],
        'categories': categories,
        'url': f'https://arxiv.org/abs/{arxiv_id}'
    }
    print(json.dumps(out))
"
}

run_search() {
    local query="$1"
    local limit="$2"

    case "$SOURCE" in
        hf)
            search_hf_papers "$query" "$limit"
            ;;
        arxiv)
            search_arxiv "$query" "$limit"
            ;;
        both)
            search_hf_papers "$query" "$limit"
            search_arxiv "$query" "$limit"
            ;;
    esac
}

# Bio-quantum preset search terms
PRESETS=(
    "Posner molecule"
    "quantum coherence biology"
    "neural oscillation coherence"
    "theta gamma coupling"
    "EEG phase synchronization"
    "quantum brain"
    "calcium phosphate quantum"
    "room temperature quantum computing"
    "decoherence biology"
    "viscoelastic quantum"
    "biomanufacturing quantum"
    "zero knowledge proof biology"
)

if $USE_PRESETS; then
    for preset in "${PRESETS[@]}"; do
        >&2 echo "[papers] $preset ..."
        run_search "$preset" "$LIMIT"
    done
    exit 0
fi

if [[ -z "$QUERY" ]]; then
    echo "Error: No query provided. Use --help for usage." >&2
    exit 1
fi

>&2 echo "[papers] $QUERY (limit: $LIMIT, source: $SOURCE) ..."
run_search "$QUERY" "$LIMIT"
