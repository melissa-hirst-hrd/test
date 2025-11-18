"""
SharePoint client for reading contract PDFs.
"""
import logging
from typing import List, Dict, Optional
from io import BytesIO
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

logger = logging.getLogger(__name__)


class SharePointClient:
    """Client for interacting with SharePoint to retrieve contract PDFs."""
    
    def __init__(self, site_url: str, client_id: str, client_secret: str, 
                 tenant_id: str, contracts_folder: str):
        """
        Initialize SharePoint client.
        
        Args:
            site_url: SharePoint site URL
            client_id: Azure AD app client ID
            client_secret: Azure AD app client secret
            tenant_id: Azure AD tenant ID
            contracts_folder: Folder path containing contracts
        """
        self.site_url = site_url
        self.contracts_folder = contracts_folder
        
        # Authenticate
        credentials = ClientCredential(client_id, client_secret)
        self.ctx = ClientContext(site_url).with_credentials(credentials)
        
        logger.info(f"SharePoint client initialized for site: {site_url}")
    
    def list_pdf_files(self) -> List[Dict[str, str]]:
        """
        List all PDF files in the contracts folder.
        
        Returns:
            List of dictionaries with file metadata (name, url, size, modified)
        """
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(self.contracts_folder)
            files = folder.files
            self.ctx.load(files)
            self.ctx.execute_query()
            
            pdf_files = []
            for file in files:
                if file.name.lower().endswith('.pdf'):
                    pdf_files.append({
                        'name': file.name,
                        'server_relative_url': file.serverRelativeUrl,
                        'size': file.length,
                        'modified': file.time_last_modified.isoformat() if file.time_last_modified else None,
                        'unique_id': file.unique_id
                    })
            
            logger.info(f"Found {len(pdf_files)} PDF files in {self.contracts_folder}")
            return pdf_files
            
        except Exception as e:
            logger.error(f"Error listing PDF files: {e}")
            raise
    
    def download_file(self, server_relative_url: str) -> BytesIO:
        """
        Download a file from SharePoint.
        
        Args:
            server_relative_url: Server-relative URL of the file
            
        Returns:
            BytesIO object containing file content
        """
        try:
            file = self.ctx.web.get_file_by_server_relative_url(server_relative_url)
            content = file.read()
            self.ctx.execute_query()
            
            logger.info(f"Downloaded file: {server_relative_url}")
            return BytesIO(content)
            
        except Exception as e:
            logger.error(f"Error downloading file {server_relative_url}: {e}")
            raise
    
    def get_file_metadata(self, server_relative_url: str) -> Dict:
        """
        Get metadata for a specific file.
        
        Args:
            server_relative_url: Server-relative URL of the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            file = self.ctx.web.get_file_by_server_relative_url(server_relative_url)
            self.ctx.load(file)
            self.ctx.execute_query()
            
            return {
                'name': file.name,
                'size': file.length,
                'modified': file.time_last_modified.isoformat() if file.time_last_modified else None,
                'created': file.time_created.isoformat() if file.time_created else None,
                'unique_id': file.unique_id,
                'server_relative_url': file.serverRelativeUrl
            }
            
        except Exception as e:
            logger.error(f"Error getting file metadata for {server_relative_url}: {e}")
            raise
    
    def download_all_contracts(self) -> List[Dict]:
        """
        Download all contract PDFs with their metadata.
        
        Returns:
            List of dictionaries containing file metadata and content
        """
        pdf_files = self.list_pdf_files()
        contracts = []
        
        for pdf_file in pdf_files:
            try:
                content = self.download_file(pdf_file['server_relative_url'])
                contracts.append({
                    'metadata': pdf_file,
                    'content': content
                })
                logger.info(f"Successfully downloaded: {pdf_file['name']}")
            except Exception as e:
                logger.error(f"Failed to download {pdf_file['name']}: {e}")
                continue
        
        return contracts
