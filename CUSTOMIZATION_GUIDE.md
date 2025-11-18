# Customization Guide

This guide explains how to customize the contract extraction system with your specific Claude AI instructions.

## Overview

The system uses three main prompts to process contracts:

1. **Extraction Prompt** - Tells Claude what data to extract from contracts
2. **Summary Prompt** - Tells Claude how to format summary pages
3. **Validation Prompt** - (Optional) Validates extracted data

These prompts are defined in `prompts.py`.

## Step 1: Prepare Your Claude AI Instructions

You mentioned you have instructions in Claude AI. You'll need to:

1. Copy your extraction instructions from Claude
2. Copy your summary page generation instructions
3. Identify any specific data fields you want to extract

## Step 2: Update the Extraction Prompt

Edit `prompts.py` and replace the `EXTRACTION_PROMPT`:

```python
EXTRACTION_PROMPT = """
[PASTE YOUR CLAUDE AI EXTRACTION INSTRUCTIONS HERE]

Make sure to include the placeholder {contract_text} where the contract content should be inserted.

Contract Text:
{contract_text}

[Your instructions for output format]
"""
```

### Example Extraction Prompt

```python
EXTRACTION_PROMPT = """
You are a legal contract analyst. Analyze the following contract and extract structured information.

Extract these details:
- Contract ID/Number
- Contract Title
- All parties (legal names and roles)
- Effective Date
- Expiration/End Date
- Auto-renewal terms
- Contract Value (total and breakdown if applicable)
- Payment terms and schedule
- Deliverables or scope of work
- Key obligations of each party
- Termination conditions
- Notice requirements
- Governing law and jurisdiction
- Confidentiality clauses
- Liability limitations
- Force majeure provisions
- Amendment procedures
- Special terms or conditions

Contract Text:
{contract_text}

Output the extracted information in JSON format with clear field names.
If any information is not found, use "Not specified" as the value.
For dates, use ISO format (YYYY-MM-DD) when possible.
For monetary amounts, include currency code.

Example output structure:
{{
  "contract_id": "...",
  "title": "...",
  "parties": [
    {{"name": "...", "role": "..."}},
    {{"name": "...", "role": "..."}}
  ],
  "dates": {{
    "effective": "YYYY-MM-DD",
    "expiration": "YYYY-MM-DD"
  }},
  ...
}}
"""
```

## Step 3: Update the Summary Prompt

Edit the `SUMMARY_PAGE_PROMPT` in `prompts.py`:

```python
SUMMARY_PAGE_PROMPT = """
[PASTE YOUR CLAUDE AI SUMMARY PAGE INSTRUCTIONS HERE]

The placeholder {extracted_data} will contain the data extracted from the contract.

Extracted Information:
{extracted_data}

[Your instructions for formatting the summary]
"""
```

### Example Summary Prompt

```python
SUMMARY_PAGE_PROMPT = """
Create a comprehensive contract summary page for Confluence based on the extracted data below.

Extracted Information:
{extracted_data}

Format the summary using HTML for Confluence with the following sections:

1. **Header Section**
   - Contract title as H1
   - Status badge (Active/Expired/Pending)
   - Quick facts box with key dates and values

2. **Executive Summary**
   - 2-3 paragraph overview
   - Key business purpose
   - Financial impact

3. **Parties Involved**
   - Table with party names, roles, and contact info if available

4. **Key Terms**
   - Table format
   - Dates (effective, expiration, renewal)
   - Financial terms
   - Payment schedule

5. **Obligations & Deliverables**
   - Organized by party
   - Bullet points for clarity

6. **Risk & Compliance**
   - Termination conditions
   - Liability limitations
   - Notable clauses requiring attention

7. **Action Items**
   - Upcoming deadlines
   - Renewal decisions
   - Required notifications

Use this HTML structure:
<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>[Important information]</p>
  </ac:rich-text-body>
</ac:structured-macro>

For tables:
<table>
  <thead><tr><th>Column</th></tr></thead>
  <tbody><tr><td>Data</td></tr></tbody>
</table>

Make the summary clear, scannable, and actionable.
"""
```

## Step 4: Customize Data Fields

If your Claude instructions extract specific fields, update the Confluence table generation in `confluence_client.py`:

