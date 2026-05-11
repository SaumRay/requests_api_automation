# 🧪 API Automation Framework
### Python + Requests + pytest + Allure | User Management & Blog Posts

![CI](https://github.com/<YOUR_USERNAME>/<YOUR_REPO>/actions/workflows/ci.yml/badge.svg)

---

## 📁 Project Structure

```
requests_api_automation/
│
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI pipeline
│
├── config/
│   ├── config.yaml                  # Real credentials — gitignored, never committed
│   └── config.yaml.example          # Safe template with placeholders — committed
│
├── api/
│   ├── base_client.py               # Core HTTP client (requests.Session wrapper)
│   └── endpoints.py                 # All endpoint constants — no hardcoded URLs
│
├── tests/
│   ├── test_users.py                # GET/POST/PUT/PATCH/DELETE — User CRUD
│   ├── test_auth.py                 # Login, register, token injection, unauth
│   ├── test_posts.py                # GET/POST/PUT/PATCH/DELETE — Posts CRUD
│   ├── test_schema_validation.py    # JSON schema contract tests
│   └── test_data_driven.py          # Parametrized data-driven tests
│
├── utils/
│   ├── schemas.py                   # 14 JSON Schema definitions
│   ├── schema_validator.py          # jsonschema wrapper with rich error output
│   ├── data_loader.py               # JSON test data loader for parametrize
│   └── allure_labels.py             # Centralised Allure decorator constants
│
├── test_data/
│   └── users.json                   # 28 parametrized test cases
│
├── reports/                         # Auto-generated after each run (gitignored)
│   ├── test_report.html             # pytest-html single-file report
│   └── allure-results/              # Allure raw JSON results
│
├── conftest.py                      # Shared fixtures + Allure hooks + HTML metadata
├── pytest.ini                       # pytest config, markers, report paths
├── run_tests.sh                     # Master shell runner (smoke/regression/allure/…)
└── requirements.txt                 # All dependencies pinned
```

---

## ⚙️ Setup

```bash
# 1. Clone the repo
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
cd requests_api_automation

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Allure CLI (for local Allure reports)
# macOS:
brew install allure
# Windows (scoop):
scoop install allure
# Linux:
wget https://github.com/allure-framework/allure2/releases/download/2.27.0/allure-2.27.0.tgz
tar -zxf allure-2.27.0.tgz && sudo mv allure-2.27.0 /opt/allure
sudo ln -s /opt/allure/bin/allure /usr/local/bin/allure

# 5. Configure credentials
cp config/config.yaml.example config/config.yaml
# Open config/config.yaml and fill in your real API key + credentials
# config.yaml is gitignored — it will never be committed
```

---

## ▶️ Running Tests

### Using the master runner (recommended)
```bash
./run_tests.sh              # All tests
./run_tests.sh smoke        # Smoke only  (quick sanity after build)
./run_tests.sh regression   # Full regression suite
./run_tests.sh auth         # Auth tests only
./run_tests.sh users        # User CRUD tests only
./run_tests.sh posts        # Posts CRUD tests only
./run_tests.sh negative     # Negative / failure tests only
./run_tests.sh allure       # All tests + open Allure report in browser
```

### Using pytest directly
```bash
pytest                                    # All tests
pytest tests/test_users.py -v            # Specific file
pytest -m smoke                          # By marker
pytest -m "auth and negative"            # Combined markers
pytest -m regression --tb=long           # Full tracebacks
pytest -n auto                           # Parallel (pytest-xdist)
pytest -k "test_login"                   # By test name keyword
```

---

## 📊 Reports

### HTML Report (auto-generated after every run)
```bash
open reports/test_report.html            # macOS
start reports/test_report.html           # Windows
```

### Allure Report
```bash
# Serve live (recommended — opens in browser automatically)
allure serve reports/allure-results

# Or generate static HTML then open
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

---

## 🔁 CI/CD — GitHub Actions

Every push to `main` automatically:
1. Spins up Ubuntu + Python 3.11
2. Installs all dependencies from `requirements.txt`
3. Reconstructs `config/config.yaml` securely from **GitHub Secrets**
4. Runs all 156 tests via `pytest`
5. Generates Allure + pytest-html reports
6. Uploads both reports as **downloadable artifacts** (retained 14 days)

### Setting up GitHub Secrets (one-time)
Go to **Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `REQRES_API_KEY` | Your ReqRes API key |
| `VALID_EMAIL` | `eve.holt@reqres.in` |
| `VALID_PASSWORD` | `cityslicka` |

> ⚠️ `config/config.yaml` is gitignored. `config/config.yaml.example` (with placeholders) is committed instead. The CI pipeline reconstructs the real config at runtime using the secrets above — credentials are never stored in the repo or logs.

### Viewing CI reports
After a run: **Actions → your workflow run → Artifacts**
- `allure-report` → download zip, open `index.html`
- `pytest-html-report` → download and open directly

---

## 🌐 APIs Under Test

| Service | Base URL | Used For |
|---|---|---|
| ReqRes.in | `https://reqres.in/api` | Auth + User Management |
| JSONPlaceholder | `https://jsonplaceholder.typicode.com` | Blog Posts CRUD |

---

## 🏷️ Test Markers

| Marker | What it runs |
|---|---|
| `smoke` | GET happy paths — run after every build |
| `regression` | Full POST/PUT/PATCH/DELETE suite |
| `auth` | Login, register, token, unauth tests |
| `users` | All User Management tests |
| `posts` | All Blog Posts tests |
| `negative` | Error cases, invalid inputs, 4xx tests |
| `schema` | JSON schema contract validation |
| `data_driven` | Parametrized tests from JSON |

---

## 📈 Test Suite Summary

| File | Tests | Notes |
|---|---|---|
| `test_users.py` | 31 | User CRUD — GET/POST/PUT/PATCH/DELETE |
| `test_auth.py` | 26 | Login, register, token injection, unauth |
| `test_schema_validation.py` | 38 | JSON schema contract validation |
| `test_data_driven.py` | 42 | 8 parametrized functions × JSON datasets |
| `test_posts.py` | 17 | Blog Posts CRUD |
| **Total** | **156** | **153 pass · 3 xfail (known API limitation)** |

### ⚠️ Known Issue — 3 `XFAIL` tests
Three tests targeting `POST /login` with a wrong password are marked `xfail`:

| Test | Reason |
|---|---|
| `test_auth.py::test_invalid_password_returns_400` | ReqRes demo API returns `200 + token` for known emails with any password |
| `test_data_driven.py::test_login_scenarios[TC_AUTH_LOGIN_002]` | Same — `_meta.context: legacy_success` confirms demo-mode response |
| `test_schema_validation.py::test_login_error_schema_wrong_password` | Same root cause |

These are marked `xfail(strict=True)` — they appear as `XFAIL` in reports (not failures), and will automatically promote to `XPASS` if the ReqRes API behaviour is restored, alerting you to re-enable the assertions.

---

## 🏗️ Build Phases

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Done | Project setup, config, base client, endpoints |
| Phase 2 | ✅ Done | User CRUD — GET/POST/PUT/PATCH/DELETE tests |
| Phase 3 | ✅ Done | Auth tests — login, register, token injection |
| Phase 4 | ✅ Done | Schema validation — 14 JSON schemas |
| Phase 5 | ✅ Done | Data-driven tests — parametrized from JSON |
| Phase 6 | ✅ Done | HTML + Allure reporting, test_posts.py, run_tests.sh |
| Phase 7 | ✅ Done | GitHub Actions CI pipeline + secrets-based config injection |