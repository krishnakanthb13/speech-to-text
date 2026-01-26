# Security Policy

## Security Audit Report
**Date**: 2026-01-26
**Auditor**: Antigravity AI

### Summary
| Category | Status | Notes |
| :--- | :--- | :--- |
| **Secrets Detection** | 🟢 Passed | `GROQ_API_KEY` is loaded from `.env` via `python-dotenv`. `.env` is listed in `.gitignore`. |
| **Injection Protection** | 🟢 Passed | No unsafe use of `eval()`, `exec()`, or unparameterized shell commands found. Keyboard input simulation is handled via `pynput.keyboard.Controller`. |
| **Authentication** | 🟢 Passed | Local application; utilizes environment variables for API authentication with Groq. |
| **Dependency Analysis** | 🟢 Passed | `requirements.txt` contains essential and trusted packages. Unused packages (`keyboard`, `pyinstaller`) were recently removed. |

---

### Findings & Mitigations

#### 1. API Key Security
- **Finding**: The application requires a Groq API Key to function.
- **Mitigation**: Users are instructed to store the key in a local `.env` file. The project includes a robust `.gitignore` to prevent accidental commits of this file.

#### 2. Keyboard Control (pynput)
- **Finding**: The application uses `pynput` to simulate typing (specifically `Ctrl+V` for pasting).
- **Security Note**: This simulates a physical user action. Under normal circumstances, this is safe and confined to the active window where the user has already placed focus.

#### 3. Log Protection
- **Finding**: transcription history is stored in `history.log`.
- **Mitigation**: `history.log` is added to `.gitignore` by default to ensure private transcripts are not pushed to public repositories.

---

### Reporting a Vulnerability
If you discover a security vulnerability within this project, please open a GitHub Issue or contact the project maintainer directly. We value your feedback and aim to maintain a secure environment for all users.
