"""
Contract extraction prompts for Claude AI.

This file contains the instructions for Claude to extract specific information
from contracts and create summary pages.

TODO: Replace these placeholder instructions with your actual Claude AI instructions.
"""

# Main extraction prompt - used to extract structured data from contracts
EXTRACTION_PROMPT = """
You are a contract analyst. Please analyze the following contract and extract the key information.

Extract the following details:
1. Contract Title/Name
2. Parties Involved (all parties)
3. Effective Date
4. Expiration Date
5. Contract Value/Amount
6. Key Terms and Conditions
7. Payment Terms
8. Termination Clauses
9. Renewal Terms
10. Special Provisions or Notes

Contract Text:
{contract_text}

Please provide the extracted information in a structured JSON format with clear labels for each field.
If any information is not found in the contract, mark it as "Not found" or "N/A".
"""

# Summary page prompt - used to create a summary document
SUMMARY_PAGE_PROMPT = """
Based on the following extracted contract information, create a clear and concise summary page
that can be published in Confluence.

Extracted Information:
{extracted_data}

Please format the summary as a Confluence-compatible document with:
- A clear title
- Executive summary section
- Key details in a structured format (tables if appropriate)
- Important dates and milestones
- Risk factors or items requiring attention
- Recommendations or action items

Use Confluence wiki markup or HTML format for the output.
"""

# Validation prompt - optional, to verify extracted data
VALIDATION_PROMPT = """
Please review the following extracted contract data and verify its accuracy and completeness.

Original Contract Text (first 2000 characters):
{contract_text_sample}

Extracted Data:
{extracted_data}

Identify any:
- Missing critical information
- Potentially incorrect extractions
- Ambiguities that need clarification

Provide your feedback in a structured format.
"""

def get_extraction_prompt(contract_text: str) -> str:
    """Get the extraction prompt with the contract text inserted."""
    return EXTRACTION_PROMPT.format(contract_text=contract_text)

def get_summary_prompt(extracted_data: str) -> str:
    """Get the summary page prompt with extracted data inserted."""
    return SUMMARY_PAGE_PROMPT.format(extracted_data=extracted_data)

def get_validation_prompt(contract_text: str, extracted_data: str) -> str:
    """Get the validation prompt with contract text sample and extracted data."""
    contract_text_sample = contract_text[:2000] + "..." if len(contract_text) > 2000 else contract_text
    return VALIDATION_PROMPT.format(
        contract_text_sample=contract_text_sample,
        extracted_data=extracted_data
    )
