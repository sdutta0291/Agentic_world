# Dezerv Wealth Manager AI Agent

## Overview

The Dezerv Wealth Manager AI Agent is a client-facing virtual assistant designed to represent Dezerv Investments Private Limited. Built using OpenAI's GPT-4o-mini model, this agent engages with potential and existing clients, answers questions about Dezerv's investment services, and guides users toward scheduling consultations with human wealth management experts.

The agent is designed to maintain a professional, SEBI-compliant tone while providing accurate information about Dezerv's Portfolio Management Services (PMS), investment strategies, and wealth management philosophy.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Gradio Web Interface                     │
│              (User Chat Interface - Browser)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   DezervAgent Class                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Initialization (__init__)                           │   │
│  │  - Loads agent_context.txt (System Prompt)           │   │
│  │  - Loads Full_Context.pdf                            │   │
│  │  - Loads latest_overview.pdf                         │   │
│  │  - Initializes OpenAI Client                         │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  System Prompt Builder (system_prompt)               │   │
│  │  - Combines agent context with PDF documents         │   │
│  │  - Adds tool usage instructions                      │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Chat Handler (chat)                                 │   │
│  │  - Processes user messages                           │   │
│  │  - Maintains conversation history                    │   │
│  │  - Handles tool calls (function calling)             │   │
│  │  - Returns LLM responses                             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tool Call Handler (handle_tool_call)                │   │
│  │  - Executes function tools                           │   │
│  │  - Returns tool results to LLM                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenAI API (GPT-4o-mini)                       │
│  - Processes messages with system prompt                    │
│  - Performs function calling for tools                      │
│  - Returns natural language responses                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Function Tools                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  record_user_details(email, name, notes)             │   │
│  │  → Sends notification via Pushover                   │   │
│  │  → Records lead information                          │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  record_unknown_question(question)                   │   │
│  │  → Logs unanswered questions                         │   │
│  │  → Sends notification via Pushover                   │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  record_conversation_end(name, email, summary)       │   │
│  │  → Logs conversation endings                         │   │
│  │  → Sends notification via Pushover                   │   │
│  │  → Captures conversation summary                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘                       

```

## Key Components

### 1. Core Agent Class (`DezervAgent`)

The main class that orchestrates the entire agent system.

**Key Methods:**
- `__init__()`: Initializes the agent, loads all context documents
- `system_prompt()`: Constructs the complete system prompt by combining agent context and PDF documents
- `chat()`: Main chat handler that processes user messages and maintains conversation flow
- `handle_tool_call()`: Executes function tools requested by the LLM

### 2. Context Management

The agent uses three primary sources of context:

1. **Agent Context (`about/agent_context.txt`)**: 
   - Core identity and personality guidelines
   - SEBI compliance rules
   - Conversation frameworks
   - Regulatory constraints
   - Tone and language guidelines

2. **Full Context Document (`about/Full_Context.pdf`)**:
   - Comprehensive company information
   - Detailed product offerings
   - Investment strategies documentation

3. **Latest Overview (`about/latest_overview.pdf`)**:
   - Recent updates and overviews
   - Current market positioning
   - Latest service information

### 3. Function Tools

The agent has access to three function tools that enable it to interact with external systems:

#### `record_user_details`
- **Purpose**: Captures user contact information for lead generation
- **Parameters**: 
  - `email` (required): User's email address
  - `name` (optional): User's name
  - `notes` (optional): Conversation context and interests
- **Action**: Sends notification via Pushover API

#### `record_unknown_question`
- **Purpose**: Logs questions that couldn't be answered
- **Parameters**:
  - `question` (required): The unanswered question
- **Action**: Logs the question for review and sends notification

#### `record_conversation_end`
- **Purpose**: Records when a conversation ends and captures a summary for follow-up analysis
- **Parameters**:  
   - `summary` (required): A brief summary of what was discussed in the conversation  - `name` (optional): The user's name if provided during the conversation  - `email` (optional): The user's email if provided during the 
- **Action**: Sends notification via Pushover API with conversation summary
- **When to use**: Automatically triggered when a user indicates they are ending the conversation (e.g., says goodbye, thanks, "that's all", "I'm done", etc.)
- **Background**: This tool ensures that every conversation interaction is tracked and analyzed. When users end their conversation, the agent automatically captures:  
   - Topics discussed during the conversation  
   - User interests and concerns  
   - Questions asked  
   - Any contact information provided  
   - Overall conversation context

**This enables the Dezerv team to**:  
   - Track engagement patterns  
   - Identify common questions and concerns  
   - Follow up with interested prospects  
   - Improve the agent's knowledge base  
   - Analyze conversation quality and effectiveness

### 4. External Services

- **OpenAI API**: Powers the LLM capabilities
- **Pushover API**: Sends notifications for:
  - Lead capture (`record_user_details`)
  - Unanswered questions (`record_unknown_question`)
  - Conversation endings (`record_conversation_end`)
- **Gradio**: Provides the web-based chat interface

## File Structure

```
Dezerv_agent/
├── dezerv_agent.py          # Main agent implementation
├── web_scraper.py           # Utility script for web scraping (separate tool)
├── test.ipynb               # Testing notebook for development
├── README.md                # This file
└── about/
    ├── agent_context.txt    # Core system prompt and guidelines
    ├── Full_Context.pdf     # Comprehensive company context
    └── latest_overview.pdf  # Latest company overview
