
#!/usr/bin/env bash
# ip_guard_hook.sh — Pre-commit hook to prevent IP leaks in public repos
# TAURUS AI Corp — Global Bio-Foundry
#
# Install: cp tools/ip_guard_hook.sh .git/hooks/pre-commit
#
# This hook scans all staged files for proprietary terms and blocks the commit
# if any are found. Designed for the PUBLIC repo only.

set -euo pipefail

show_help() {
    cat <<'HELP'
ip_guard_hook.sh — Pre-commit IP leak prevention

USAGE:
    As git hook:  cp tools/ip_guard_hook.sh .git/hooks/pre-commit
    Standalone:   ./tools/ip_guard_hook.sh [--scan-all]

OPTIONS:
    --scan-all   Scan all files, not just staged (for auditing)
    --help       Show this help

BLOCKED TERMS:
    File patterns: posner_qpu_sim, dqsb_*, zk_coherence*, patent_*
    Content terms: PosnerQPUSimulator, AKQS, HQGP, NACRS, HederaHCSMock,
                   DQSB_MasterController, PQCLayer, ML-KEM, sol-gel,
                   viscoelastic, decay_constant, 55.4, Kyber
HELP
    exit 0
}

[[ "${1:-}" == "--help" ]] && show_help

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ── BLOCKED FILE PATTERNS ──────────────────────────────────
BLOCKED_FILES=(
    "posner_qpu_sim"
    "dqsb_orchestrator"
    "dqsb_master_controller"
    "zk_coherence_verifier"
    "patent_AKQS"
    "patent_HQGP"
    "DQSB_BLUEPRINT"
    "INVESTOR"
    "PRODUCTION-READY"
    "REVENUE"
    "CLINICAL_DATA"
    "ARXIV-DRAFT"
    "partnership_proposal"
)

# ── BLOCKED CONTENT TERMS ──────────────────────────────────
# These are the proprietary algorithm signatures
BLOCKED_TERMS=(
    "PosnerQPUSimulator"
    "AKQS"
    "HQGP"
    "NACRS"
    "HederaHCSMock"
    "DQSB_MasterController"
    "DQSBOrchestrator"
    "PQCLayer"
    "ML-KEM-768"
    "ML-DSA-65"
    "viscoelastic"
    "sol-gel"
    "decay_constant"
    "Sol.*Gel.*transition"
    "viscosity.*55"
    "0\.0001.*decay"
    "40Hz.*threshold"
    "Posner.*qubit"
    "Posner.*molecule.*sim"
    "bioreactor.*fleet"
    "governance_audit"
    "coherence_verifier"
    "Kyber"
)

VIOLATIONS=0

# Get files to scan
if [[ "${1:-}" == "--scan-all" ]]; then
    FILES=$(find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) ! -path "./.git/*" ! -path "./node_modules/*" ! -path "./.hf_space_staging/*")
else
    FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || echo "")
fi

if [[ -z "$FILES" ]]; then
    echo -e "${GREEN}No files to scan.${NC}"
    exit 0
fi

echo -e "${YELLOW}[IP Guard] Scanning staged files for proprietary content...${NC}"

# Check filenames
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    basename=$(basename "$file")
    for pattern in "${BLOCKED_FILES[@]}"; do
        if [[ "$basename" == *"$pattern"* ]]; then
            echo -e "${RED}BLOCKED FILE: ${file}${NC}"
            echo "  Matches blocked pattern: ${pattern}"
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    done
done <<< "$FILES"

# Check file contents
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ ! -f "$file" ]] && continue

    for term in "${BLOCKED_TERMS[@]}"; do
        if grep -qE "$term" "$file" 2>/dev/null; then
            echo -e "${RED}BLOCKED CONTENT in ${file}:${NC}"
            grep -nE "$term" "$file" 2>/dev/null | head -3 | while read -r line; do
                echo "  $line"
            done
            VIOLATIONS=$((VIOLATIONS + 1))
        fi
    done
done <<< "$FILES"

# Verdict
echo ""
if [[ $VIOLATIONS -gt 0 ]]; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}  COMMIT BLOCKED: ${VIOLATIONS} IP violation(s) detected${NC}"
    echo -e "${RED}  Proprietary content must not enter public repos.${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
else
    echo -e "${GREEN}[IP Guard] Clean — no proprietary content detected.${NC}"
    exit 0
fi
