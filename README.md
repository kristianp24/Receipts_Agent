# Receipts Agent

## Tech Stack
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-blue?logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-grey?logo=graphql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-yellow?logo=--&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-green?logo=--&logoColor=white)


An intelligent agent for processing, understanding, and querying receipt and bill documents. This agent can parse PDF receipts, extract structured information, store it in a vector database, and answer questions about the stored documents. !! For the moment the query part of the database is still to be implemented in the coming day !!

This project is mainly for personal use for my day to day receipts from food merchants and utility bills from Iren (An gas/electricity provider in Turin, Italy.), so it will not work on every utility bill possible yet.

## Features

- **PDF Document Processing**: Ingests PDF files containing receipts or bills.
- **Receipt Type Classification**: Automatically determines the type of bill (e.g., Gas, Electricity, Grocery).
- **Structured Data Extraction**: Uses large language models (LLMs) to extract key information like vendor name, due date, total amount, and detailed line items.
- **Vector-Based Storage**: Stores extracted data in a ChromaDB collection for efficient similarity search.
- **Natural Language Querying**: Allows users to ask questions about their bills (e.g., "show me my bills from Vendor X").

## How it Works

The agent is built as a state machine using [LangGraph](https://github.com/langchain-ai/langgraph). The workflow is as follows:

1.  **Intent Recognition**: The agent first determines the user's intent. If a PDF document is provided, it proceeds to the document processing pipeline. If a text query is given, it routes to the query handler.

2.  **Document Processing Pipeline**:
    - **Parse**: The PDF is converted into raw text.
    - **Classify**: The bill type is identified.
    - **Chunk**: Relevant sections of the text are selected for processing.
    - **Reason**: An LLM extracts structured data based on a sophisticated prompt and Pydantic models.
    - **Format**: The extracted data is transformed into a text format suitable for embedding.
    - **Store**: The formatted text and associated metadata are saved to a ChromaDB database.

3.  **Query Handling**:
    - The agent extracts key information (like a vendor name) from the user's query.
    - It then searches the ChromaDB database for relevant documents and returns the findings.

## Technologies Used

- **Backend**: Python
- **LLM Orchestration**: [LangChain](https://www.langchain.com/) & [LangGraph](https://github.com/langchain-ai/langgraph)
- **LLM Provider**: [Groq](https://groq.com/) for high-speed inference (using Llama models)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Data Modeling**: [Pydantic](https://pydantic.dev/)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Receipts_Agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the dependencies:**
    *(Note: A `requirements.txt` file should be created for this project)*
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```
    GROQ_KEY="your_groq_api_key"
    CHROMA_DB_KEY="your_chromadb_api_key"
    CHROMA_DB_TENANT="your_chromadb_tenant"
    ```

## Usage

The agent can be used as a library within a larger application. You would initialize the `ReceiptAgent` and then invoke its graph with the appropriate state.

**Example: Processing a document**
```python
from agent.agent import ReceiptAgent

# Initialize the agent
receipt_agent = ReceiptAgent()

# Define the initial state with the path to the PDF
initial_state = {
    "pdf_document": "/path/to/your/receipt.pdf",
    "user_input": [] 
}

# Run the agent
for output in receipt_agent.graph.stream(initial_state):
    for key, value in output.items():
        print(f"Output from node '{key}':")
        print("--- ")
        print(value)
    print("\n---\n")
```

**Example: Querying documents**
```python
from agent.agent import ReceiptAgent
from langchain_core.messages import HumanMessage

# Initialize the agent
receipt_agent = ReceiptAgent()

# Define the initial state with a user query
initial_state = {
    "pdf_document": None,
    "user_input": [HumanMessage(content="Find all bills from Iren")] 
}

# Run the agent
for output in receipt_agent.graph.stream(initial_state):
    for key, value in output.items():
        print(f"Output from node '{key}':")
        print("--- ")
        print(value)
    print("\n---\n")

```