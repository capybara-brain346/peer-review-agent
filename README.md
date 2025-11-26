## Peer Review Agent

This is a peer review system for blog posts and technical content. It acts like a professional editor who reads your content, fact-checks claims, provides structured feedback, and remembers past reviews to track your progress over time. The system can verify information against both uploaded source materials and external web searches.

<img width="1224" height="984" alt="diagram-export-11-26-2025-4_42_32-PM" src="https://github.com/user-attachments/assets/e218ff6b-e33f-423b-b549-4fc1396d8e93" />

### Why does this exist?

Writing quality content requires thorough fact-checking, style review, and consistency. This agent automates the peer review process by combining multiple verification methods: checking against your uploaded reference materials, searching the web for external facts, and maintaining memory of past feedback to catch recurring issues and track improvement.

### Model flexibility

The system is provider-agnostic and works with Gemini, OpenAI, Claude, or local Ollama models. Switch between providers by changing a single environment variable - no code modifications required. This gives you the freedom to use the most cost-effective, performant, or private option for your needs.

### How it works

The system uses Google's ADK (Agent Development Kit) with your choice of LLM provider (Gemini, OpenAI, Claude, or local Ollama models) to create a sophisticated review agent. When you submit content for review:

1. The agent fetches the content (from text input or URL)
2. Retrieves past review history for your project using Mem0 memory system
3. Searches through your uploaded source documents using semantic search
4. Fact-checks external claims using Google search via a sub-agent
5. Analyzes content for accuracy, clarity, tone, structure, and recurring issues
6. Generates a structured report with major/minor issues and line-by-line comments
7. Stores the review in memory for future reference

### Architecture overview

The application has several key components working together:

Agent Core (agent/agent.py)
The main LLM agent that can be configured with any supported model provider. Supports Gemini (default), OpenAI GPT models, Anthropic Claude, or local Ollama models via LiteLLM. Simply change the MODEL_PROVIDER environment variable to switch between providers. The agent orchestrates the review process and has access to multiple tools.

Tools (agent/tools.py)

- fetch_url_context: Extracts clean text content from web URLs
- retrieve_source_context: Searches through uploaded source documents
- get_current_datetime: Provides temporal context for time-sensitive claims

Sub-agents (agent/sub_agents/)

- google_search_agent: Dedicated agent for performing Google searches to verify external facts

Source Manager (agent/source_manager.py)
Manages a knowledge base of reference materials. Uses ChromaDB for vector storage and HuggingFace embeddings (all-MiniLM-L6-v2) to enable semantic search. Documents are chunked and indexed so the agent can retrieve relevant context during reviews.

Memory Manager (agent/memory.py)
Tracks review history per project/blog using Mem0. This enables the agent to identify recurring issues, track author improvement, and provide personalized feedback based on past interactions.

Schemas (agent/schemas.py)
Defines the structured output format using Pydantic models:

- PeerReviewReport: Overall review structure
- MajorIssue: Critical problems with evidence
- LineByLineComment: Granular feedback on specific text

Web Interface (app.py)
Streamlit-based UI for uploading sources, submitting content, viewing reports, and downloading PDFs.

### Installation and setup

**Requirements:**

- Python 3.12 or higher
- API key for your chosen LLM provider (Gemini, OpenAI, Claude, or none for local Ollama)
- UV package manager (recommended) or pip

Step 1: Clone and navigate to the project

```
git clone <repository-url>
cd peer-review-agent
```

Step 2: Install dependencies

Using UV (recommended):

```
uv sync
```

Using pip:

```
pip install -r pyproject.toml
```

Note: UV is preferred as it handles dependency resolution more efficiently.

Step 3: Set up environment variables

Create a .env file in the project root. Choose ONE of the following configurations based on your preferred LLM provider:

For Google Gemini (default, no MODEL_PROVIDER needed):

```
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

For OpenAI:

```
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4
```

For Anthropic Claude:

```
MODEL_PROVIDER=claude
ANTHROPIC_API_KEY=your_anthropic_key
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

