# AxiomUIXV — Forbes-Grade Deterministic Terminal Substrate

A **local, privacy-first NLP agent** with Warp AI-style commands, powered by **Ollama** and hardened by **deterministic safety invariants**. Single-file Windows .exe packaged for professional deployments.

## Features

### 🎯 Warp AI-Style Commands
- `!ai <query>` — Chat with local model (Ollama)
- `!explain` — Explain last shell command and its output
- `!fix` — Diagnose errors and propose corrected commands
- Shell commands execute under **DeterministicAgent** safety checks

### 🛡️ Deterministic Safety
- **Zero Entropy Ledger**: Durable audit trail of every command, file mutation, and model interaction
- **DeterministicAgent**: Invariant-checked shell execution (forbids destructive ops, shell metacharacters)
- **Omega Invariant**: System prompt anchors all model calls to determinism-first philosophy
- **Alexis Protocol**: Envelopes all responses with architect acknowledgment and provenance

### 🎨 Forbes-Grade Polish
- **Textual TUI**: Styled widgets, reactive state, borderless terminal UI
- **Premium Branding**: Icon, manifest, DPI awareness, Windows 10/11 compatible
- **Single-File .exe**: No dependencies to install; just run

### 🔐 Privacy First
- **Local-only model**: All data stays on your machine (Ollama HTTP)
- **No cloud calls**: Zero external API dependencies
- **Encrypted ledger**: Zero Entropy Ledger in plaintext (JSON Lines), fully inspectable

## Installation

### Windows (One-Click Desktop App)
1. Download `AxiomUIXV.exe` from [Releases](https://github.com/AXI0MH1VE/AxiomUIXV/releases).
2. Run the installer script:
   ```powershell
   .\Install-App.ps1
   ```
3. Double-click the desktop shortcut **AxiomUIXV** to launch.

### From Source
1. Clone the repo:
   ```bash
   git clone https://github.com/AXI0MH1VE/AxiomUIXV.git
   cd AxiomUIXV
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. Ensure **Ollama** is running locally (default: `http://localhost:11434`).

4. Launch the app:
   ```bash
   python launch.py
   ```

## Usage

Once the dashboard opens:

```
┌─ AxiomUIXV — Deterministic Terminal Substrate ─┐
│  [Thought Stream]                              │
│  source: model[OK]                             │
│  content: Deterministic safety is paramount... │
│                                                 │
│  [Status: last command | exit=0]              │
│  !ai for chat | !explain | !fix               │
└─────────────────────────────────────────────────┘
```

### Example Session

```bash
# Run a shell command
axiom> ls -la
# stdout/stderr appears in Thought Stream

# Explain what it did
axiom> !explain
# model: "ls -la lists all files in current directory..."

# Diagnose if it failed
axiom> !fix
# model: "Try: ls -la --group-directories-first"

# Chat with the model
axiom> !ai why is determinism important in AI?
# model: "Determinism ensures reproducibility, auditability, and safety..."
```

## Architecture

### Core Modules

- **`textual_dashboard.py`**: Premium Textual TUI interface
- **`kernel.py`**: Local Ollama HTTP interface (no external calls)
- **`law_core.py`**: Model calls wrapped in Alexis Protocol + Zero Entropy recording
- **`deterministic_agent.py`**: Shell command execution under invariants
- **`entropy_shield.py`**: Audit ledger (JSON Lines, fully inspectable)
- **`foundations.py`**: Omega Invariant, Zero Entropy Law, axioms
- **`main.py`** / **`launch.py`**: Entry points

### Build Pipeline

- **`axiom_ui_xv_simple.spec`**: PyInstaller spec for single-file .exe
- **`Install-App.ps1`**: Windows installer to LOCALAPPDATA
- **`app.manifest`**: DPI awareness, Windows 10/11 compatibility
- **`axiom_icon.ico`**: Branding icon

## Configuration

Customize behavior with command-line arguments:

```bash
python launch.py \
  --model llama2 \
  --ollama-url http://localhost:11434 \
  --log-dir .axiom_logs
```

All settings and audit logs stored in `.axiom_logs/`.

## Safety Invariants

The **DeterministicAgent** blocks:
- Destructive commands: `rm`, `rm -rf`, `shutdown`, `reboot`, `format`
- Shell metacharacters: `|`, `&`, `;`, `&&`, `||` (non-local reasoning)
- Empty commands
- Unverifiable operations

All blocked operations are logged to the Zero Entropy Ledger.

## Deterministic Axioms

From **foundations.py**:

> **Omega Invariant**: "The human substrate is the axiomatic fixed point. The AI is a tool, not the mover."

> **Zero Entropy Law**: "If you cannot prove the computation is correct or reversible at this scale, you do not get to run it."

> **Substrate Principle**: "The human is the substrate; the AI is the tool."

## Requirements

- **Python 3.8+**
- **Ollama** running locally (https://ollama.ai)
- **Windows 10/11** (for packaged .exe)

### Python Dependencies

```
rich>=13.7.0
textual>=0.50.0
httpx>=0.27.0
PyYAML>=6.0.0
psutil>=5.9.0
```

## Security & Privacy

✅ **Local-only**: No cloud calls, no telemetry  
✅ **Auditable**: Every action recorded in Zero Entropy Ledger  
✅ **Invariant-checked**: Safety constraints enforced before execution  
✅ **Deterministic**: Reproducible, verifiable behavior  
✅ **Open-source**: Full transparency  

## Development

### Build the .exe

```bash
pip install pyinstaller
pyinstaller --clean axiom_ui_xv_simple.spec
```

Output: `dist/AxiomUIXV.exe`

### Contributing

1. Fork the repo
2. Create a feature branch
3. Commit changes with: `Co-Authored-By: Warp <agent@warp.dev>`
4. Push and open a PR

## License

© 2026 Axiom Hive. All rights reserved.

## Credits

**Architect**: Alexis M. Adams  
**Built with**: Python, Textual, Rich, Ollama, PyInstaller

---

**Get started**: Clone the repo or download the .exe from Releases. Questions? Open an issue on GitHub.
