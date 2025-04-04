# 🔐 Security Policy

## Supported Versions

As Gittxt is currently in **v1.7.0**, we aim to provide security updates for the latest release only.

| Version | Supported          |
|---------|--------------------|
| 1.7.0   | ✅ Actively supported |

---
# 🔐 Gittxt Security Practices

Gittxt is designed with security best practices in mind to ensure safe and reliable operation.

---

## 🛡 Security Features

- **Local Processing**: All repository processing and file scanning are performed locally, minimizing data exposure.
- **Selective File Processing**: Only textual content and explicitly included assets are processed.
- **Configurable Exclusions**: Use `.gittxtignore` files and exclusion patterns to ensure sensitive data or files are never scanned or included in outputs.
- **No Persistent Caching**: Scanned repository data is not cached locally to avoid unnecessary retention of potentially sensitive information.

---

## 🚧 Best Practices

### Exclude Sensitive Files

Always exclude sensitive files using CLI patterns or a `.gittxtignore` file:

```text
*.pem
*.key
.env
secrets.json
```

CLI example:
```bash
gittxt scan . --exclude-patterns "*.pem" "*.key" ".env"
```

### Limit Repository Scans

Scan only necessary parts of your repository:

```bash
gittxt scan . --include-patterns "src/**/*"
```

### Secure Outputs

- Use the `--output-dir` option to store generated outputs in a secure, dedicated location.
- Consider enabling `--zip` mode for secure and organized data management.

---

## 🔍 Auditing and Logs

- Gittxt supports configurable logging levels (`debug`, `info`, `warning`, `error`).
- Monitor logs for unusual activity, file access errors, or unexpected file type detections:

```bash
gittxt scan . --log-level info
```

---

## 🚨 Reporting Vulnerabilities

If you identify a vulnerability or security issue:
- **Do not** disclose publicly immediately.
- Privately report.

We appreciate your responsible disclosure and commit to addressing vulnerabilities promptly.

We are committed to ensuring the security of Gittxt and the safety of its users. 
If you discover a vulnerability, please follow the process below.

### 📩 How to Report
- Email **sandeep.paidipati@gmail.com** with the following:
  - Description of the vulnerability
  - Steps to reproduce
  - Impact assessment (e.g., data leakage, remote execution, etc.)
  - Suggested mitigation (if available)
  
Please do **NOT** file public issues for security vulnerabilities.

### 🕒 Response Timeline
- We aim to acknowledge your report within **3 business days**.
- After triage, remediation will typically occur within **30 days**, depending on severity.

### 🔒 Disclosure
We practice **responsible disclosure**. We ask that reporters:
- Avoid publicly disclosing vulnerabilities prior to a confirmed patch release.
- Coordinate with us for coordinated disclosure timelines, if needed.

---

## Our Commitment
- We treat security issues with urgency.
- Critical vulnerabilities may lead to expedited releases.
- Credits will be given to researchers who responsibly disclose bugs (unless anonymity is requested).

Thank you for helping make **Gittxt** a safer project!

---