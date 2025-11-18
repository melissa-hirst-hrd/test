"""
Main contract processor orchestration logic.
"""
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from sharepoint_client import SharePointClient
from claude_client import ClaudeClient
from confluence_client import ConfluenceClient
from pdf_processor import PDFProcessor
from prompts import get_extraction_prompt, get_summary_prompt, get_validation_prompt

logger = logging.getLogger(__name__)


class ContractProcessor:
    """Main processor for orchestrating contract extraction and documentation workflow."""
    
    def __init__(self, config: Dict):
        """
        Initialize the contract processor with all required clients.
        
        Args:
            config: Configuration dictionary with SharePoint, Claude, and Confluence settings
        """
        self.config = config
        
        # Initialize clients
        sp_config = config['sharepoint']
        self.sharepoint_client = SharePointClient(
            site_url=sp_config['site_url'],
            client_id=sp_config['client_id'],
            client_secret=sp_config['client_secret'],
            tenant_id=sp_config['tenant_id'],
            contracts_folder=sp_config['contracts_folder']
        )
        
        claude_config = config['claude']
        self.claude_client = ClaudeClient(
            api_key=claude_config['api_key'],
            model=claude_config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=claude_config.get('max_tokens', 4096)
        )
        
        confluence_config = config['confluence']
        self.confluence_client = ConfluenceClient(
            url=confluence_config['url'],
            username=confluence_config['username'],
            api_token=confluence_config['api_token'],
            space_key=confluence_config['space_key']
        )
        
        self.pdf_processor = PDFProcessor()
        
        # Processing configuration
        self.batch_size = config.get('processing', {}).get('batch_size', 5)
        self.parent_page_title = confluence_config.get('parent_page_title', 'Contract Summaries')
        
        # Results storage
        self.results = []
        
        logger.info("Contract processor initialized successfully")
    
    def process_single_contract(self, contract_data: Dict) -> Dict:
        """
        Process a single contract through the full pipeline.
        
        Args:
            contract_data: Dictionary with 'metadata' and 'content' keys
            
        Returns:
            Dictionary with processing results
        """
        metadata = contract_data['metadata']
        file_name = metadata['name']
        
        logger.info(f"Processing contract: {file_name}")
        
        result = {
            'file_name': file_name,
            'metadata': metadata,
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Extract text from PDF
            logger.info(f"Extracting text from {file_name}...")
            pdf_content = contract_data['content']
            contract_text = self.pdf_processor.extract_text(pdf_content)
            pdf_info = self.pdf_processor.get_pdf_info(pdf_content)
            
            result['pdf_info'] = pdf_info
            result['text_length'] = len(contract_text)
            
            if not contract_text.strip():
                raise ValueError("No text extracted from PDF")
            
            logger.info(f"Extracted {len(contract_text)} characters from {file_name}")
            
            # Step 2: Extract structured data using Claude
            logger.info(f"Extracting data from {file_name} using Claude AI...")
            extraction_prompt = get_extraction_prompt(contract_text)
            extracted_data = self.claude_client.extract_contract_data(
                contract_text, 
                extraction_prompt
            )
            
            result['extracted_data'] = extracted_data
            logger.info(f"Successfully extracted data from {file_name}")
            
            # Step 3: Generate summary document
            logger.info(f"Generating summary for {file_name}...")
            summary_prompt = get_summary_prompt(extracted_data)
            summary_content = self.claude_client.generate_summary(
                extracted_data,
                summary_prompt
            )
            
            result['summary_content'] = summary_content
            logger.info(f"Generated summary for {file_name}")
            
            # Step 4: Create Confluence pages
            logger.info(f"Creating Confluence pages for {file_name}...")
            
            # Get or create parent page
            parent_page_id = self.confluence_client.get_or_create_parent_page(
                self.parent_page_title
            )
            
            # Create summary page
            page_info = self.confluence_client.create_contract_summary_page(
                contract_name=file_name.replace('.pdf', ''),
                summary_content=summary_content,
                parent_page_id=parent_page_id
            )
            
            result['confluence_page'] = page_info
            result['status'] = 'completed'
            
            # Add label for easy filtering
            try:
                self.confluence_client.add_label_to_page(page_info['id'], 'contract')
            except Exception as e:
                logger.warning(f"Could not add label: {e}")
            
            logger.info(f"Successfully processed {file_name}. Confluence page: {page_info['url']}")
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            logger.error(f"Failed to process {file_name}: {e}", exc_info=True)
        
        return result
    
    def process_all_contracts(self) -> List[Dict]:
        """
        Process all contracts from SharePoint.
        
        Returns:
            List of processing results for each contract
        """
        logger.info("Starting to process all contracts from SharePoint")
        
        try:
            # Download all contracts
            logger.info("Downloading contracts from SharePoint...")
            contracts = self.sharepoint_client.download_all_contracts()
            logger.info(f"Downloaded {len(contracts)} contracts")
            
            if not contracts:
                logger.warning("No contracts found to process")
                return []
            
            # Process each contract
            results = []
            for i, contract_data in enumerate(contracts, 1):
                logger.info(f"Processing contract {i}/{len(contracts)}")
                result = self.process_single_contract(contract_data)
                results.append(result)
                self.results.append(result)
            
            # Create master summary table
            logger.info("Creating master summary table...")
            try:
                parent_page_id = self.confluence_client.get_or_create_parent_page(
                    self.parent_page_title
                )
                master_summary = self.confluence_client.create_master_summary_table(
                    parent_page_id,
                    results
                )
                logger.info(f"Master summary created: {master_summary.get('url', 'N/A')}")
            except Exception as e:
                logger.error(f"Failed to create master summary table: {e}")
            
            # Log summary statistics
            successful = len([r for r in results if r['status'] == 'completed'])
            failed = len([r for r in results if r['status'] == 'failed'])
            
            logger.info(f"Processing complete: {successful} successful, {failed} failed")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing contracts: {e}", exc_info=True)
            raise
    
    def save_results(self, output_file: str = 'processing_results.json'):
        """
        Save processing results to a JSON file.
        
        Args:
            output_file: Path to output file
        """
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def get_processing_summary(self) -> Dict:
        """
        Get a summary of processing results.
        
        Returns:
            Dictionary with summary statistics
        """
        if not self.results:
            return {'total': 0, 'completed': 0, 'failed': 0}
        
        total = len(self.results)
        completed = len([r for r in self.results if r['status'] == 'completed'])
        failed = len([r for r in self.results if r['status'] == 'failed'])
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'success_rate': f"{(completed/total)*100:.1f}%" if total > 0 else "0%"
        }
