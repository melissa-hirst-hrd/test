#!/usr/bin/env python3
"""
Test script to verify all connections are working correctly.

Run this before processing contracts to ensure everything is set up properly.
"""
import yaml
import sys
from sharepoint_client import SharePointClient
from claude_client import ClaudeClient
from confluence_client import ConfluenceClient
from logger_config import setup_logging


def test_sharepoint(config):
    """Test SharePoint connection and file access."""
    print("\n" + "=" * 60)
    print("Testing SharePoint Connection")
    print("=" * 60)
    
    try:
        sp_config = config['sharepoint']
        sp = SharePointClient(
            site_url=sp_config['site_url'],
            client_id=sp_config['client_id'],
            client_secret=sp_config['client_secret'],
            tenant_id=sp_config['tenant_id'],
            contracts_folder=sp_config['contracts_folder']
        )
        
        files = sp.list_pdf_files()
        print(f"✓ Successfully connected to SharePoint")
        print(f"✓ Found {len(files)} PDF files in folder: {sp_config['contracts_folder']}")
        
        if files:
            print("\nSample files:")
            for i, file in enumerate(files[:3], 1):
                print(f"  {i}. {file['name']} ({file['size']} bytes)")
        
        return True
        
    except Exception as e:
        print(f"✗ SharePoint connection failed: {e}")
        return False


def test_claude(config):
    """Test Claude AI connection."""
    print("\n" + "=" * 60)
    print("Testing Claude AI Connection")
    print("=" * 60)
    
    try:
        claude_config = config['claude']
        claude = ClaudeClient(
            api_key=claude_config['api_key'],
            model=claude_config.get('model', 'claude-3-5-sonnet-20241022')
        )
        
        # Simple test query
        test_response = claude.analyze_contract(
            "This is a test contract between Company A and Company B for testing purposes.",
            "Please extract the party names from this contract: {contract_text}"
        )
        
        print(f"✓ Successfully connected to Claude AI")
        print(f"✓ Model: {claude_config.get('model', 'claude-3-5-sonnet-20241022')}")
        print(f"✓ Test response received ({len(test_response)} characters)")
        
        return True
        
    except Exception as e:
        print(f"✗ Claude AI connection failed: {e}")
        return False


def test_confluence(config):
    """Test Confluence connection and access."""
    print("\n" + "=" * 60)
    print("Testing Confluence Connection")
    print("=" * 60)
    
    try:
        conf_config = config['confluence']
        conf = ConfluenceClient(
            url=conf_config['url'],
            username=conf_config['username'],
            api_token=conf_config['api_token'],
            space_key=conf_config['space_key']
        )
        
        # Test by getting or creating parent page
        parent_title = conf_config.get('parent_page_title', 'Contract Summaries')
        parent_id = conf.get_or_create_parent_page(parent_title)
        
        print(f"✓ Successfully connected to Confluence")
        print(f"✓ Space: {conf_config['space_key']}")
        print(f"✓ Parent page: {parent_title} (ID: {parent_id})")
        print(f"✓ URL: {conf_config['url']}/wiki/spaces/{conf_config['space_key']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Confluence connection failed: {e}")
        return False


def main():
    """Main test execution."""
    print("=" * 60)
    print("Contract Data Extraction - Connection Test")
    print("=" * 60)
    
    # Setup basic logging
    setup_logging('INFO')
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Configuration file loaded successfully")
    except FileNotFoundError:
        print("✗ config.yaml not found. Please create it from config.yaml.example")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    results.append(("SharePoint", test_sharepoint(config)))
    results.append(("Claude AI", test_claude(config)))
    results.append(("Confluence", test_confluence(config)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✓ All tests passed! You're ready to process contracts.")
        print("\nRun the following command to start processing:")
        print("  python main.py --config config.yaml")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed. Please check your configuration and credentials.")
        print("\nSee SETUP_INSTRUCTIONS.md for detailed setup help.")
        sys.exit(1)


if __name__ == '__main__':
    main()
