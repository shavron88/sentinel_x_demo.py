# 🔒 Security Policy

Thank you for helping keep SentinelX secure.

SentinelX is an AI Edge Surveillance Platform that processes live video streams and security-related information. Because security is central to the project, responsible disclosure of vulnerabilities is highly appreciated.

---

# Supported Versions

| Version | Supported |
|----------|-----------|
| MVP (Current) | ✅ Yes |
| Older Development Builds | ❌ No |

Only the latest version of the project is actively maintained.

---

# Reporting a Vulnerability

If you discover a security vulnerability, **please do not create a public GitHub issue**.

Instead:

1. Contact the project maintainer privately.
2. Include a detailed description of the issue.
3. Explain how to reproduce it.
4. Include screenshots or logs if available.
5. Suggest a possible fix if you have one.

Example report:

```
Title:
Unauthenticated API Access

Description:
The /stats endpoint exposes internal information without authentication.

Steps to Reproduce:
1. Start SentinelX
2. Open /stats
3. Observe returned JSON

Impact:
Medium

Suggested Fix:
Require authentication middleware.
```

---

# Response Process

After receiving a vulnerability report, the maintainer will:

- Confirm receipt.
- Investigate the issue.
- Reproduce the vulnerability.
- Develop a fix.
- Release a patched version.
- Credit the reporter (if they wish).

---

# Security Goals

SentinelX follows these principles:

- Secure-by-default architecture
- Local AI processing whenever possible
- Minimal external dependencies
- Modular components
- Principle of least privilege
- Responsible evidence handling

---

# Current Security Features

Current implementation includes:

- Local video processing
- Local evidence storage
- Modular event processing
- Isolated detection modules
- Configurable camera sources

---

# Planned Security Improvements

Future releases will include:

- User authentication
- Role-Based Access Control (RBAC)
- HTTPS support
- JWT authentication
- API key protection
- Password hashing
- Secure configuration management
- Audit logging
- Encrypted evidence storage
- Secure cloud synchronization

---

# Secure Coding Guidelines

Contributors should:

- Never hardcode passwords or API keys.
- Never commit secrets to Git.
- Validate all user input.
- Keep dependencies up to date.
- Avoid unnecessary third-party libraries.
- Handle exceptions safely.
- Protect sensitive files from public exposure.

---

# Reporting False Positives

If you believe a detection result is incorrect (for example, a false weapon or fall detection), please open a normal GitHub Issue rather than a security report.

---

# Disclaimer

SentinelX is currently an MVP developed for educational and hackathon purposes.

It should not be relied upon as the sole security system in production environments without additional testing, validation, and hardening.

---

Thank you for helping make SentinelX more secure.