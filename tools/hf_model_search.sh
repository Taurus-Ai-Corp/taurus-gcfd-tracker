#!/usr/bin/env bash
# hf_model_search.sh — Search Hugging Face Hub for bio-quantum and neuro-signal models
# TAURUS AI Corp — Global Bio-Foundry
#
# Usage:
#   ./hf_model_search.sh "EEG" 10
#   ./hf_model_search.sh "quantum biology" 5
#   echo "EEG signal processing" | ./hf_model_search.sh --stdin 20
#
# Output: NDJSON (one JSON object per model) for easy piping with jq

set -euo pipefail

show_help() {
    cat <<'HELP'
hf_model_search.sh — Search HF Hub for bio-quantum & neuro-signal models

USAGE:
    ./hf_model_search.sh <query> [limit]
    ./hf_model_search.sh --stdin [limit]
    ./hf_model_search.sh --presets

ARGUMENTS:
    query       Search term (e.g. "EEG", "quantum biology", "MEG signal")
    limit       Max results to return (default: 10)

OPTIONS:
    --stdin     Read query from stdin (for piping)
    --presets   Run all bio-quantum preset searches
    --full      Include full metadata (tags, sha, siblings)
    --help      Show this help message

PRESET QUERIES (--presets):
    EEG, MEG, brain signal, neuroscience, quantum biology,
    phase synchronization, coherence, biosignal, bioinformatics,
    signal processing

OUTPUT:
    NDJSON — one JSON object per line with fields:
      id, downloads, likes, tags, pipeline_tag, createdAt

EXAMPLES:
    # Basic search
    ./hf_model_search.sh "EEG transformer" 20

    # Pipe to jq for filtering
    ./hf_model_search.sh "EEG" 50 | jq -r 'select(.downloads > 100) | .id'

    # Run all preset searches
    ./hf_model_search.sh --presets | jq -s 'unique_by(.id) | sort_by(.downloads) | reverse'

    # Chain: search → enrich → filter
    ./hf_model_search.sh "brain" 30 | jq -r '.id' | ./hf_enrich_models.sh
HELP
    exit 0
}

LIMIT=10
FULL=false
QUERY=""
USE_STDIN=false
USE_PRESETS=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) show_help ;;
        --stdin) USE_STDIN=true; shift ;;
        --presets) USE_PRESETS=true; shift ;;
        --full) FULL=true; shift ;;
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

if $USE_STDIN; then
    QUERY=$(cat)
fi

AUTH_HEADER=""
if [[ -n "${HF_TOKEN:-}" ]]; then
    AUTH_HEADER="-H \"Authorization: Bearer ${HF_TOKEN}\""
fi

search_models() {
    local query="$1"
    local limit="$2"
    local encoded_query
    encoded_query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")

    local url="https://huggingface.co/api/models?search=${encoded_query}&limit=${limit}&sort=downloads&direction=-1"

    local response
    if [[ -n "${HF_TOKEN:-}" ]]; then
        response=$(curl -s -H "Authorization: Bearer ${HF_TOKEN}" "$url")
    else
        response=$(curl -s "$url")
    fi

    if $FULL; then
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data:
    print(json.dumps(m))
"
    else
        echo "$response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for m in data:
    out = {
        'id': m.get('id', ''),
        'downloads': m.get('downloads', 0),
        'likes': m.get('likes', 0),
        'tags': m.get('tags', []),
        'pipeline_tag': m.get('pipeline_tag', ''),
        'createdAt': m.get('createdAt', ''),
        'query': '$query'
    }
    print(json.dumps(out))
"
    fi
}

# Preset bio-quantum search terms
PRESETS=(
    "EEG"
    "MEG"
    "brain signal"
    "neuroscience"
    "quantum biology"
    "phase synchronization"
    "coherence"
    "biosignal"
    "bioinformatics"
    "signal processing"
    "EEG classification"
    "brain-computer interface"
)

if $USE_PRESETS; then
    for preset in "${PRESETS[@]}"; do
        >&2 echo "[search] $preset ..."
        search_models "$preset" "$LIMIT"
    done
    exit 0
fi

if [[ -z "$QUERY" ]]; then
    echo "Error: No query provided. Use --help for usage." >&2
    exit 1
fi

>&2 echo "[search] $QUERY (limit: $LIMIT) ..."
search_models "$QUERY" "$LIMIT"
