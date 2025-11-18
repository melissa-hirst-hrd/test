# Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] SharePoint site with PDF contracts
- [ ] Azure AD app credentials (client ID, secret, tenant ID)
- [ ] Anthropic API key
- [ ] Confluence account with API token

## Quick Setup

### 1. Install Dependencies (2 min)

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials (2 min)

```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your credentials
```

**Required fields:**
- SharePoint: site_url, client_id, client_secret, tenant_id, contracts_folder
- Claude: api_key
- Confluence: url, username, api_token, space_key

### 3. Customize Extraction Instructions (1 min)

Edit `prompts.py` and add your Claude AI instructions:

```python
EXTRACTION_PROMPT = """
[YOUR CLAUDE AI INSTRUCTIONS HERE]

Contract Text:
{contract_text}
"""
```

### 4. Test Connections (30 sec)

```bash
python test_connections.py
```

This verifies:
- ✓ SharePoint access
- ✓ Claude AI connection
- ✓ Confluence permissions

### 5. Run Processing (varies by contract count)

```bash
python main.py --config config.yaml
```

## What Happens Next?

The system will:

1. **Download** all PDF contracts from SharePoint
2. **Extract** text from each PDF
3. **Analyze** contracts using Claude AI with your instructions
4. **Create** individual summary pages in Confluence
5. **Generate** a master summary table

## Output Locations

- **Confluence**: Check your space for "Contract Summaries" parent page
- **Logs**: `logs/contract_processor_[timestamp].log`
- **Results**: `processing_results.json`

## Viewing Results

Go to your Confluence space:
```
https://yourcompany.atlassian.net/wiki/spaces/[SPACE_KEY]
```

Look for the "Contract Summaries" page with:
- Master table of all contracts
- Individual child pages for each contract

## Troubleshooting

If something fails:

```bash
# Re-run with debug logging
python main.py --log-level DEBUG

# Check the detailed logs
cat logs/contract_processor_*.log | tail -100

# Review results file
cat processing_results.json
```

Common issues:
- **SharePoint access denied**: Check Azure AD permissions
- **Claude authentication failed**: Verify API key
- **Confluence unauthorized**: Check API token and space permissions

## Next Steps

1. Review the Confluence pages
2. Refine your prompts in `prompts.py` if needed
3. Re-run for updated results

## Need More Help?

- Detailed setup: See `SETUP_INSTRUCTIONS.md`
- Customization: See `CUSTOMIZATION_GUIDE.md`
- Full documentation: See `README.md`

---

**Important**: Before your first run, share your Claude AI instructions with me so I can integrate them into `prompts.py`!