For local Ollama:

```
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

You can freely switch between providers by changing the MODEL_PROVIDER variable and providing the appropriate API key. If MODEL_PROVIDER is not set or set to "gemini", the system uses Google Gemini by default.

Step 4: Verify installation

The first run will download the HuggingFace embedding model (all-MiniLM-L6-v2) automatically. This is about 80MB and only happens once.

Running the application

Start the Streamlit web interface:

```
streamlit run app.py
```

The app will open in your browser at http://localhost:8501

### Using the system

**Basic workflow:**

<img width="1517" height="1872" alt="diagram-export-11-26-2025-4_44_32-PM" src="https://github.com/user-attachments/assets/600b1f08-be65-4665-a7ca-9642aebe9469" />

1. Upload source materials
   In the sidebar, upload text or markdown files that contain reference information. These could be research papers, documentation, data sheets, or any authoritative content you want the agent to verify against. Click "Ingest Source" to add them to the knowledge base.

2. Enter project/blog name
   Give your project a unique identifier. This is used to track review history. All reviews for the same project name will build on each other.

3. Submit content for review
   Use either:

- Text Input tab: Paste your blog content directly
- URL Input tab: Enter a URL and the agent will fetch the content

4. Run review
   Click "Run Review" and wait. The agent will:

- Fetch content if needed
- Search your uploaded sources
- Fact-check claims via Google
- Review past feedback for this project
- Generate a comprehensive report

5. Review the report
   The report includes:

- Summary: High-level assessment
- Recommendation: Editor's note (publish/reject/revise)
- Major Issues: Critical problems with evidence links
- Minor Issues: Smaller nitpicks
- Line-by-line Comments: Specific feedback on quoted text

6. Download PDF
   Export the review as a PDF for offline reference or sharing.

### Understanding the review process

Phase 1: Ingestion

- Fetches content from URLs if needed
- Loads past review history for the project
- Examines uploaded source documents

Phase 2: Verification

- Identifies all factual claims in the content
- Searches uploaded sources for supporting evidence
- Uses Google search for external fact-checking
- Validates technical assertions and statistics

Phase 3: Evaluation

- Assesses clarity, flow, and structure
- Checks accuracy against evidence
- Evaluates tone for target audience
- Compares to past feedback to track improvement
- Flags recurring issues with escalated severity

Phase 4: Synthesis

- Generates structured report
- Provides evidence for all major issues
- References past feedback when relevant
- Gives actionable, constructive feedback

### Memory and learning

The memory system (Mem0) stores every review. For each project:

- Past issues are tracked
- Improvement patterns are recognized
- Recurring problems are escalated
- Author-specific feedback is personalized

This means the more you use it with the same project name, the smarter and more personalized the feedback becomes.

Source context and knowledge base

Uploaded sources are:

- Split into 800-character chunks with 200-character overlap
- Embedded using HuggingFace transformers
- Stored in ChromaDB vector database
- Searched semantically during reviews

The agent automatically retrieves relevant chunks when reviewing content. This ensures claims are verified against YOUR source materials first before checking external sources.

Project structure

```
peer-review-agent/
├── agent/
│   ├── __init__.py
│   ├── agent.py                    # Main agent definition
│   ├── schemas.py                  # Output data models
│   ├── tools.py                    # Tool functions
│   ├── memory.py                   # Memory management
│   ├── source_manager.py           # Knowledge base
│   ├── prompts/
│   │   └── peer_reviewer_prompt.py # Agent system instructions
│   ├── sub_agents/
│   │   └── google_search_agent.py  # Search sub-agent
│   ├── utils/
│   │   ├── logger.py               # Logging configuration
│   │   └── pdf_generator.py       # PDF export
│   ├── source_store/               # ChromaDB vector store (created on first run)
│   └── memory_store/               # Mem0 storage (created on first run)
├── logs/                           # Application logs
├── app.py                          # Streamlit web interface
├── pyproject.toml                  # Dependencies
├── uv.lock                         # Locked dependencies
├── .env                            # Environment variables (create this)
└── README.md                       # This file
```

Configuration details

Model selection and flexibility:

The system is designed to work with any LLM provider. You can freely switch between models by changing a single environment variable. Set MODEL_PROVIDER in .env to choose your LLM:

- gemini (default): Uses Google's Gemini models (gemini-2.5-flash, gemini-1.5-pro, etc.)
- openai: Uses OpenAI GPT models (gpt-4, gpt-3.5-turbo, etc.)
- claude: Uses Anthropic Claude models (claude-3-5-sonnet, claude-3-opus, etc.)
- ollama: Uses locally hosted Ollama models (llama2, mistral, codellama, etc.)

Each provider is integrated via LiteLLM, which provides a unified interface. To switch models:

1. Update MODEL_PROVIDER in your .env file
2. Set the appropriate API key (if using cloud providers)
3. Optionally specify the exact model name (e.g., GEMINI_MODEL=gemini-1.5-pro)
4. Restart the application

No code changes needed - the system automatically adapts to your chosen provider.

Model recommendations:

- Gemini-2.5-flash: Fast, cost-effective, good quality (default)
- GPT-4: High quality, more expensive, slower
- Claude-3-5-sonnet: Excellent reasoning, good balance of speed and quality
- Ollama (llama2/mistral): Completely private, no API costs, requires local compute

You can experiment with different models to find the best balance of cost, speed, and quality for your use case.

Memory configuration:

The memory system uses:

- ChromaDB for vector storage
- HuggingFace embeddings (all-MiniLM-L6-v2)
- Gemini-2.5-flash for memory synthesis (currently hardcoded, separate from main agent model choice)
- Local persistence in agent/memory_store/

Note: The main peer review agent can use any provider, but the Mem0 memory system currently uses Gemini for processing stored memories. This is independent of your main agent's model choice.

Storage locations:

- Source documents: agent/source_store/
- Review memory: agent/memory_store/
- Application logs: logs/
- All data persists between runs

Dependencies explained

Core dependencies:

- google-adk: Agent Development Kit for building AI agents
- streamlit: Web interface
- mem0ai: Memory management for agents
- chromadb: Vector database for semantic search
- langchain: Document processing and text splitting
- langchain-huggingface: Embedding models
- beautifulsoup4: HTML parsing for URL fetching
- reportlab: PDF generation
- python-dotenv: Environment variable management

Troubleshooting

Issue: "Failed to initialize SourceManager"
Solution: Ensure sufficient disk space for ChromaDB. First run downloads embeddings.

Issue: "Agent did not produce a response"
Solution: Check API key in .env matches your MODEL_PROVIDER. Verify internet connection if using cloud LLM providers (Gemini, OpenAI, Claude).

Issue: Memory errors or CUDA issues
Solution: System uses CPU by default. Set PYTORCH_ENABLE_MPS_FALLBACK=1 is already configured.

Issue: Vector store errors
Solution: Delete agent/source_store/ and agent/memory_store/ directories to reset databases.

Advanced usage

Switching models on the fly:

You can change models anytime by updating your .env file and restarting the app. The agent configuration in agent/agent.py reads environment variables at startup, making it simple to test different models for quality, cost, or speed comparisons.

Custom prompts:

Edit agent/prompts/peer_reviewer_prompt.py to customize review criteria and agent behavior.

Different embedding models:

In source_manager.py and memory.py, change the model_name from "all-MiniLM-L6-v2" to any HuggingFace embedding model.

Adding custom tools:

In agent/tools.py, add new functions and register them in agent/agent.py tools list.

Batch processing:

Import and use the run_peer_review_async function directly for batch processing multiple documents programmatically.

API integration:

The PeerReviewer class in app.py can be imported and used in other Python applications:

```
from app import peer_reviewer
report = peer_reviewer.review_blog("project_name", "content here")
```

The model used will be determined by your environment variables, making it easy to deploy with different LLM backends in different environments (e.g., GPT-4 in production, local Ollama for development).
