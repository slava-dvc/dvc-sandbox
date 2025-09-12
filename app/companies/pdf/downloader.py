import io
import re
import httpx
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from app.foundation.server import Logger
from app.foundation.env import get_env


class URLDownloader:
    def __init__(self, url: str, logger: Logger):
        self.url = url
        self.logger = logger

    @staticmethod
    async def _download_docsend(url: str, logger: Logger) -> bytes:
        """Download PDF from DocSend URL and return raw bytes"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                }
                
                # Use the API endpoint
                payload = {
                    "url": url,
                    "searchable": False
                }
                
                response = await client.post(
                    "https://docsend2pdf.com/api/convert",
                    headers=headers,
                    json=payload,
                    timeout=60,
                )
                response.raise_for_status()
                
                content_type = response.headers.get("content-type", "").lower()
                if "application/pdf" not in content_type:
                    raise ValueError(f"Failed to download PDF from DocSend. The document may be password protected, expired, or not publicly accessible. Please verify the link and try again.")
                
                return response.content
        except httpx.TimeoutException:
            raise ValueError(f"Download timed out. The DocSend document took too long to download. Please try again or contact support if the issue persists.")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise ValueError("DocSend conversion service is rate limited. Please wait a moment and try again.")
            elif e.response.status_code == 400:
                raise ValueError("Failed to download PDF from DocSend. The document URL may be invalid or malformed. Please verify the link and try again.")
            else:
                raise ValueError(f"DocSend conversion service returned an error (status {e.response.status_code}). The document may be password protected, expired, or not publicly accessible.")
        except Exception as e:
            if "Failed to download PDF from DocSend" in str(e) or "DocSend" in str(e):
                raise
            raise ValueError(f"Unable to download PDF from DocSend. This could be due to network issues, document restrictions, or an invalid link. Technical details: {str(e)}")

    @staticmethod
    async def _get_file_from_google_drive(url: str, logger: Logger) -> bytes:
        """Download PDF from Google Drive URL and return raw bytes"""
        # Extract the file ID from the URL
        match = re.search(r"/d/(.*?)/", url)
        if not match:
            raise ValueError("Invalid Google Drive URL. Please ensure the link is a valid Google Drive file URL (e.g., https://drive.google.com/file/d/FILE_ID/view).")
        
        file_id = match.group(1)
        
        # Try public download first (faster, no credentials needed)
        public_download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        
        try:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(public_download_url, follow_redirects=True, timeout=60)
                    response.raise_for_status()
                    
                    # Check if we got HTML (likely a permission page) instead of PDF
                    content_type = response.headers.get("content-type", "").lower()
                    if "text/html" in content_type:
                        # Fall back to authenticated API method
                        return await URLDownloader._get_file_from_google_drive_api(file_id)
                    
                    return response.content
                except httpx.HTTPStatusError:
                    # Fall back to authenticated API method
                    return await URLDownloader._get_file_from_google_drive_api(file_id)
        except httpx.TimeoutException:
            raise ValueError("Download timed out. The Google Drive file took too long to download. Please try again or check your internet connection.")
        except Exception as e:
            if "Unable to access Google Drive file" in str(e):
                raise
            raise ValueError(f"Unable to download PDF from Google Drive. The file may be private, deleted, or you may not have permission to access it. Please verify the sharing settings and try again. Technical details: {str(e)}")
    
    @staticmethod
    async def _get_file_from_google_drive_api(file_id: str) -> bytes:
        """Download PDF from Google Drive using authenticated API"""
        try:
            credentials_path = get_env('GOOGLE_DRIVE_CREDENTIALS_PATH')
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            drive_service = build("drive", "v3", credentials=credentials)
            
            # Request the file content from the API
            content_request = drive_service.files().get_media(fileId=file_id)
            
            # Create an in-memory file
            fh = io.BytesIO()
            
            # Download the file
            downloader = MediaIoBaseDownload(fh, content_request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Reset and return bytes
            fh.seek(0)
            return fh.read()
        except Exception as e:
            raise ValueError(f"Unable to access Google Drive file. The file may be private, deleted, or restricted. Please ensure the file is shared properly and accessible. Technical details: {str(e)}")

    async def _is_pdf(self) -> bool:
        """Check if URL points to a PDF file"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(self.url, follow_redirects=True, timeout=10)
                response.raise_for_status()
                
                content_type = response.headers.get("Content-Type", "").lower()
                if "application/pdf" in content_type:
                    return True
                
                content_disposition = response.headers.get("Content-Disposition", "").lower()
                if "filename" in content_disposition and ".pdf" in content_disposition:
                    return True
                
                # If headers don't indicate PDF, check first few bytes
                response = await client.get(self.url, headers={"Range": "bytes=0-4"})
                if response.content.startswith(b"%PDF-"):
                    return True
                
                return False
        except Exception:
            return False

    async def _download_pdf(self) -> bytes:
        """Download PDF from direct URL and return raw bytes"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, follow_redirects=True, timeout=60)
                response.raise_for_status()
                return response.content
        except httpx.TimeoutException:
            raise ValueError("Download timed out. The PDF file took too long to download. Please try again or check your internet connection.")
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Unable to download PDF. The server returned an error (status {e.response.status_code}). Please verify the URL is correct and accessible.")
        except Exception as e:
            raise ValueError(f"Failed to download PDF from the provided URL. This could be due to network issues or an invalid link. Technical details: {str(e)}")

    async def process_content(self) -> bytes:
        """Main method to download PDF from any supported URL type"""
        if "drive.google.com" in self.url:
            return await self._get_file_from_google_drive(self.url, self.logger)
        
        if "docsend.com" in self.url:
            return await self._download_docsend(self.url, self.logger)
        
        if not await self._is_pdf():
            raise ValueError(f"The provided URL does not contain a PDF file. Please ensure you're linking to a valid PDF document and try again. URL: {self.url}")
        
        return await self._download_pdf()


if __name__ == "__main__":
    import asyncio
    from pathlib import Path
    from app.foundation.server.logger import LocalLogger
    logger = LocalLogger()
    url = 'https://docsend.com/view/dshmfm4gjfdzrgnq'
    downloader = URLDownloader(url, logger)
    data = asyncio.run(downloader.process_content())
    Path('test.pdf').write_bytes(data)
