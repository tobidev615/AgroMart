# FarmFresh API – Testing Guide (For Non‑Coders)

This guide explains, step by step, how to run and understand the automated tests for the FarmFresh API. No coding experience required.

---

## 1) What are “tests” and why run them?
- Tests automatically check that the API still works after changes.
- They quickly catch mistakes, like broken endpoints or missing permissions.
- You’ll see a simple “passed/failed” report.

---

## 2) What you need on your computer
- Python 3.8 or higher
- Internet connection (to install tools)

Optional (for advanced use):
- Redis (only if you want to test readiness with external services)

You do NOT need Docker or any external database to run the basic tests.

---

## 3) One‑time setup (about 5–10 minutes)
Follow these steps in your Terminal (macOS) or Command Prompt/PowerShell (Windows):

1. Go to the project folder
   ```bash
   cd /path/to/farmfresh-restapi
   ```

2. Create a virtual environment (keeps project tools separate)
   ```bash
   python -m venv farmfresh_env
   ```

3. Activate it
   - macOS/Linux:
     ```bash
     source farmfresh_env/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .\agromart_env\Scripts\Activate.ps1
     ```

4. Install the main project tools
   ```bash
   pip install -r requirements.txt
   ```

5. Install the testing tools
   ```bash
   pip install -r requirements-dev.txt
   ```

That’s it. Setup is done.

---

## 4) Running the tests
The command below runs all tests and prints a friendly summary.
```bash
pytest -q
```
What you’ll see:
- “.” means a test passed
- “F” means a test failed
- A final summary like “2 passed” or “1 failed”

If everything is OK you’ll see something like:
```
..  [100%]
```

---

## 5) What do our tests check today?
We ship a few basic tests so you can see it working:

- Health check
  - Verifies the health endpoint is up.
- Account registration
  - Simulates a user signing up and checks that it succeeds.

As the project grows, we’ll add tests for orders, payments, notifications, etc.

---

## 6) Running specific tests
- Run just the health test:
  ```bash
  pytest tests/test_health.py::test_health -q
  ```
- Run all account tests:
  ```bash
  pytest tests/test_accounts.py -q
  ```

---

## 7) Getting a coverage report (optional)
Coverage tells you how much of the code is executed by tests.
```bash
pytest --cov=. --cov-report=term-missing
```
You’ll see a percentage and any files/lines not covered.

---

## 8) Common issues & quick fixes
- “command not found: pytest”
  - Make sure the virtual environment is activated (see step 3.3) and you ran `pip install -r requirements-dev.txt`.
- “ModuleNotFoundError” / missing package
  - Re-run both install commands: `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`.
- Database errors
  - Try running database setup: `python manage.py migrate` (only needed if tests depend on migrations; our current basic tests do not require special setup).
- Permission denied on macOS when activating venv
  - Use: `source farmfresh_env/bin/activate` (make sure the path is correct).

---

## 9) (Optional) Run tests inside Docker
If you prefer running tests in Docker (for consistency across machines), you can do that once a Dockerfile/Compose file is added. Example command (after we add Docker files):
```bash
docker compose run --rm api pytest -q
```
We can add these Docker files later if you’d like.

---

## 10) Continuous Integration (CI) – What it is
- CI runs tests automatically in the cloud (e.g., on GitHub) on every change.
- It ensures the project stays healthy for all team members.

If you want, we can add a GitHub Actions workflow file so CI runs automatically on every push.

Example (we can add this for you):
```yaml
name: CI
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest -q
```

---

## 11) Where to ask for help
If you get stuck or see a test failing:
- Copy the error message
- Tell us which command you ran
- We’ll help diagnose and fix it

You’re all set. Running `pytest -q` is safe and quick—feel free to run it anytime to check the API’s health.


