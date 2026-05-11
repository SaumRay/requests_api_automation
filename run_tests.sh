#!/bin/bash
# ─────────────────────────────────────────────
# API Automation Framework — Master Test Runner
# ─────────────────────────────────────────────
# Usage:
#   ./run_tests.sh              → Run ALL tests
#   ./run_tests.sh smoke        → Smoke only
#   ./run_tests.sh regression   → Regression suite
#   ./run_tests.sh auth         → Auth tests only
#   ./run_tests.sh users        → User tests only
#   ./run_tests.sh posts        → Posts tests only
#   ./run_tests.sh negative     → Negative tests only
#   ./run_tests.sh allure       → Run all + open Allure report
# ─────────────────────────────────────────────

set -e  # Exit immediately on any error

# ── Colours ───────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
RESET='\033[0m'

# ── Paths ─────────────────────────────────────
REPORT_DIR="reports"
HTML_REPORT="$REPORT_DIR/test_report.html"
ALLURE_RESULTS="$REPORT_DIR/allure-results"
ALLURE_REPORT="$REPORT_DIR/allure-report"

echo ""
echo -e "${CYAN}══════════════════════════════════════════════${RESET}"
echo -e "${CYAN}  API Automation Framework — Test Runner       ${RESET}"
echo -e "${CYAN}══════════════════════════════════════════════${RESET}"
echo ""

# ── Ensure reports directory exists ──────────
mkdir -p "$REPORT_DIR"

# ── Parse argument ───────────────────────────
MODE=${1:-"all"}

case "$MODE" in

    smoke)
        echo -e "${YELLOW}▶ Running SMOKE tests...${RESET}"
        pytest -m smoke -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    regression)
        echo -e "${YELLOW}▶ Running REGRESSION suite...${RESET}"
        pytest -m regression -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    auth)
        echo -e "${YELLOW}▶ Running AUTH tests...${RESET}"
        pytest -m auth -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    users)
        echo -e "${YELLOW}▶ Running USER tests...${RESET}"
        pytest -m users -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    posts)
        echo -e "${YELLOW}▶ Running POSTS tests...${RESET}"
        pytest -m posts -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    negative)
        echo -e "${YELLOW}▶ Running NEGATIVE tests...${RESET}"
        pytest -m negative -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;

    allure)
        echo -e "${YELLOW}▶ Running ALL tests + opening Allure report...${RESET}"
        pytest -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        echo ""
        echo -e "${CYAN}▶ Generating Allure HTML report...${RESET}"
        allure generate "$ALLURE_RESULTS" -o "$ALLURE_REPORT" --clean
        echo -e "${CYAN}▶ Opening Allure report in browser...${RESET}"
        allure open "$ALLURE_REPORT"
        ;;

    all|*)
        echo -e "${YELLOW}▶ Running ALL tests...${RESET}"
        pytest -v --tb=short \
            --html="$HTML_REPORT" --self-contained-html \
            --alluredir="$ALLURE_RESULTS"
        ;;
esac

# ── Post-run summary ─────────────────────────
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${GREEN}  ✅  Test run complete!${RESET}"
echo -e "${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "  📄 HTML Report  : ${CYAN}${HTML_REPORT}${RESET}"
echo -e "  📊 Allure Data  : ${CYAN}${ALLURE_RESULTS}${RESET}"
echo ""
echo -e "  To view Allure report:"
echo -e "  ${YELLOW}allure serve ${ALLURE_RESULTS}${RESET}"
echo ""