from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)

def push(text):
    """Send notification via Pushover"""
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )


def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact details for follow-up"""
    push(f"Dezerv Lead: {name} ({email}) - Notes: {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    """Record questions that couldn't be answered"""
    push(f"Dezerv Unknown Question: {question}")
    return {"recorded": "ok"}

def record_conversation_end(name="Not provided", email="Not provided", summary="Conversation ended"):
    """Record when a conversation ends and send notification"""
    push(f"Dezerv Conversation Ended: {name} ({email}) - Summary: {summary}")
    return {"recorded": "ok"}

record_conversation_end_json = {
    "name": "record_conversation_end",
    "description": "ALWAYS use this tool when a user indicates they are ending the conversation (e.g., says goodbye, thanks, 'that's all', 'I'm done', etc.). Capture a brief summary of what was discussed.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The user's name if they provided it during the conversation"
            },
            "email": {
                "type": "string",
                "description": "The user's email if they provided it during the conversation"
            },
            "summary": {
                "type": "string",
                "description": "A brief summary of what was discussed in the conversation - topics covered, user's interests, questions asked, etc."
            }
        },
        "required": ["summary"],
        "additionalProperties": False
    }
}
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool when a user provides their email address to get in touch for more information or to schedule a consultation. Always ask for email when users express interest.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The Name and email address of the user who wants to get in touch"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Context about the conversation - what the user is interested in, their concerns, investment goals, etc."
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered accurately as you didn't have the specific information needed",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
    {"type": "function", "function": record_conversation_end_json}
]

    
class DezervAgent:

    def __init__(self):
        self.openai = OpenAI()
        self.company_name = "Dezerv Investments Private Limited"
        
        # Load system prompt from agent_context.txt
        context_path = "about/agent_context.txt"
        with open(context_path, "r", encoding="utf-8") as f:
            self.agent_context = f.read()
        
        # Load Full_Context.pdf
        self.full_context = ""
        try:
            reader = PdfReader("about/Full_Context.pdf")
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    self.full_context += text + "\n"
        except Exception as e:
            print(f"Warning: Could not load Full_Context.pdf: {e}")
        
        # Load latest_overview.pdf
        self.latest_overview = ""
        try:
            reader = PdfReader("about/latest_overview.pdf")
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    self.latest_overview += text + "\n"
        except Exception as e:
            print(f"Warning: Could not load latest_overview.pdf: {e}")

    def handle_tool_call(self, tool_calls):
        """Handle function/tool calls from the LLM"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self):
        """Build the complete system prompt"""
        system_prompt = self.agent_context
        
        # Add company context documents
        system_prompt += "\n\n══════════════════════════════════════\n"
        system_prompt += "COMPANY CONTEXT DOCUMENTS\n"
        system_prompt += "══════════════════════════════════════\n\n"
        
        if self.full_context:
            system_prompt += "## Full Context Document:\n"
            system_prompt += self.full_context + "\n\n"
        
        if self.latest_overview:
            system_prompt += "## Latest Overview Document:\n"
            system_prompt += self.latest_overview + "\n\n"
        
        # Additional instructions for tool usage
        system_prompt += "\n══════════════════════════════════════\n"
        system_prompt += "TOOL USAGE INSTRUCTIONS\n"
        system_prompt += "══════════════════════════════════════\n"
        system_prompt += "- Always try to guide users to provide their Name email for consultation scheduling.\n"
        system_prompt += "- Use record_user_details tool when user provides name email or expresses interest in getting in touch.\n"
        system_prompt += "- Use record_unknown_question tool if you cannot answer a question with the provided context.\n"
        system_prompt += "- IMPORTANT: When a user indicates they are ending the conversation (says goodbye, thanks, 'that's all', 'I'm done', etc.), ALWAYS use the record_conversation_end tool BEFORE responding. Include a brief summary of what was discussed, and any name/email if provided during the conversation.\n"
        system_prompt += "- Remember to maintain your professional, SEBI-compliant tone at all times.\n"
        
        return system_prompt
    
    def chat(self, message, history):
        """Handle chat messages and maintain conversation flow"""
        messages = [
            {"role": "system", "content": self.system_prompt()}
        ] + history + [
            {"role": "user", "content": message}
        ]
        
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        
        return response.choices[0].message.content


if __name__ == "__main__":
    # Change to the Dezerv_agent directory to ensure correct file paths
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    agent = DezervAgent()
    gr.ChatInterface(
        agent.chat,
        type="messages",
        title="Dezerv Wealth Manager AI",
        description="I'm Dezerv's AI Wealth Manager. I can help answer questions about our investment services and guide you toward scheduling a consultation with our experts."
    ).launch(share=True)