"""
Claude AI client for contract analysis and data extraction.
"""
import logging
import json
from typing import Dict, Optional
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with Claude AI for contract analysis."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", 
                 max_tokens: int = 4096):
        """
        Initialize Claude AI client.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens for response
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        
        logger.info(f"Claude client initialized with model: {model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def analyze_contract(self, contract_text: str, prompt: str) -> str:
        """
        Analyze a contract using Claude AI.
        
        Args:
            contract_text: Full text of the contract
            prompt: Analysis prompt/instructions
            
        Returns:
            Claude's analysis response
        """
        try:
            # Truncate contract text if it's too long
            max_contract_length = 100000  # Approximate character limit
            if len(contract_text) > max_contract_length:
                logger.warning(f"Contract text truncated from {len(contract_text)} to {max_contract_length} chars")
                contract_text = contract_text[:max_contract_length] + "\n\n[Content truncated due to length...]"
            
            # Format the prompt with contract text
            full_prompt = prompt.format(contract_text=contract_text)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            logger.info(f"Successfully analyzed contract (input: {len(contract_text)} chars, output: {len(response_text)} chars)")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error analyzing contract with Claude: {e}")
            raise
    
    def extract_contract_data(self, contract_text: str, extraction_prompt: str) -> Dict:
        """
        Extract structured data from a contract.
        
        Args:
            contract_text: Full text of the contract
            extraction_prompt: Prompt for data extraction
            
        Returns:
            Dictionary with extracted data
        """
        try:
            response = self.analyze_contract(contract_text, extraction_prompt)
            
            # Try to parse as JSON if possible
            try:
                # Look for JSON in the response
                if '```json' in response:
                    # Extract JSON from code block
                    json_start = response.find('```json') + 7
                    json_end = response.find('```', json_start)
                    json_str = response[json_start:json_end].strip()
                    extracted_data = json.loads(json_str)
                elif '{' in response and '}' in response:
                    # Try to find JSON object in response
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    json_str = response[json_start:json_end]
                    extracted_data = json.loads(json_str)
                else:
                    # Return as text if no JSON found
                    extracted_data = {'raw_response': response}
                
                logger.info("Successfully extracted structured data from contract")
                return extracted_data
                
            except json.JSONDecodeError:
                logger.warning("Could not parse response as JSON, returning raw text")
                return {'raw_response': response}
                
        except Exception as e:
            logger.error(f"Error extracting contract data: {e}")
            raise
    
    def generate_summary(self, extracted_data: Dict, summary_prompt: str) -> str:
        """
        Generate a summary document from extracted contract data.
        
        Args:
            extracted_data: Dictionary with extracted contract data
            summary_prompt: Prompt for summary generation
            
        Returns:
            Generated summary text (formatted for Confluence)
        """
        try:
            # Convert extracted data to string for prompt
            data_str = json.dumps(extracted_data, indent=2)
            
            # Format prompt with extracted data
            full_prompt = summary_prompt.format(extracted_data=data_str)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            summary = message.content[0].text
            logger.info(f"Successfully generated summary ({len(summary)} chars)")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def validate_extraction(self, contract_text: str, extracted_data: Dict, 
                          validation_prompt: str) -> Dict:
        """
        Validate extracted contract data.
        
        Args:
            contract_text: Original contract text
            extracted_data: Extracted data to validate
            validation_prompt: Prompt for validation
            
        Returns:
            Dictionary with validation results
        """
        try:
            data_str = json.dumps(extracted_data, indent=2)
            
            # Format validation prompt
            contract_sample = contract_text[:2000] + "..." if len(contract_text) > 2000 else contract_text
            full_prompt = validation_prompt.format(
                contract_text_sample=contract_sample,
                extracted_data=data_str
            )
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            validation_result = message.content[0].text
            logger.info("Completed validation of extracted data")
            
            return {'validation_response': validation_result}
            
        except Exception as e:
            logger.error(f"Error validating extraction: {e}")
            raise
