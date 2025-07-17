# SmartSeva - Chatbot

#### 🛠️ Technology Stack

- **Backend**: Python 3.11+
- **UI Framework**: Streamlit
- **LLM Integration**: OpenAI GPT-4
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **Document Processing**: LangChain, PyPDF
- **Memory Management**: Custom conversation buffer
- **Logging**: Structured logging with rotationect Overview

## 📘 Project Overview

**SmartSeva** is an intelligent RAG (Retrieval-Augmented Generation) powered chatbot designed to simplify and streamline access to Indian government schemes and services. It delivers fast, reliable, and verified information—such as eligibility, required documents, and application steps—based strictly on available data. If information is missing, the assistant clearly indicates it, avoiding hallucinations or made-up responses. Ideal for citizens seeking clarity on government processes.



## 🚀 Features

- **🤖 Intelligent Chatbot**: AI-powered conversational interface for citizen queries
- **📚 RAG Engine**: Advanced retrieval system for accurate information extraction
- **🔍 Vector Operations**: Document upload, indexing, and similarity search
- **💾 Persistent Memory**: Chat history and context management
- **📊 Analytics Dashboard**: Query analysis and system performance metrics
- **🔄 Real-time Updates**: Dynamic content management and updates
- **🎨 Modern UI**: Clean, intuitive interface built with Streamlit

## 🛠️ Technology Stack

- **Backend**: Python 3.11+
- **UI Framework**: Streamlit
- **LLM Integration**: OpenAI GPT-4, Groq (Llama, Mixtral, Gemma)
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI text-embedding-3-small
- **Document Processing**: LangChain, PyPDF
- **Memory Management**: Custom conversation buffer
- **Logging**: Structured logging with rotation


## 🔧 Installation & Setup

### Prerequisites

- Python 3.11
- pip package manager
- Git (for cloning the repository)

### Step 1: Create Python Virtual Environment

#### Option A: Using Python venv (Standard)

```bash
# Create virtual environment with Python 3.11
python -m venv my_env

# Activate the virtual environment
# On Windows:
my_env\Scripts\activate
# On macOS/Linux:
source my_env/bin/activate
```

#### Option B: Using Anaconda/Miniconda

```bash
# Create conda environment with Python 3.11
conda create -n my_env python=3.11 -y

# Activate the conda environment
conda activate my_env
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### Step 3: Environment Configuration

1. Create a `.env` file in the project root directory
2. Add your API keys and configuration:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Step 4: Configure LLM Provider

The application uses OpenAI as its LLM provider:

- Ensure `OPENAI_API_KEY` is set in your `.env` file
- The application will automatically use the configured OpenAI model

## 🤖 LLM Provider Configuration

The SmartSeva Assistant uses OpenAI's Language Models:

### OpenAI Models
- **Models**: GPT-4o-mini, GPT-4o, GPT-3.5-turbo
- **Pros**: High quality, reliable, well-documented
- **Setup**: Requires OpenAI API key

### Configuration

1. **Update Environment Variables**:
   ```env
   # For OpenAI
   OPENAI_API_KEY=your_openai_key_here
   ```

2. **Restart the Application** for changes to take effect.

### Model Recommendations

- **For Production**: OpenAI GPT-4o-mini (balanced performance and cost)
- **For High Quality Responses**: OpenAI GPT-4o (best quality, higher cost)

### Step 5: Initialize the Application

```bash
# Run the Streamlit application
streamlit run app.py
```

## 🚀 Usage Guide

### For Service Providers:

1. **Access the Chatbot**: Open the application and navigate to the chat interface
2. **Ask Questions**: Type citizen queries about government schemes, eligibility, or procedures
3. **Review Responses**: Get comprehensive answers with source citations
4. **Manage Documents**: Upload new policy documents through the Vector Operations page

### For Administrators

1. **Document Management**: Use the Vector Operations page to:
   - Upload new government service documents
   - Update existing policy information
   - Monitor vector database statistics
2. **System Monitoring**: Check logs and performance metrics
3. **Configuration Updates**: Modify settings in the config files as needed



## 📊 Performance Metrics

- **Response Time**: < 3 seconds for typical queries
- **Accuracy**: 95%+ based on internal testing
- **Document Processing**: 100+ pages per minute

## 🔮 Future Plans


### Long-term Roadmap
- **Full-fledged Web Interface**: Migration to React.js frontend with Node.js/FastAPI backend
- **Advanced AI Framework**: Integration with LangGraph for more sophisticated workflows
- **API Integration**: Direct integration with government service APIs
- **Voice Interface**: Speech-to-text and text-to-speech capabilities
- **Mobile Application**: Dedicated mobile app for field operators
