# MultiAgent Boilerplate

## Overview

**MultiAgent Boilerplate** is a production-grade implementation of AI agents with tool integrations, designed for customer journey automation in cloud services and managed IT. The system leverages FastAPI, LangChain, and ChromaDB to deliver a robust, extensible platform for conversational AI, workflow orchestration, and business process automation.

---

## Key Features

- **AI Agent Orchestration:** Modular, extensible agent architecture for handling customer journeys, onboarding, appointment scheduling, and expert matching.
- **Tool Integration:** Agents interact with tools for onboarding, specialist search, appointment booking, case studies, testimonials, and conversation summarization.
- **State Management:** Strict protocols for ID management, consent capture, and conversation state tracking.
- **Summarization Protocol:** Automatic summarization of conversations at critical milestones (e.g., after appointment booking or when key business topics are discussed).
- **WebSocket Support:** Real-time communication with clients using FastAPI WebSocket endpoints.
- **Production-Grade Logging:** Centralized logging for traceability and debugging.
- **Vector Database:** ChromaDB integration for semantic search over case studies and testimonials.
- **Extensible Prompts:** System prompts enforce business rules, consent protocols, and summarization logic.

---

## Customer Journey Flow

1. **First Impression & Trust**
   - AI agent introduces itself and the company.
   - Adapts tone to customer role (CTO, Developer, Business, etc.).
   - Discovers customer goals, pain points, and requirements.

2. **Conversion & Engagement**
   - Provides case studies and testimonials as proof.
   - Enforces explicit consent before onboarding.
   - Onboards customer and stores IDs for future tool calls.
   - Matches customer with specialists and schedules appointments.

3. **Solution Alignment**
   - Maps challenges to solutions (migration, modernization, cost optimization, cloud ops).
   - Presents tailored solutions and company strengths.

4. **Retention & Up-sell**
   - Offers managed services, SLAs, and follow-up engagements.

---

## Critical Protocols

- **ID Management:** Always use exact IDs returned by tools. Never invent IDs.
- **Consent Protocol:** Onboarding only after explicit, affirmative consent.
- **Summarization Protocol:** Summarize conversation only after appointment booking or when key business topics are mentioned (see full keyword list in `prompts/planner_prompts.py`).
- **Tool Usage:** Agents only call tools when protocols are satisfied. Never hallucinate data or responses.

---

## Tooling

- **Case Studies Tool:** Semantic search and retrieval of company case studies.
- **Testimonials Tool:** Semantic search and retrieval of customer testimonials.
- **Onboard Customer Tool:** Creates customer profiles after explicit consent.
- **Summarize Conversation Tool:** Extracts structured summaries for CRM and analytics.
- **Specialist Availability Tool:** Matches customer needs to available specialists.
- **Appointment Tools:** Checks availability and books appointments.

---

## Technology Stack

- **FastAPI**: High-performance API and WebSocket server.
- **LangChain**: Agent orchestration and tool integration.
- **ChromaDB**: Vector database for semantic search.
- **Redis**: State management and checkpointing.
- **Python**: Core language for all backend logic.

---

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Set up `.env` with required keys (OpenAI, Google, Redis, etc.).
   - Place your case studies and testimonials in the respective folders.

3. **Populate vector databases:**
   ```bash
   python populate_casestudies.py
   python populate_testimonials.py
   ```

4. **Run the server:**
   ```bash
   python fastapi_app.py
   ```

5. **Access the chat interface:**
   - Open your browser to `http://localhost:8000`

---

## Enforcement & Best Practices

- **Never skip consent or ID protocols.**
- **Never hallucinate case studies, testimonials, or IDs.**
- **Always respond in the customer's language.**
- **Keep answers short, clear, and role-appropriate.**
- **Silent summarization:** Never mention summarization to the customer.

---

## Extending the System

- Add new tools by implementing them in the `agent_tools` directory.
- Update prompts and protocols in `prompts/planner_prompts.py`.
- Integrate new data sources by updating vector database scripts.

---

## License

This project is intended for production use and can be adapted for commercial deployments. Please review and comply with all third-party licenses for dependencies.

---

## Contact

For support, customization, or enterprise deployments, contact the maintainers or open an issue