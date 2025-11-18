# Contract Data Extraction and Documentation System

Automated system for extracting data from PDF contracts stored in SharePoint, processing them with Claude AI, and creating comprehensive documentation in Confluence.

## 🚀 Quick Links

- **New to the system?** Start with [QUICK_START.md](QUICK_START.md)
- **Setting up credentials?** See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
- **Customizing extraction?** Read [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)

## Features

- **SharePoint Integration**: Automatically reads all PDF contracts from a specified SharePoint folder
- **AI-Powered Extraction**: Uses Claude AI to extract structured data from contracts
- **Confluence Documentation**: Creates summary pages and a master index in Confluence
- **Robust Error Handling**: Retry logic, comprehensive logging, and graceful failure handling
- **Batch Processing**: Process multiple contracts efficiently

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  SharePoint │────▶│ PDF Processor│────▶│  Claude AI  │────▶│  Confluence  │
│   (Source)  │     │   (Extract)  │     │  (Analyze)  │     │ (Document)   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

## Prerequisites

- Python 3.8 or higher
- SharePoint site with contracts (PDF files)
- Azure AD app registration for SharePoint access
- Anthropic API key (Claude AI)
- Confluence account with API access

## Installation

1. **Clone the repository** (if applicable) or navigate to the project directory:

```bash
cd /workspace
```

2. **Install dependencies**:

```bash
pip install -r requirements.txt
```

## Configuration

1. **Create configuration file**:

```bash
cp config.yaml.example config.yaml
```

2. **Edit `config.yaml`** with your credentials:

```yaml
# SharePoint Configuration
sharepoint:
  site_url: "https://yourcompany.sharepoint.com/sites/YourSite"
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  tenant_id: "your-tenant-id"
  contracts_folder: "Shared Documents/Contracts"

# Claude AI Configuration
claude:
  api_key: "your-anthropic-api-key"
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 4096

# Confluence Configuration
confluence:
  url: "https://yourcompany.atlassian.net"
  username: "your-email@company.com"
  api_token: "your-confluence-api-token"
  space_key: "CONTRACTS"
  parent_page_title: "Contract Summaries"
```

### Setting Up SharePoint Access

1. Register an app in Azure AD:
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Create a new registration
   - Note the Client ID and Tenant ID
   - Create a client secret and note it down

2. Grant SharePoint permissions:
   - In the app registration, go to API permissions
   - Add SharePoint permissions (Sites.Read.All)
   - Grant admin consent

3. Grant site access:
   - Go to your SharePoint site
   - Site Settings → Site Permissions
   - Grant the app access to the site

### Setting Up Confluence Access

1. Generate an API token:
   - Go to https://id.atlassian.com/manage-profile/security/api-tokens
   - Create a new API token
   - Copy the token (you won't see it again)

2. Create a space in Confluence (if needed):
   - Note the space key (e.g., "CONTRACTS")

### Setting Up Claude AI

1. Get an API key:
   - Sign up at https://www.anthropic.com
   - Go to your account settings
   - Generate an API key

## Customizing Extraction Instructions

The extraction logic is defined in `prompts.py`. You can customize:

1. **Extraction Prompt**: Defines what data to extract from contracts
2. **Summary Prompt**: Defines how to format the summary pages
3. **Validation Prompt**: Optional validation of extracted data

**To customize with your Claude AI instructions:**

Edit the prompts in `prompts.py`:

```python
EXTRACTION_PROMPT = """
Your custom extraction instructions here...

Contract Text:
{contract_text}
"""

SUMMARY_PAGE_PROMPT = """
Your custom summary generation instructions here...

Extracted Information:
{extracted_data}
"""
```

## Usage

### Basic Usage

Process all contracts with default settings:

```bash
python main.py --config config.yaml
```

### Advanced Options

```bash
# Specify custom configuration file
python main.py --config /path/to/custom/config.yaml

# Set logging level
python main.py --log-level DEBUG

# Specify output file for results
python main.py --output results.json
```

### Command-Line Options

- `--config PATH`: Path to configuration file (default: config.yaml)
- `--log-level LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--output PATH`: Output file for processing results (default: processing_results.json)

## Output

### Logs

- Console output with color-coded log levels
- Detailed log files in the `logs/` directory
- Each run creates a timestamped log file

### Results File

A JSON file (default: `processing_results.json`) containing:
- Processing status for each contract
- Extracted data
- Confluence page URLs
- Error messages (if any)

### Confluence Pages

1. **Master Summary Page**: Table with all contracts and key information
2. **Individual Summary Pages**: Detailed summary for each contract
   - Created as child pages under the master page
   - Tagged with "contract" label

## Project Structure

```
/workspace/
├── main.py                      # Main entry point
├── contract_processor.py        # Orchestration logic
├── sharepoint_client.py         # SharePoint integration
├── claude_client.py             # Claude AI integration
├── confluence_client.py         # Confluence integration
├── pdf_processor.py             # PDF text extraction
├── prompts.py                   # AI prompts (CUSTOMIZE THIS)
├── logger_config.py             # Logging configuration
├── config.yaml.example          # Example configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Troubleshooting

### SharePoint Connection Issues

- Verify your Azure AD app has the correct permissions
- Check that the client ID, secret, and tenant ID are correct
- Ensure the contracts folder path is correct (case-sensitive)

### PDF Extraction Issues

- Some PDFs may be scanned images without text layer
- Consider adding OCR capabilities for image-based PDFs
- Check PDF is not password-protected

### Claude AI Issues

- Verify API key is valid
- Check rate limits on your Anthropic account
- Large contracts may need to be truncated (handled automatically)

### Confluence Issues

- Verify API token is valid and not expired
- Check that the space key exists
- Ensure you have write permissions in the space

## Security Notes

- **Never commit `config.yaml`** with real credentials to version control
- Use environment variables for sensitive data in production
- Rotate API keys and tokens regularly
- Limit SharePoint app permissions to minimum required

## Environment Variables (Alternative to config.yaml)

You can use environment variables instead of config.yaml:

```bash
export SHAREPOINT_SITE_URL="https://..."
export SHAREPOINT_CLIENT_ID="..."
export SHAREPOINT_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."
export CLAUDE_API_KEY="..."
export CONFLUENCE_URL="..."
export CONFLUENCE_USERNAME="..."
export CONFLUENCE_API_TOKEN="..."
```

## Next Steps

1. **Customize the prompts** in `prompts.py` with your specific extraction instructions from Claude AI
2. **Test with a small subset** of contracts first
3. **Review the output** in Confluence and adjust prompts as needed
4. **Run on full contract set** once satisfied with results

## Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Review the `processing_results.json` file
3. Enable DEBUG logging for more detailed information

## License

[Your License Here]

## Changelog

### Version 1.0.0
- Initial release
- SharePoint integration
- Claude AI extraction
- Confluence documentation
- Batch processing with error handling