```

## Setup and Installation

### Prerequisites

1. Python 3.8 or higher
2. OpenAI API key
3. Pushover account (optional, for notifications)
4. Required Python packages

### Installation Steps

1. **Install dependencies:**
   ```bash
   pip install openai python-dotenv requests pypdf gradio
   ```

2. **Set up environment variables:**
   Create a `.env` file in the parent directory with:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_TOKEN=your_pushover_token (optional)
   PUSHOVER_USER=your_pushover_user (optional)
   ```

3. **Ensure PDF files are in place:**
   - Verify `about/Full_Context.pdf` exists
   - Verify `about/latest_overview.pdf` exists
   - Verify `about/agent_context.txt` exists

### Running the Agent

```bash
cd assistant_SD/Dezerv_agent
python dezerv_agent.py
```

The agent will launch a Gradio web interface. By default, it runs with `share=True`, which creates a publicly accessible link.

## How It Works

### Conversation Flow

1. **User sends a message** via the Gradio interface
2. **System constructs prompt** by combining:
   - Agent context (personality, rules, guidelines)
   - PDF documents (company information)
   - Conversation history
   - Current user message

3. **LLM processes the request**:
   - Analyzes the message
   - Determines if tools need to be called
   - Generates appropriate response

4. **Tool execution** (if needed):
   - LLM requests a tool (e.g., `record_user_details`)
   - Agent executes the tool function
   - Tool results are returned to LLM
   - LLM incorporates results into response
   - **Special case**: When user indicates conversation ending, `record_conversation_end` is automatically called to log the interaction

5. **Response delivery**:
   - Final response is sent back to user
   - Conversation history is maintained for context

### System Prompt Construction

The system prompt is dynamically built from:

```
[Agent Context from agent_context.txt]
+ 
[Full Context PDF content]
+
[Latest Overview PDF content]
+
[Tool Usage Instructions]
```

This ensures the LLM has comprehensive knowledge of:
- How to behave (from agent_context.txt)
- What Dezerv offers (from PDFs)
- How to use tools (from instructions)

## Key Features

### 1. SEBI Compliance
- Never provides personalized investment advice
- Never guarantees returns
- Always emphasizes risk
- Uses compliant language ("subject to market risks", etc.)

### 2. Professional Tone
- Calm, professional, and reassuring
- Sophisticated but simple language
- Never salesy or casual
- Avoids emojis and slang

### 3. Lead Generation
- Proactively asks for user contact information
- Records leads with conversation context
- Guides users toward consultations

### 4. Knowledge Management
- Comprehensive company knowledge from PDFs
- Handles unknown questions gracefully
- Logs gaps in knowledge for improvement

### 5. Context Awareness
- Maintains conversation history
- Remembers user's name and interests
- Adapts responses based on conversation flow

### 6. Conversation Tracking
- Automatically detects when conversations end
- Captures conversation summaries for analysis
- Tracks user engagement patterns
- Enables follow-up opportunities
- Provides insights for continuous improvement

## Configuration

### Model Configuration

Currently uses `gpt-4o-mini`. To change the model:

```python
response = self.openai.chat.completions.create(
    model="gpt-4",  # Change model here
    messages=messages,
    tools=tools
)
```

### Notification Configuration

To enable/disable Pushover notifications, modify the `push()` function or set environment variables.

### PDF Loading

The agent automatically loads PDFs on initialization. If a PDF fails to load, a warning is printed but the agent continues running.

## Development and Testing

### Testing in Notebook

Use `test.ipynb` for interactive testing and development.

### Separate Web Scraper Tool

The `web_scraper.py` file contains a separate utility for web scraping using the OpenAI Agents SDK. This is independent of the main Dezerv agent and can be used for research purposes.

## Compliance and Safety

### Regulatory Compliance

- **SEBI Awareness**: Agent is programmed to be aware of SEBI regulations
- **No Personalized Advice**: Never provides specific investment recommendations
- **Risk Disclosure**: Always mentions market risks
- **Deferral to Experts**: Directs complex questions to human experts

### Data Privacy

- User emails are captured only when explicitly provided
- All data transmission uses secure APIs (OpenAI, Pushover)
- No data is stored locally beyond conversation history in Gradio session

## Troubleshooting

### Common Issues

1. **PDF files not loading:**
   - Check file paths are correct
   - Verify PDF files exist in `about/` directory
   - Check file permissions

2. **OpenAI API errors:**
   - Verify API key in `.env` file
   - Check API quota and billing
   - Verify network connectivity

3. **Pushover notifications not working:**
   - Verify `PUSHOVER_TOKEN` and `PUSHOVER_USER` in `.env`
   - Check Pushover account status
   - Agent will continue working even if notifications fail

## Future Enhancements

Potential improvements:
- Integration with CRM systems for lead management
- Support for multiple languages
- Enhanced conversation analytics
- Integration with Dezerv's internal knowledge base
- Voice interface support
- Multi-modal capabilities (image/document upload)

## Author / Creator

**Soumya Dutta**

- **Role**: Senior Data Architect
- **Background**: Engineer and avid learner with expertise in data architecture and AI/ML solutions
- **Location**: Bangalore, India
- **Expertise**: 
  - Data Architecture & Engineering
  - AI/ML Agent Development
  - Personal Finance & Investment Technology
  - Building client-facing AI applications

This agent was developed as part of an initiative to create intelligent, compliant, and user-friendly AI assistants for the financial services industry. The implementation focuses on SEBI compliance, professional communication, and seamless integration of company knowledge bases.

## License and Credits

Built for Dezerv Investments Private Limited.

Developed by Soumya Dutta.
🔗 LinkedIn: linkedin.com/in/iamsoumyadutta

Based on OpenAI's GPT models and Gradio framework.

## Support

For issues or questions, contact s.dutta0291@gmail.com or refer to the agent's source code for implementation details.