```python
# In create_master_summary_table method, around line 100

# Replace these lines:
name = extracted.get('contract_name', 'N/A')
parties = extracted.get('parties', 'N/A')
effective_date = extracted.get('effective_date', 'N/A')
# ... etc

# With your actual field names:
name = extracted.get('title', 'N/A')  # If your extraction uses 'title'
parties = extracted.get('party_names', 'N/A')  # If you use 'party_names'
effective_date = extracted.get('dates', {}).get('effective', 'N/A')
# ... etc
```

## Step 5: Add Custom Processing Logic

If you need custom processing (e.g., date parsing, currency conversion), create a helper file:

```python
# custom_processors.py

from datetime import datetime
import re

def parse_contract_date(date_str: str) -> str:
    """Convert various date formats to ISO format."""
    # Add your logic here
    pass

def extract_currency_amount(amount_str: str) -> dict:
    """Extract currency and amount from text."""
    # Add your logic here
    return {'currency': 'USD', 'amount': 0.0}

def categorize_contract_type(title: str, content: str) -> str:
    """Determine contract category."""
    # Add your logic here
    return 'Service Agreement'
```

Then import and use in `contract_processor.py`:

```python
from custom_processors import parse_contract_date, categorize_contract_type

# In process_single_contract method:
extracted_data = self.claude_client.extract_contract_data(...)

# Add custom processing
if 'effective_date' in extracted_data:
    extracted_data['effective_date'] = parse_contract_date(
        extracted_data['effective_date']
    )

extracted_data['category'] = categorize_contract_type(
    extracted_data.get('title', ''),
    contract_text
)
```

## Step 6: Test Your Customizations

1. **Test with one contract**:

```python
# test_single_contract.py
from contract_processor import ContractProcessor
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

processor = ContractProcessor(config)

# Get just one contract
contracts = processor.sharepoint_client.download_all_contracts()
if contracts:
    result = processor.process_single_contract(contracts[0])
    print(json.dumps(result, indent=2))
```

2. **Review the output**:
   - Check `extracted_data` structure
   - Verify all required fields are present
   - Check Confluence page formatting

3. **Iterate**:
   - Adjust prompts based on output quality
   - Add field mappings if needed
   - Refine summary formatting

## Common Customization Scenarios

### Scenario 1: Multi-language Contracts

```python
EXTRACTION_PROMPT = """
This contract may be in English, Spanish, or French.
First identify the language, then extract the information.

Contract Text:
{contract_text}

Provide the extracted data in English, but note the original language.
"""
```

### Scenario 2: Industry-specific Terms

```python
EXTRACTION_PROMPT = """
You are analyzing a [YOUR INDUSTRY] contract. Pay special attention to:
- [Industry-specific term 1]
- [Industry-specific term 2]
- [Regulatory compliance requirements]

Contract Text:
{contract_text}

Extract according to [YOUR INDUSTRY] standards...
"""
```

### Scenario 3: Custom Risk Assessment

```python
# Add to prompts.py
RISK_ASSESSMENT_PROMPT = """
Analyze the following contract data and assess risks.

Contract Data:
{extracted_data}

Identify:
1. Financial risks
2. Compliance risks
3. Operational risks
4. Reputational risks

Rate each risk as: Low, Medium, High, Critical
Provide brief explanation for each identified risk.
"""
```

Then update `contract_processor.py`:

```python
# Add risk assessment step
risk_assessment = self.claude_client.analyze_contract(
    json.dumps(extracted_data),
    get_risk_assessment_prompt(extracted_data)
)
result['risk_assessment'] = risk_assessment
```

## Tips for Effective Prompts

1. **Be Specific**: Clearly define what data you want and in what format
2. **Provide Examples**: Show Claude the desired output structure
3. **Handle Missing Data**: Tell Claude what to do when information isn't found
4. **Use Structured Output**: JSON or HTML tables work better than free text
5. **Iterate**: Start simple, then add complexity based on results

## Need Help?

If you have your Claude AI instructions ready, you can:

1. Share them with me to integrate into `prompts.py`
2. Use the examples above as templates
3. Test incrementally with small changes

## Next Steps

1. Copy your Claude AI instructions
2. Update `prompts.py` with your instructions
3. Run `python test_connections.py` to verify setup
4. Test with a single contract
5. Review and refine
6. Process full contract library
