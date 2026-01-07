# Security Guidelines

This repository contains sensitive code and may handle API keys or credentials.
Follow these rules to keep secrets safe:

- Never commit API keys, passwords, or other secrets to the repository. Use environment variables or GitHub Secrets instead.
- Locally, store secrets in an `.env` file (ignored by `.gitignore`) or use your OS credential store. Add `.env` to `.gitignore` if needed.
- For CI or actions, store secrets in **GitHub Settings → Secrets and variables → Actions → New repository secret**.
- Enable Two-Factor Authentication (2FA) on your GitHub account (https://docs.github.com/en/authentication/securing-your-account-with-two-factor-authentication-2fa).
- If you find a secret accidentally committed: rotate it immediately (invalidate the key), remove it from the repo using `git rm --cached` and rewrite history only if necessary, then notify any affected parties.

Reporting security issues:
- If you discover a vulnerability or accidentally committed secrets in this repo, report it by creating an issue or contacting the repository owner directly.
