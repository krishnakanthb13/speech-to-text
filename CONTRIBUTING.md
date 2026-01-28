# Contributing to Handy-Groq STT

First off, thank you for considering contributing to Handy-Groq STT! It's people like you that make it a great tool for everyone.

## How to Contribute

### Reporting Bugs
- Use the GitHub Issues tracker.
- Describe the bug in detail, including your hardware setup (Microphone type) and OS version.
- Provide steps to reproduce the issue.

### Suggesting Enhancements
- Open a GitHub Issue with the tag `enhancement`.
- Explain how the feature would improve the user experience.

### Pull Requests
1. **Fork** the repository.
2. **Create a branch** for your feature or fix (`git checkout -b feature/amazing-feature`).
3. **Commit** your changes with clear, descriptive messages.
4. **Push** to the branch (`git push origin feature/amazing-feature`).
5. **Open a Pull Request**.

## Local Development Setup

1. **Clone the repo**:
   ```bash
   git clone https://github.com/krishnakanthb13/speech-to-text.git
   cd speech-to-text
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   The launcher scripts will automatically create a `.env` file from `.env.example` if it's missing. Open `.env` and add your `GROQ_API_KEY`.

4. **Run the app**:
   ```bash
   python main.py
   ```

## Pre-submission Checklist
- [ ] Code follows the existing style (clean, modular).
- [ ] All bare `except:` blocks are avoided.
- [ ] No secrets or personal API keys are commited.
- [ ] UI changes have been tested for "graininess" and DPI compatibility.
- [ ] Documentation is updated if features are changed.

## Metadata
- **Project Owner**: [Krishna Kanth B](https://github.com/krishnakanthb13)
- **License**: GPL v3
