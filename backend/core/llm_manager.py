import os
import time
import google.generativeai as genai
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import requests
import openai
from .currency_converter import convert_currency


class LLMProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    LOCAL = "local"


class ToolCall:
    """Represents a tool call with name and arguments"""

    def __init__(self, name: str, arguments: Dict[str, Any]):
        self.name = name
        self.arguments = arguments

    def execute(self) -> Any:
        """Execute the tool call"""
        if self.name == "currency_converter":
            amount = self.arguments.get("amount", 0)
            from_currency = self.arguments.get("from_currency", "USD")
            to_currency = self.arguments.get("to_currency", "INR")
            return convert_currency(amount, from_currency, to_currency)
        elif self.name == "get_current_time":
            return time.strftime("%Y-%m-%d %H:%M:%S")
        elif self.name == "calculate":
            expression = self.arguments.get("expression", "")
            # Safe evaluation of simple math expressions
            try:
                # Only allow numbers, operators, and decimal points
                if re.match(r'^[0-9+\-*/().\s]+$', expression):
                    return eval(expression)
                else:
                    return "Invalid expression"
            except:
                return "Calculation error"
        else:
            return f"Unknown tool: {self.name}"


class LLMManager:
    """
    Manages multiple LLM providers with fallback mechanisms and tool calling
    """

    def __init__(self):
        self.providers = {}
        self.active_provider = None
        self.tool_registry = {}
        self._setup_providers()
        self._register_default_tools()

    def _setup_providers(self):
        """Setup different LLM providers"""
        # Setup Gemini
        gemini_api_key = os.getenv("GOOGLE_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.providers[LLMProvider.GEMINI] = genai.GenerativeModel(
                "gemini-pro")
            self.active_provider = LLMProvider.GEMINI

        # Setup OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            openai.api_key = openai_api_key
            self.providers[LLMProvider.OPENAI] = openai
            if not self.active_provider:
                self.active_provider = LLMProvider.OPENAI

        # If no providers configured, we'll use fallback mechanisms
        if not self.active_provider:
            print("⚠️ Warning: No LLM providers configured. Using fallback responses.")

    def _register_default_tools(self):
        """Register default tools available to the system"""
        self.register_tool("currency_converter", {
            "description": "Convert currency amounts between different currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount to convert"},
                    "from_currency": {"type": "string", "description": "Source currency code (e.g., USD)"},
                    "to_currency": {"type": "string", "description": "Target currency code (e.g., EUR)"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        })

        self.register_tool("get_current_time", {
            "description": "Get the current time and date",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        })

        self.register_tool("calculate", {
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                },
                "required": ["expression"]
            }
        })

    def register_tool(self, name: str, schema: Dict[str, Any]):
        """Register a new tool with its schema"""
        import re  # Import here to avoid circular dependencies

        def wrapper(func: Callable):
            self.tool_registry[name] = {
                "function": func,
                "schema": schema
            }
            return func
        return wrapper

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their schemas"""
        return [{
            "type": "function",
            "function": {
                "name": name,
                "description": tool["schema"]["description"],
                "parameters": tool["schema"]["parameters"]
            }
        } for name, tool in self.tool_registry.items()]

    def _call_gemini(self, prompt: str, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Call Gemini with optional tools"""
        try:
            model = self.providers[LLMProvider.GEMINI]

            if tools:
                # For now, we'll simulate tool calling with prompt engineering
                # since the basic Gemini SDK doesn't support structured tool calling
                tool_names = [tool["function"]["name"] for tool in tools]
                enhanced_prompt = f"{prompt}\n\nAvailable tools: {', '.join(tool_names)}. " \
                    f"If you need to use any of these tools, respond with the tool name " \
                    f"and arguments in JSON format: {{\"tool\": \"tool_name\", \"arguments\": {{...}}}}"

                response = model.generate_content(enhanced_prompt)
                response_text = response.text

                # Try to detect if a tool should be called
                import json
                import re

                # Look for tool call pattern in response
                tool_match = re.search(
                    r'\{"tool":\s*"([^"]+)"(?:,\s*"arguments":\s*(\{[^}]+\}))?\}', response_text)
                if tool_match:
                    tool_name = tool_match.group(1)
                    arguments_str = tool_match.group(2)

                    if arguments_str:
                        arguments = json.loads(arguments_str)
                        tool_call = ToolCall(tool_name, arguments)
                        tool_result = tool_call.execute()

                        # Call the model again with tool result
                        followup_prompt = f"{prompt}\n\nTool '{tool_name}' was called with arguments {arguments} and returned: {tool_result}. " \
                            "Provide the final answer based on this information."
                        followup_response = model.generate_content(
                            followup_prompt)
                        return {
                            "content": followup_response.text,
                            "tool_calls": [{"name": tool_name, "arguments": arguments, "result": tool_result}],
                            "provider": LLMProvider.GEMINI.value
                        }

            else:
                response = model.generate_content(prompt)
                return {
                    "content": response.text,
                    "tool_calls": [],
                    "provider": LLMProvider.GEMINI.value
                }

        except Exception as e:
            print(f"Gemini call failed: {e}")
            return None

    def _call_openai(self, prompt: str, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Call OpenAI with optional tools"""
        try:
            if tools:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    functions=self.get_available_tools(),
                    function_call="auto"
                )

                message = response.choices[0].message

                if hasattr(message, 'function_call') and message.function_call:
                    # Execute the function
                    function_name = message.function_call.name
                    function_args = eval(message.function_call.arguments)

                    tool_call = ToolCall(function_name, function_args)
                    tool_result = tool_call.execute()

                    # Follow up with the result
                    followup_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": prompt},
                            {"role": "function", "name": function_name,
                                "content": str(tool_result)}
                        ]
                    )

                    return {
                        "content": followup_response.choices[0].message.content,
                        "tool_calls": [{"name": function_name, "arguments": function_args, "result": tool_result}],
                        "provider": LLMProvider.OPENAI.value
                    }
                else:
                    return {
                        "content": message.content,
                        "tool_calls": [],
                        "provider": LLMProvider.OPENAI.value
                    }
            else:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )

                return {
                    "content": response.choices[0].message.content,
                    "tool_calls": [],
                    "provider": LLMProvider.OPENAI.value
                }

        except Exception as e:
            print(f"OpenAI call failed: {e}")
            return None

    def generate_response(self, prompt: str, use_tools: bool = True) -> Dict[str, Any]:
        """
        Generate response using available providers with fallback
        """
        tools = self.get_available_tools() if use_tools else None

        # Try primary provider first
        if self.active_provider == LLMProvider.GEMINI and LLMProvider.GEMINI in self.providers:
            result = self._call_gemini(prompt, tools)
            if result:
                return result

        if self.active_provider == LLMProvider.OPENAI and LLMProvider.OPENAI in self.providers:
            result = self._call_openai(prompt, tools)
            if result:
                return result

        # Try other providers as fallback
        for provider in LLMProvider:
            if provider != self.active_provider and provider in self.providers:
                if provider == LLMProvider.GEMINI:
                    result = self._call_gemini(prompt, tools)
                elif provider == LLMProvider.OPENAI:
                    result = self._call_openai(prompt, tools)

                if result:
                    return result

        # Fallback response if no providers work
        return {
            "content": f"I'm sorry, but I couldn't process your request. The input was: {prompt[:100]}...",
            "tool_calls": [],
            "provider": "fallback"
        }

    def health_check(self) -> Dict[str, bool]:
        """Check health of all configured providers"""
        health_status = {}

        for provider_type, provider in self.providers.items():
            try:
                if provider_type == LLMProvider.GEMINI:
                    # Simple test call to Gemini
                    test_model = genai.GenerativeModel('gemini-pro')
                    test_response = test_model.generate_content(
                        "Say 'health check' in one word")
                    health_status[provider_type.value] = True
                elif provider_type == LLMProvider.OPENAI:
                    # Simple test call to OpenAI
                    test_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": "Say 'health check' in one word"}],
                        max_tokens=5
                    )
                    health_status[provider_type.value] = True
            except Exception as e:
                print(f"Health check failed for {provider_type.value}: {e}")
                health_status[provider_type.value] = False

        return health_status


# Global instance
llm_manager = LLMManager()


def generate_with_fallback(prompt: str, use_tools: bool = True) -> Dict[str, Any]:
    """
    Convenience function to generate response with fallback
    """
    return llm_manager.generate_response(prompt, use_tools)


if __name__ == "__main__":
    # Test the LLM manager
    test_prompt = "What is 100 USD in INR?"

    result = generate_with_fallback(test_prompt, use_tools=True)
    print(f"Response: {result['content']}")
    print(f"Provider: {result['provider']}")
    print(f"Tools used: {len(result['tool_calls'])}")

    # Test health check
    health = llm_manager.health_check()
    print(f"Provider health: {health}")
