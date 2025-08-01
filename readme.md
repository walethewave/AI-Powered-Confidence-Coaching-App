# 🌟 ConfidenceAI — Your Personal Confidence Coach  
_Empowering authentic growth through AI-driven, explainable coaching_

👉 **[🌐 Try the App Live on Streamlit](https://9punzdhswetzx92taubijy.streamlit.app/)**

[![Build Status](https://img.shields.io/github/actions/workflow/status/walethewave/Confidence-Coach/ci.yml?branch=main&label=build)](https://github.com/walethewave/Confidence-Coach/actions)
[![PyPI Version](https://img.shields.io/pypi/v/confidenceai)](https://pypi.org/project/confidenceai/)
[![License](https://img.shields.io/github/license/walethewave/Confidence-Coach)](LICENSE)
[![Code Coverage](https://img.shields.io/codecov/c/github/walethewave/Confidence-Coach)](https://codecov.io/gh/walethewave/Confidence-Coach)
[![Security](https://img.shields.io/badge/security-scanned-brightgreen)](https://github.com/walethewave/Confidence-Coach/security)
[![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-orange)](https://streamlit.io/)

---

## 👋 Why ConfidenceAI? (The Problem)

As a developer and mentor, I’ve seen firsthand how self-doubt and lack of confidence can stall even the most talented people. Traditional self-help tools are generic, impersonal, and often fail to adapt to real, nuanced human struggles.

**ConfidenceAI** was born from a simple question:  
> _What if everyone could access a supportive, expert coach—anytime, anywhere, tailored to their unique journey?_

---

## 🚀 Solution Overview

**ConfidenceAI** is a next-generation, AI-powered confidence coach built with Streamlit, Pydantic, and Google Gemini. It combines advanced prompt engineering, explainable analytics, and a privacy-first design to deliver actionable, empathetic coaching—**not just pep talks**.

### **Key Innovations:**
- **Explainable AI**: Every confidence score is justified with transparent reasoning.
- **Real-Time Analytics**: Visualize your confidence journey and progress.
- **Dynamic Prompting**: Context-aware, human-like responses that adapt to your needs.
- **Privacy by Design**: All conversations are local and never shared.

---

## ✨ Key Features

- **Conversational AI Coaching**  
  Warm, supportive, and context-aware responses powered by Google Gemini.

- **Confidence Assessment**  
  Real-time scoring (1–10) with keyword analysis and AI validation.

- **Actionable Tips & Next Steps**  
  Extracts practical advice and micro-actions from every conversation.

- **Progress Tracking**  
  Visual charts and session analytics to monitor growth over time.

- **Motivational Quotes & Affirmations**  
  On-demand inspiration, tailored to your emotional state.

- **Goal Setting & Tracking**  
  Set, check off, and review daily goals—integrated into your coaching flow.

- **Exportable Sessions**  
  Download your entire chat history and analytics for personal review.

- **Explainable Reasoning**  
  Every AI decision is accompanied by human-readable explanations.

- **Cross-Platform**  
  Runs on Windows, macOS, and Linux (via Streamlit).

---

## ⚡ Quick Start

### 1. Installation

#### Using pip
```bash
pip install -r requirements.txt
````

#### Using Poetry

```bash
poetry install
```

#### Using Conda

```bash
conda env create -f environment.yml
conda activate confidenceai
```

### 2. Environment Setup

* Obtain a [Google Gemini API key](https://ai.google.dev/)
* Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your-gemini-api-key-here
```

### 3. Launch the App

```bash
streamlit run app.py
```

*The app will open in your browser at `http://localhost:8501`.*

---

## 🛠️ Documentation

*coming soon...*

---

## 🧪 Testing & Quality

* **Unit Tests**: All core logic is covered by unit tests (see `tests/`).
* **Type Safety**: Pydantic models enforce strict data validation.
* **Continuous Integration**: Automated builds and tests via GitHub Actions.
* **Code Coverage**: >90% coverage on business logic.
* **Security**: Dependencies scanned with Dependabot and Bandit.

### Running Tests

```bash
pytest
```

---

## 🖥️ Screenshots

|            Chat UI (Light)           |              Analytics Sidebar              |             Goal Setting            |
| :----------------------------------: | :-----------------------------------------: | :---------------------------------: |
| ![Chat UI](docs/screenshot_chat.png) | ![Analytics](docs/screenshot_analytics.png) | ![Goals](docs/screenshot_goals.png) |

---

## 🧩 Technical Decisions

* **Streamlit** for rapid, interactive UI prototyping and cross-platform support.
* **Pydantic** for robust data validation and type safety.
* **Google Gemini** for advanced, context-aware conversational AI.
* **Explainable AI**: Every confidence score is justified for transparency.
* **Session Export**: JSON format for easy analysis and privacy.

---

## 🚧 Roadmap

* [ ] **Multi-language Support** (i18n)
* [ ] **Voice Input & Output**
* [ ] **Mobile-Optimized UI**
* [ ] **Customizable Coaching Styles**
* [ ] **Integration with Journaling Apps**
* [ ] **Advanced Analytics (e.g., sentiment over time)**
* [ ] **Plugin System for Third-Party Tools**
* [ ] **OpenAPI/REST API for external integrations**

---

## 🛠️ Troubleshooting

| Issue                         | Solution                                                      |
| ----------------------------- | ------------------------------------------------------------- |
| `GEMINI_API_KEY` not found    | Ensure `.env` file is present and key is valid                |
| Streamlit app won't start     | Check Python version (3.8+), dependencies, and port conflicts |
| AI responses are generic      | Check API quota, network, or try restarting the app           |
| Exported session missing data | Ensure session is active and not reset before export          |

---

## 📈 Performance

* **Response Time**: \~1.2s avg (Gemini API, local testing)
* **Memory Usage**: <200MB (typical session)
* **Scalability**: Stateless backend, suitable for containerization

---

## 🤝 Contributing

We welcome contributions of all kinds!
**To get started:**

1. Fork the repo and clone locally.
2. Install dependencies (`pip install -r requirements.txt`).
3. Create a feature branch (`git checkout -b feature/your-feature`).
4. Write tests for your changes.
5. Submit a pull request with a clear description.

### Development Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run linting and formatting
black .
flake8 .
```

**Code Style:**

* Black for formatting
* Flake8 for linting
* 100% type annotations

---

## 🙏 Acknowledgments

* **Google Gemini** — for the conversational AI backbone
* **Streamlit** — for making rapid prototyping a joy
* **Pydantic** — for robust data validation
* **Type.fit API** — for motivational quotes
* Inspiration from the developer community and every user who’s ever struggled with self-doubt.

---

## 📚 Learning Outcomes

* Advanced prompt engineering for nuanced, human-like AI responses
* Explainable AI techniques for transparency in user-facing analytics
* Robust, type-safe data modeling with Pydantic
* Building privacy-first, exportable analytics in a conversational app
* End-to-end testing and CI/CD for Streamlit-based projects

---

## 👤 Author

**Afolabi Olawale**
AI Engineer | AI Enthusiast | Confidence Advocate
[GitHub](https://github.com/walethewave)

> *"I built ConfidenceAI because I believe everyone deserves a champion in their corner.
> If this project helps even one person take a step forward, it’s a win.
> I’m always open to feedback, collaboration, or just a chat about AI and human potential—reach out anytime!"*

---

## ⭐️ Feedback & Collaboration

If you find this project valuable, please ⭐️ star the repo, open issues, or submit PRs.
Let’s build a more confident world—one conversation at a time.

---

# AI-Powered-Confidence-Coaching-App


