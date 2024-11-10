from typing import Dict, Optional, List
import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import openai
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Structured response from AI service"""
    scenario_title: str
    description: str
    stakeholders_affected: List[str]
    approaches: List[Dict]
    hidden_factors: List[str]
    category: str
    raw_response: Dict  # Store full response for debugging

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_completion(self, prompt: str) -> str:
        """Generate completion from AI provider"""
        pass

class OpenAIProvider(AIProvider):
    """OpenAI integration"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate_completion(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in business ethics and scenario design."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class AnthropicProvider(AIProvider):
    """Anthropic Claude integration"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def generate_completion(self, prompt: str) -> str:
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

class AIService:
    """Main AI service for scenario generation"""

    def __init__(
        self,
        primary_provider: AIProvider,
        backup_provider: Optional[AIProvider] = None,
        cache_service: Optional["CacheService"] = None
    ):
        self.primary_provider = primary_provider
        self.backup_provider = backup_provider
        self.cache_service = cache_service

    async def generate_scenario(self, prompt: str) -> AIResponse:
        """Generate a scenario using AI"""
        
        # Check cache first if available
        if self.cache_service:
            cached_response = await self.cache_service.get_scenario(prompt)
            if cached_response:
                return cached_response

        try:
            # Try primary provider
            response_text = await self.primary_provider.generate_completion(prompt)
            response = self._parse_response(response_text)
            
        except Exception as e:
            logger.error(f"Primary AI provider failed: {str(e)}")
            
            if self.backup_provider:
                try:
                    # Fallback to backup provider
                    response_text = await self.backup_provider.generate_completion(prompt)
                    response = self._parse_response(response_text)
                except Exception as backup_error:
                    logger.error(f"Backup AI provider failed: {str(backup_error)}")
                    raise RuntimeError("All AI providers failed")
            else:
                raise

        # Cache successful response if caching is available
        if self.cache_service:
            await self.cache_service.store_scenario(prompt, response)

        return response

    def _parse_response(self, response_text: str) -> AIResponse:
        """Parse AI response into structured format"""
        try:
            # Assuming response is in JSON format
            import json
            response_dict = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                'scenario_title',
                'description',
                'stakeholders_affected',
                'approaches'
            ]
            
            for field in required_fields:
                if field not in response_dict:
                    raise ValueError(f"Missing required field: {field}")

            return AIResponse(
                scenario_title=response_dict['scenario_title'],
                description=response_dict['description'],
                stakeholders_affected=response_dict['stakeholders_affected'],
                approaches=response_dict['approaches'],
                hidden_factors=response_dict.get('hidden_factors', []),
                category=response_dict.get('category', 'general'),
                raw_response=response_dict
            )

        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            raise ValueError("Invalid AI response format")
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            raise

    def _enhance_prompt(self, base_prompt: str) -> str:
        """Enhance prompt with additional context and formatting"""
        return f"""
        You are an expert in business ethics and scenario design.
        Generate a realistic and challenging business ethics scenario in JSON format.
        
        Requirements:
        {base_prompt}
        
        Response must be valid JSON with the following structure:
        {{
            "scenario_title": "string",
            "description": "string",
            "category": "string",
            "stakeholders_affected": ["string"],
            "approaches": [
                {{
                    "title": "string",
                    "description": "string",
                    "impacts": {{
                        "financial": int,
                        "reputation": int,
                        "stakeholder_name": int
                    }}
                }}
            ],
            "hidden_factors": ["string"]
        }}
        """

# Example usage:
async def main():
    # Initialize providers
    openai_provider = OpenAIProvider(api_key="your_openai_key")
    anthropic_provider = AnthropicProvider(api_key="your_anthropic_key")
    
    # Initialize service with both providers
    ai_service = AIService(
        primary_provider=anthropic_provider,  # Claude as primary
        backup_provider=openai_provider      # GPT-4 as backup
    )
    
    # Generate scenario
    sample_prompt = """
    Generate a scenario involving environmental sustainability and employee welfare.
    The company is medium-sized in the manufacturing sector.
    Recent decisions show a bias toward short-term financial gains.
    """
    
    try:
        response = await ai_service.generate_scenario(sample_prompt)
        print(f"Generated scenario: {response.scenario_title}")
    except Exception as e:
        print(f"Failed to generate scenario: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())