# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the TendedLoop Arena SDK, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email **security@tendedloop.com** with:

1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

We will acknowledge your report within 48 hours and provide a timeline for a fix.

## Strategy Tokens

Strategy tokens (`strat_...`) are scoped to a single experiment variant and grant limited access:
- Read signals for that variant only
- Submit config updates (subject to guardrails)
- Send heartbeats
- View the experiment scoreboard

**Best practices:**
- Never commit tokens to source control
- Use environment variables (`STRATEGY_TOKEN`)
- Rotate tokens if compromised
- Tokens expire with the experiment

## HTTPS Enforcement

The SDK enforces HTTPS for all non-localhost connections to prevent credential leakage. Attempting to connect over plain HTTP raises `ValueError`. HTTP is only allowed for `localhost` / `127.0.0.1` during local development.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |
