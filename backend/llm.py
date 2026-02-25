"""
LLM module for generating answers using Azure OpenAI.
"""

import os
from typing import List, Dict
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMClient:
    """Wrapper for Azure OpenAI API."""
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
        self.api_version = os.getenv('AZURE_OPENAI_VERSION', '2024-02-01')
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT', '')
        
        self.client = None
        
        if self.has_token():
            try:
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.endpoint,
                    api_version=self.api_version,
                )
                print("✅ Azure OpenAI client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Azure OpenAI client: {str(e)}")
                self.client = None
        else:
            print("⚠️ Azure OpenAI credentials not found. Using extractive fallback.")
    
    def has_token(self) -> bool:
        """Check if Azure OpenAI credentials are available."""
        return bool(self.api_key and self.endpoint and self.deployment_name)
    
    def generate_answer(self, question: str, context_chunks: List[Dict], max_tokens: int = 800) -> str:
        """
        Generate answer using Azure OpenAI with context.
        
        Args:
            question: User question
            context_chunks: List of retrieved context chunks
            max_tokens: Maximum response length
        
        Returns:
            Generated answer text
        """
        if not context_chunks:
            return "No relevant context found. Please index some documents first."
        
        # Format context from chunks
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk.get('source', 'Unknown')
            text = chunk.get('text', '')
            context_parts.append(f"[Source {i}: {source}]\n{text}")
        
        context = "\n\n".join(context_parts)
        
        # Generate answer using Azure OpenAI
        if self.client:
            try:
                messages = [
                    {
                        "role": "system", 
                        "content": """You are a helpful research assistant. Use ONLY the provided context to answer questions accurately and comprehensively. 

Guidelines:
- Base your answer strictly on the provided context
- If the context doesn't contain enough information, clearly state this
- Cite sources when possible
- Provide detailed, well-structured answers
- If multiple sources contain relevant information, synthesize them coherently"""
                    },
                    {
                        "role": "user", 
                        "content": f"""Question: {question}

Context:
{context}

Please provide a comprehensive answer based on the context above."""
                    }
                ]
                
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3,  # Lower temperature for more focused answers
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                if response.choices and response.choices[0].message:
                    answer = response.choices[0].message.content
                    return answer.strip() if answer else "No answer generated."
                else:
                    return "No response from Azure OpenAI."
                    
            except Exception as e:
                error_msg = str(e)
                if "rate limit" in error_msg.lower():
                    return "⚠️ Rate limit exceeded. Please try again in a moment."
                elif "content filter" in error_msg.lower():
                    return "⚠️ Content filtered by Azure OpenAI. Please try rephrasing your question."
                elif "timeout" in error_msg.lower():
                    return "⚠️ Request timed out. Please try again."
                else:
                    return f"❌ Error generating answer: {error_msg}"
        else:
            # Fallback: extractive answer from context
            return self._extractive_fallback(question, context_chunks)
    
    def _extractive_fallback(self, question: str, context_chunks: List[Dict]) -> str:
        """
        Fallback extractive answer when Azure OpenAI is not available.
        Returns the most relevant chunk as answer.
        """
        if not context_chunks:
            return "No context available. Please configure Azure OpenAI credentials for LLM generation."
        
        # Return the top chunk as answer
        top_chunk = context_chunks[0]
        source = top_chunk.get('source', 'Unknown')
        text = top_chunk.get('text', '')
        score = top_chunk.get('score', 0)
        
        answer = f"**Extractive Answer** (Relevance: {score:.3f})\n\n"
        answer += f"**Source:** {source}\n\n"
        answer += f"**Content:** {text[:800]}"
        
        if len(text) > 800:
            answer += "...\n\n*Note: This is an extractive answer. Configure Azure OpenAI for generated responses.*"
        else:
            answer += "\n\n*Note: This is an extractive answer. Configure Azure OpenAI for generated responses.*"
        
        return answer
    
    def test_connection(self) -> Dict[str, str]:
        """
        Test Azure OpenAI connection.
        
        Returns:
            Dictionary with status and message
        """
        if not self.has_token():
            return {
                "status": "error",
                "message": "Missing Azure OpenAI credentials. Please check environment variables."
            }
        
        if not self.client:
            return {
                "status": "error", 
                "message": "Azure OpenAI client not initialized."
            }
        
        try:
            # Test with a simple query
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello, are you working?"}],
                max_tokens=10,
                temperature=0.1
            )
            
            if response.choices and response.choices[0].message:
                return {
                    "status": "success",
                    "message": "Azure OpenAI connection successful!"
                }
            else:
                return {
                    "status": "error",
                    "message": "No response from Azure OpenAI."
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}"
            }