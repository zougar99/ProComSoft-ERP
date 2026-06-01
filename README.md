# 🏢 ProComSoft-ERP — ProComSoft ERP — Système de Gestion d'Entreprise avec POS, CRM, comptabilité et IA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/zougar99/ProComSoft-ERP/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/zougar99/ProComSoft-ERP?style=social)](https://github.com/zougar99/ProComSoft-ERP)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)](https://github.com/zougar99/ProComSoft-ERP)

> ProComSoft ERP — Système de Gestion d'Entreprise avec POS, CRM, comptabilité et IA. Full enterprise resource planning system for small to medium businesses.

---

## 📖 Table of Contents
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Screenshots](#-screenshots)
- [Roadmap](#-roadmap)
- [FAQ](#-faq)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features
- ✔ **POS Module** — Point of sale with receipt printing, barcode scanning, and payment integration
- ✔ **CRM** — Customer management with history, preferences, and communication tracking
- ✔ **Accounting** — General ledger, accounts payable/receivable, bank reconciliation
- ✔ **Inventory** — Stock tracking, purchase orders, supplier management
- ✔ **AI Analytics** — Sales forecasting, customer insights, anomaly detection
- ✔ **HR Module** — Employee management, payroll, attendance tracking
- ✔ **Reporting** — Financial reports, sales reports, tax reports (multi-format)

---

## 🔮 How It Works

```
  Input ──► Processing Pipeline ──► Output
  ┌────────┐   ┌────────┐   ┌────────┐
  │ Data   │──►│ Engine │──►│ Result │
  │ Source │   │ Logic  │   │        │
  └────────┘   └────────┘   └────────┘
```

1. **Input** — Load data from file, API, or user input
2. **Process** — Core engine applies logic/analysis/transformation
3. **Output** — Results displayed in UI, saved to file, or sent via API

---

## 💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| UI | PyQt5 / CustomTkinter |
| Database | PostgreSQL / SQLite |
| AI | scikit-learn + pandas |
| Platform | Windows / Linux |

---

## 🚀 Installation

```bash
git clone https://github.com/zougar99/ProComSoft-ERP.git
cd ProComSoft-ERP
pip install -r requirements.txt
```

---

## 📄 Configuration

Create a `config.yaml` or `.env` file in the project root:

```yaml
# Application settings
debug: false
port: 8080
theme: dark
language: en
```

---

## 🧰 Usage Guide

1. Launch: `python main.py`
2. Set up company profile
3. Configure modules (POS / CRM / Accounting)
4. Add products, customers, and suppliers
5. Start processing sales and managing operations

---

## 🖼 Screenshots

> *(Screenshots coming soon. PRs welcome!)*

---

## 🔄 Roadmap

- 🟢 Web dashboard
- 🟡 Mobile companion app
- ⚫ API access
- ⚫ Plugin system
- ⚫ Multi-language support

---

## ❓ FAQ

### Is this suitable for multi-branch operations?
Yes — supports multi-branch with centralized reporting.

### Does it support VAT/TVA?
Yes — configurable tax rates per product and region.

---

## 🚧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **App won't start** | Check Python version (3.10+); run `pip install -r requirements.txt` |
| **No output** | Check logs in `logs/` folder; enable debug mode in config |
| **Performance issues** | Close other applications; reduce batch size in config |
| **Dependency errors** | Create fresh venv: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📐 License
Distributed under the **MIT License**. See [`LICENSE`](https://github.com/zougar99/ProComSoft-ERP/blob/main/LICENSE) for more information.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/zougar99">zougar99</a>
</p>
