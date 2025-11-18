# Setup Instructions

Step-by-step guide to get the Contract Data Extraction system up and running.

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure SharePoint Access

### 2.1 Register Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Enter a name (e.g., "Contract Processor")
5. Select **Single tenant**
6. Click **Register**

### 2.2 Note Down Credentials

- **Application (client) ID**: Copy this value
- **Directory (tenant) ID**: Copy this value

### 2.3 Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description and select expiration
4. Click **Add**
5. **Copy the secret value immediately** (you won't see it again)

### 2.4 Grant API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **SharePoint**
4. Select **Application permissions**
5. Add **Sites.Read.All**
6. Click **Grant admin consent** (requires admin rights)

### 2.5 Grant Site Access

1. Go to your SharePoint site
2. Navigate to **Site Settings** → **Site Permissions**
3. Click **Grant Permissions**
4. Enter your app ID: `<client-id>@<tenant-id>`
5. Grant **Read** permissions

## Step 3: Configure Claude AI

### 3.1 Get API Key

1. Go to [Anthropic Console](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the API key

## Step 4: Configure Confluence

### 4.1 Create API Token

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Enter a label (e.g., "Contract Processor")
4. Click **Create**
5. Copy the token

### 4.2 Prepare Confluence Space

1. Log in to your Confluence instance
2. Create a space for contracts (if it doesn't exist)
3. Note the **Space Key** (visible in the URL or space settings)

## Step 5: Create Configuration File

### Option A: Using config.yaml

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` with your credentials:

```yaml
sharepoint:
  site_url: "https://yourcompany.sharepoint.com/sites/YourSite"
  client_id: "<your-client-id>"
  client_secret: "<your-client-secret>"
  tenant_id: "<your-tenant-id>"
  contracts_folder: "Shared Documents/Contracts"

claude:
  api_key: "<your-anthropic-api-key>"
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 4096

confluence:
  url: "https://yourcompany.atlassian.net"
  username: "<your-email@company.com>"
  api_token: "<your-confluence-api-token>"
  space_key: "<YOUR-SPACE-KEY>"
  parent_page_title: "Contract Summaries"
```

### Option B: Using Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials and then use a tool like `python-dotenv` to load them.

## Step 6: Customize Extraction Instructions

Edit `prompts.py` to include your specific Claude AI instructions for contract extraction.

### Example Customization:

```python
EXTRACTION_PROMPT = """
You are analyzing a contract document. Please extract the following information:

1. Contract parties (all organizations and individuals)
2. Contract date and term
3. Financial details (amounts, payment schedules)
4. Deliverables and obligations
5. Termination clauses
6. Special conditions

Contract text:
{contract_text}

Return the data in JSON format with clear field names.
"""
```

**Replace the placeholder prompts with your actual Claude AI instructions.**

## Step 7: Test Connection

Create a test script `test_connections.py`:

```python
import yaml
from sharepoint_client import SharePointClient
from claude_client import ClaudeClient
from confluence_client import ConfluenceClient

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Test SharePoint
print("Testing SharePoint connection...")
sp = SharePointClient(**config['sharepoint'])
files = sp.list_pdf_files()
print(f"✓ Found {len(files)} PDF files in SharePoint")

# Test Claude
print("\nTesting Claude AI connection...")
claude = ClaudeClient(config['claude']['api_key'])
test_response = claude.analyze_contract(
    "This is a test contract.",
    "Please analyze this: {contract_text}"
)
print(f"✓ Claude AI responded")

# Test Confluence
print("\nTesting Confluence connection...")
conf = ConfluenceClient(**config['confluence'])
parent_id = conf.get_or_create_parent_page("Test Page")
print(f"✓ Confluence access confirmed")

print("\n✓ All connections successful!")
```

Run the test:

```bash
python test_connections.py
```

## Step 8: Run Initial Test

Process contracts with verbose logging:

```bash
python main.py --log-level DEBUG
```

## Step 9: Review Results

1. Check the console output for progress
2. Review log files in `logs/` directory
3. Check `processing_results.json` for detailed results
4. View the Confluence pages to see the generated documentation

## Troubleshooting

### SharePoint "Access Denied"

- Verify API permissions are granted with admin consent
- Check that the app has site-level permissions
- Ensure the folder path is correct and accessible

### Claude "Authentication Error"

- Verify API key is correct
- Check your Anthropic account has API access
- Ensure you have sufficient credits

### Confluence "Unauthorized"

- Verify API token is still valid
- Check username/email is correct
- Ensure you have write permissions in the space

### PDF Extraction Returns Empty Text

- PDF may be scanned images without text layer
- Try using OCR software to add text layer first
- Check if PDF is password-protected

## Next Steps

1. Start with a small test set of contracts
2. Review and refine your extraction prompts
3. Adjust summary formatting as needed
4. Scale up to full contract library

## Security Reminders

- Never commit `config.yaml` or `.env` with real credentials
- Use `.gitignore` to exclude sensitive files
- Rotate API keys and tokens regularly
- Use least-privilege access for all services

## Support

If you encounter issues:
1. Enable DEBUG logging: `--log-level DEBUG`
2. Check the detailed log files in `logs/`
3. Review `processing_results.json` for error details
4. Verify all prerequisites are met
