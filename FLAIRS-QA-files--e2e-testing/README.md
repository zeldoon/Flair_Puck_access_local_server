## Notice

Please run `split_tests.py` before committing to the repo with a new test. It wouldn't hurt to add `python feature/split_tests.py` as a pre-commit hook (`.git/pre-commit`). You can also make your test dev life a lot easier by adding the ft RDS password as `ft_pass` (this will be .gitignored) and adding `./commit_test.sh` to that same pre-commit script. This will run all new and modified tests through execution against an FT environment populated from your `test_db.sql`.

# Testing with Playwright-Python

To run tests, start by installing requirements. If on a Debian-family Linux (such as Ubuntu), you may have to change `python` for `python3`.

To install pip if it's not on your machine:
```bash
python -m ensurepip
pip install -U pip
```
OR
```bash
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip install -U pip
```

To install pipenv if it's not on your machine:
Mac:
```bash
brew install pipx
pipx ensurepath
brew update && brew upgrade pipx
pipx install pipenv
```

Install requirements, run subsequent commands in pipenv shell:
```bash
pipenv install
pipenv shell
```

Install Playwright deps:
```bash
playwright install
```

When running tests, all PyTest command line options are available to you as normal. I personally almost never run anything without `-vs`.

Run Setup Process Tests:
```bash
pytest setup_process/tests
```

Run Feature Tests:
```bash
PGUSER=flair PGPASSWORD=[redacted] PGHOST=flair-ft-aurora.cluster-cfkoqjoirj4p.us-east-1.rds.amazonaws.com PGPORT=5432 PGDATABASE=flair_ft ./db_reset.sh
pytest feature/tests
```

**Note: if running feature tests against a deployed PR branch use `PR_NUMBER=PR-NNN ./set-pr-location.sh` to set the env properly and `git checkout master feature/env.json` to reset the env to the original state. Don't push a broken `env.json`.**

Debug tests:
```bash
PWDEBUG=1 TEST_ENV=dev pytest path/to/tests -vs
```

To run in headed mode (so you can watch the action), ensure that `settings.json` in your test folder (`setup_process` or `feature`) has the following setting:
```json
{
    "browser_type_settings": {
        "headless": false
    }
}
```
Find the other `browser_type_settings` [here](https://playwright.dev/python/docs/api/class-browsertype#browser-type-launch) and the `browser_context_settings` [here](https://playwright.dev/python/docs/api/class-browser#browser-new-context).

Test execution traces will be recorded and overwritten every session.

Write new tests:

Follow the (instructions on Notion)[https://www.notion.so/flair-engineering/Adding-a-Test-Suite-to-e2e-testing-feature-883a743793594f39ab3f5ea73848f8b6].
