# 🧠 Learning Agent

An intelligent, autonomous, and adaptive Learning Management System powered by **NVIDIA NIM LLMs**, **FastAPI**, and **Next.js**.

---

## 🌟 Overview

The **Learning Agent** is a full-stack, AI-powered application designed to revolutionize how individuals approach self-directed learning. Instead of relying on static, one-size-fits-all courses, this platform uses advanced Large Language Models (specifically `meta/llama-3.1-8b-instruct` and `meta/llama-3.1-70b-instruct` via NVIDIA NIM) to dynamically generate, monitor, and adapt highly personalized learning journeys. 

Users simply input what they want to learn, their ultimate goal, and their current skill level. In seconds, the application's AI orchestrator parses this intent and formulates a comprehensive, multi-week curriculum broken down into actionable milestones and granular daily tasks (such as readings, videos, and quizzes). 

But the Learning Agent doesn't just generate a plan and leave you to it. It actively monitors your progress. If you ace your tasks, it accelerates your curriculum. If you struggle with a quiz, it autonomously revises your upcoming milestones to include remedial material. If you stop logging in, it sends intelligent "nudges" to get you back on track. 

---

## ✨ Key Features

### 1. 🤖 AI-Powered Intent Parsing & Curriculum Generation
- **Intelligent Onboarding:** The system uses NVIDIA NIM's ultra-fast Llama-3.1-8B model to intelligently parse raw, unstructured user input into a structured learning domain and target outcome.
- **Adaptive Plan Generation:** Using the heavy-hitting Llama-3.1-70B model, the agent generates a highly structured, step-by-step curriculum with estimated time commitments, specific task types, and logical progression.

### 2. 📊 Dynamic Dashboard & Interactive Workspace
- **Glassmorphism UI:** A sleek, modern, and immersive dark-mode interface built with Tailwind CSS and Framer Motion. 
- **Journey Timeline:** Visualize your multi-week learning plan at a glance, tracking active, delayed, and completed milestones.
- **Real-time Analytics:** Track your completion percentage, current daily streak, and a comparison of time invested versus time planned.
- **Multi-Course Support:** Manage multiple learning goals simultaneously. Easily swap between active courses or delete old ones directly from the sidebar.

### 3. 🔄 Autonomous Plan Revision
- **Performance-Based Adaptation:** If you fail a quiz or self-assessment, the backend AI agent detects the struggle and automatically proposes a curriculum revision to reinforce foundational concepts.
- **Diff Viewer:** Before accepting a revised plan, users are presented with a beautiful visual "diff" showing exactly what tasks were added, removed, or modified by the AI.

### 4. 🔔 Intelligent Nudge System
- **Proactive Interventions:** A background scheduler actively monitors user engagement. If it detects inactivity or a slipping schedule, it generates personalized, contextual "nudges" to encourage the user to return to their studies.

### 5. 🛠️ Developer Debug Controls
- Built-in UI controls to instantly simulate edge cases like 3-day inactivity, low quiz scores, schedule slips, and early task completions, making testing and showcasing the AI's reactive capabilities effortless.

---

## 🏗️ Architecture & Tech Stack

The project is structured as a decoupled monorepo containing a Python backend and a React frontend.

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS + Custom CSS Variables
- **Animations:** Framer Motion
- **Icons:** Lucide React
- **Data Fetching:** Axios

### Backend
- **Framework:** FastAPI (Python 3.12+)
- **Database:** SQLite (managed via SQLAlchemy ORM)
- **AI Integration:** OpenAI Python SDK (configured to route to NVIDIA NIM APIs)
- **Concurrency:** Asyncio for non-blocking LLM calls

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- An **NVIDIA API Key** (to access NIM endpoints)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -e .
   ```
4. Configure Environment Variables:
   Copy `.env.example` to `.env` and insert your NVIDIA API key:
   ```env
   NVIDIA_API_KEY=nvapi-your-key-here
   ```
5. Initialize the database and run the server:
   ```bash
   python init_db.py
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will now be running at `http://localhost:8000`.

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:3000`.

---

## 📖 Deep Dive: How the AI Agent Works

The "Agentic" nature of this application relies on a multi-agent backend architecture found in `backend/app/agents/`.

1. **`intent_parser.py`**: A fast, lightweight agent that uses a rigidly typed JSON schema to extract the exact domain, skill level, and ultimate goal from a casual user prompt.
2. **`plan_generator.py`**: The heavy lifter. It receives the parsed intent and uses a massive system prompt to generate a JSON-compliant curriculum. It strictly enforces rules like "no more than 3 tasks per milestone" and "realistic time estimates."
3. **`plan_reviser.py`**: The reactive agent. Triggered by the `simulate` routes (or actual user failure in a production scenario), this agent takes the *current* state of the plan and the *reason* for revision (e.g., "User scored 45% on VPC Quiz"), and outputs a modified JSON plan that addresses the weakness without entirely derailing the original timeline.
4. **`nudge_composer.py`**: The motivational agent. It takes the user's current progress and the type of trigger (e.g., "inactivity") to write a short, encouraging notification tailored specifically to what the user is currently learning.

---

## 🛣️ Roadmap & Future Enhancements

While the Learning Agent is currently a robust prototype, several features are planned for future development:

- **Authentication & Multi-Tenancy:** Implement JWT-based auth (e.g., NextAuth or Supabase) to support multiple real users. Currently, the system assumes a single hardcoded user (`user_id = 1`) for demonstration purposes.
- **Interactive Quizzes:** Replace the simulated quiz scores with an actual AI-generated quiz interface where users answer multiple-choice or free-text questions.
- **RAG Integration:** Allow users to upload their own PDFs or link to specific documentation, using Retrieval-Augmented Generation to ensure the AI's curriculum is based entirely on the provided source material.
- **Push Notifications:** Integrate Web Push or a mobile app wrapper to deliver the AI's "nudges" directly to the user's device when they are away from the keyboard.
- **PostgreSQL Migration:** Move from SQLite to PostgreSQL to handle higher concurrency and complex analytical queries.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, better AI prompts, or UI enhancements, please feel free to fork the repository and submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
*Built with ❤️ and AI.*