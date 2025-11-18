"""
Confluence client for creating and updating contract documentation.
"""
import logging
from typing import Dict, Optional, List
from atlassian import Confluence

logger = logging.getLogger(__name__)


class ConfluenceClient:
    """Client for interacting with Confluence to create contract documentation."""
    
    def __init__(self, url: str, username: str, api_token: str, space_key: str):
        """
        Initialize Confluence client.
        
        Args:
            url: Confluence instance URL
            username: Confluence username/email
            api_token: Confluence API token
            space_key: Space key where documents will be created
        """
        self.confluence = Confluence(
            url=url,
            username=username,
            password=api_token,
            cloud=True
        )
        self.space_key = space_key
        
        logger.info(f"Confluence client initialized for space: {space_key}")
    
    def get_or_create_parent_page(self, parent_title: str) -> str:
        """
        Get or create the parent page for contract summaries.
        
        Args:
            parent_title: Title of the parent page
            
        Returns:
            Page ID of the parent page
        """
        try:
            # Try to find existing page
            page = self.confluence.get_page_by_title(
                space=self.space_key,
                title=parent_title
            )
            
            if page:
                logger.info(f"Found existing parent page: {parent_title} (ID: {page['id']})")
                return page['id']
            
            # Create parent page if it doesn't exist
            new_page = self.confluence.create_page(
                space=self.space_key,
                title=parent_title,
                body="""
                <h2>Contract Summaries</h2>
                <p>This page contains summaries of all analyzed contracts.</p>
                <p>Each contract is documented in a separate child page.</p>
                """
            )
            
            logger.info(f"Created parent page: {parent_title} (ID: {new_page['id']})")
            return new_page['id']
            
        except Exception as e:
            logger.error(f"Error getting/creating parent page: {e}")
            raise
    
    def create_contract_summary_page(self, contract_name: str, summary_content: str,
                                    parent_page_id: Optional[str] = None) -> Dict:
        """
        Create a Confluence page for a contract summary.
        
        Args:
            contract_name: Name of the contract (used as page title)
            summary_content: HTML/wiki markup content for the page
            parent_page_id: Optional parent page ID
            
        Returns:
            Dictionary with page information (id, url, title)
        """
        try:
            # Clean contract name for page title
            page_title = f"Contract Summary - {contract_name}"
            
            # Check if page already exists
            existing_page = self.confluence.get_page_by_title(
                space=self.space_key,
                title=page_title
            )
            
            if existing_page:
                # Update existing page
                updated_page = self.confluence.update_page(
                    page_id=existing_page['id'],
                    title=page_title,
                    body=summary_content,
                    parent_id=parent_page_id
                )
                logger.info(f"Updated existing page: {page_title}")
                page_info = updated_page
            else:
                # Create new page
                new_page = self.confluence.create_page(
                    space=self.space_key,
                    title=page_title,
                    body=summary_content,
                    parent_id=parent_page_id
                )
                logger.info(f"Created new page: {page_title}")
                page_info = new_page
            
            return {
                'id': page_info['id'],
                'title': page_info['title'],
                'url': f"{self.confluence.url}/wiki/spaces/{self.space_key}/pages/{page_info['id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating/updating contract summary page: {e}")
            raise
    
    def create_master_summary_table(self, parent_page_id: str, 
                                   contracts_data: List[Dict]) -> Dict:
        """
        Create or update a master summary table with all contracts.
        
        Args:
            parent_page_id: ID of the parent page
            contracts_data: List of dictionaries with contract information
            
        Returns:
            Dictionary with page information
        """
        try:
            # Build HTML table with all contracts
            table_html = """
            <h2>All Contracts Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Contract Name</th>
                        <th>Parties</th>
                        <th>Effective Date</th>
                        <th>Expiration Date</th>
                        <th>Value</th>
                        <th>Status</th>
                        <th>Summary Link</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for contract in contracts_data:
                extracted = contract.get('extracted_data', {})
                page_info = contract.get('confluence_page', {})
                
                # Extract key fields (adjust based on your extraction structure)
                name = extracted.get('contract_name', contract.get('file_name', 'N/A'))
                parties = extracted.get('parties', 'N/A')
                if isinstance(parties, list):
                    parties = ', '.join(parties[:2])  # Show first 2 parties
                effective_date = extracted.get('effective_date', 'N/A')
                expiration_date = extracted.get('expiration_date', 'N/A')
                value = extracted.get('contract_value', 'N/A')
                status = extracted.get('status', 'Active')
                
                page_url = page_info.get('url', '#')
                page_title = page_info.get('title', 'View Details')
                
                table_html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{parties}</td>
                        <td>{effective_date}</td>
                        <td>{expiration_date}</td>
                        <td>{value}</td>
                        <td>{status}</td>
                        <td><a href="{page_url}">{page_title}</a></td>
                    </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            <p><em>Last updated: {timestamp}</em></p>
            """
            
            from datetime import datetime
            table_html = table_html.format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Update parent page with the table
            updated_page = self.confluence.update_page(
                page_id=parent_page_id,
                title="Contract Summaries",
                body=table_html
            )
            
            logger.info(f"Updated master summary table with {len(contracts_data)} contracts")
            
            return {
                'id': updated_page['id'],
                'title': updated_page['title'],
                'url': f"{self.confluence.url}/wiki/spaces/{self.space_key}/pages/{updated_page['id']}"
            }
            
        except Exception as e:
            logger.error(f"Error creating master summary table: {e}")
            raise
    
    def add_label_to_page(self, page_id: str, label: str):
        """
        Add a label to a Confluence page.
        
        Args:
            page_id: Page ID
            label: Label to add
        """
        try:
            self.confluence.set_page_label(page_id, label)
            logger.info(f"Added label '{label}' to page {page_id}")
        except Exception as e:
            logger.warning(f"Could not add label to page: {e}")
