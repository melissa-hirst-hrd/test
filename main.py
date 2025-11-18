#!/usr/bin/env python3
"""
Main entry point for the Contract Data Extraction and Documentation system.

This script orchestrates the entire workflow:
1. Reads PDF contracts from SharePoint
2. Extracts structured data using Claude AI
3. Creates documentation in Confluence

Usage:
    python main.py --config config.yaml
"""
import argparse
import logging
import sys
import yaml
from pathlib import Path
from datetime import datetime

from contract_processor import ContractProcessor
from logger_config import setup_logging


def load_config(config_path: str) -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        sys.exit(1)


def validate_config(config: dict) -> bool:
    """
    Validate that all required configuration keys are present.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = {
        'sharepoint': ['site_url', 'client_id', 'client_secret', 'tenant_id', 'contracts_folder'],
        'claude': ['api_key'],
        'confluence': ['url', 'username', 'api_token', 'space_key']
    }
    
    for section, keys in required_keys.items():
        if section not in config:
            logging.error(f"Missing configuration section: {section}")
            return False
        
        for key in keys:
            if key not in config[section]:
                logging.error(f"Missing configuration key: {section}.{key}")
                return False
    
    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Contract Data Extraction and Documentation System'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='processing_results.json',
        help='Output file for results (default: processing_results.json)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("Contract Data Extraction and Documentation System")
    logger.info("=" * 80)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load and validate configuration
    logger.info(f"Loading configuration from: {args.config}")
    config = load_config(args.config)
    
    if not validate_config(config):
        logger.error("Configuration validation failed. Please check your config file.")
        sys.exit(1)
    
    logger.info("Configuration loaded and validated successfully")
    
    try:
        # Initialize processor
        logger.info("Initializing contract processor...")
        processor = ContractProcessor(config)
        
        # Process all contracts
        logger.info("Starting contract processing...")
        results = processor.process_all_contracts()
        
        # Save results
        logger.info(f"Saving results to: {args.output}")
        processor.save_results(args.output)
        
        # Print summary
        summary = processor.get_processing_summary()
        logger.info("=" * 80)
        logger.info("Processing Summary:")
        logger.info(f"  Total contracts: {summary['total']}")
        logger.info(f"  Successfully processed: {summary['completed']}")
        logger.info(f"  Failed: {summary['failed']}")
        logger.info(f"  Success rate: {summary['success_rate']}")
        logger.info("=" * 80)
        
        # Print Confluence parent page URL
        confluence_url = config['confluence']['url']
        space_key = config['confluence']['space_key']
        parent_title = config['confluence'].get('parent_page_title', 'Contract Summaries')
        logger.info(f"View results in Confluence: {confluence_url}/wiki/spaces/{space_key}")
        
        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Exit with appropriate code
        if summary['failed'] > 0:
            logger.warning("Some contracts failed to process. Check logs for details.")
            sys.exit(1)
        else:
            logger.info("All contracts processed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
