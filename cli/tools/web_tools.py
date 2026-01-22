"""
Web automation and search tools using Selenium and Tavily
"""
from .base import Tool, ToolResult
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import logging
from typing import Optional, Dict, List
from config import config

logger = logging.getLogger(__name__)

# Try to import tavily, but make it optional
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning("Tavily not installed. Web search will be limited.")

class WebBrowserTool(Tool):
    """Automate web browser actions using Selenium with headless Chromium"""
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.headless = True
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding https:// if no protocol is specified.
        
        Args:
            url: URL to normalize
            
        Returns:
            URL with protocol prefix
        """
        url = url.strip()
        if not url.startswith(('http://', 'https://', 'file://')):
            return f'https://{url}'
        return url
    
    def _get_driver(self):
        """Create and return a headless Chromium WebDriver"""
        if self.driver:
            return self.driver
        
        try:
            options = Options()
            
            if self.headless:
                options.add_argument('--headless=new')  # New headless mode
            
            # Common options for headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
            
            # Use Chromium binary explicitly
            options.binary_location = '/usr/bin/chromium-browser'  # Ubuntu path
            
            # Create driver
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
            
            logger.info("Chromium WebDriver initialized in headless mode")
            return self.driver
            
        except WebDriverException as e:
            logger.error(f"Failed to initialize Chromium driver: {e}")
            logger.info("Trying alternative Chromium paths...")
            
            # Try alternative paths
            for path in ['/usr/bin/chromium', '/snap/bin/chromium']:
                try:
                    options.binary_location = path
                    self.driver = webdriver.Chrome(options=options)
                    self.driver.set_page_load_timeout(30)
                    logger.info(f"Chromium WebDriver initialized using {path}")
                    return self.driver
                except:
                    continue
            
            raise Exception("Could not find Chromium browser. Install with: sudo apt install chromium-browser chromium-chromedriver")
    
    def execute(self, action: str, url: Optional[str] = None, selector: Optional[str] = None, 
                text: Optional[str] = None, attribute: Optional[str] = None) -> ToolResult:
        """
        Execute web browser actions
        
        Args:
            action: Action to perform (navigate, click, type, get_text, get_attribute, screenshot, close)
            url: URL to navigate to
            selector: CSS selector for element
            text: Text to type
            attribute: Attribute to get
            
        Returns:
            ToolResult with action result
        """
        try:
            driver = self._get_driver()
            
            if action == "navigate":
                if not url:
                    return ToolResult(success=False, output=None, error="URL required for navigate action")
                
                # Normalize URL - add https:// if no protocol specified
                normalized_url = self._normalize_url(url)
                
                driver.get(normalized_url)
                title = driver.title
                return ToolResult(
                    success=True,
                    output=f"Navigated to: {normalized_url}\nPage title: {title}"
                )
            
            elif action == "click":
                if not selector:
                    return ToolResult(success=False, output=None, error="Selector required for click action")
                
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                return ToolResult(success=True, output=f"Clicked element: {selector}")
            
            elif action == "type":
                if not selector or not text:
                    return ToolResult(success=False, output=None, error="Selector and text required for type action")
                
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(text)
                return ToolResult(success=True, output=f"Typed '{text}' into {selector}")
            
            elif action == "get_text":
                if not selector:
                    return ToolResult(success=False, output=None, error="Selector required for get_text action")
                
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                text = element.text
                return ToolResult(success=True, output=text)
            
            elif action == "get_attribute":
                if not selector or not attribute:
                    return ToolResult(success=False, output=None, error="Selector and attribute required")
                
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                value = element.get_attribute(attribute)
                return ToolResult(success=True, output=value)
            
            elif action == "screenshot":
                filename = url or "screenshot.png"
                driver.save_screenshot(filename)
                return ToolResult(success=True, output=f"Screenshot saved to: {filename}")
            
            elif action == "get_page_source":
                source = driver.page_source
                return ToolResult(success=True, output=source)
            
            elif action == "get_title":
                title = driver.title
                return ToolResult(success=True, output=title)
            
            elif action == "close":
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                return ToolResult(success=True, output="Browser closed")
            
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Unknown action: {action}. Valid: navigate, click, type, get_text, get_attribute, screenshot, get_page_source, get_title, close"
                )
            
        except TimeoutException:
            return ToolResult(
                success=False,
                output=None,
                error=f"Timeout waiting for element: {selector}"
            )
        except Exception as e:
            logger.error(f"WebBrowserTool error: {e}")
            return ToolResult(success=False, output=None, error=str(e))
    
    def __del__(self):
        """Cleanup driver on deletion"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

class WebScrapeTool(Tool):
    """Scrape web page content using Selenium"""
    
    def execute(self, url: str, selector: Optional[str] = None, 
                wait_for: Optional[str] = None) -> ToolResult:
        """
        Scrape content from a web page
        
        Args:
            url: URL to scrape
            selector: CSS selector for specific content (optional)
            wait_for: CSS selector to wait for before scraping (optional)
            
        Returns:
            ToolResult with scraped content
        """
        browser_tool = WebBrowserTool()
        
        try:
            # Navigate to URL
            result = browser_tool.execute("navigate", url=url)
            if not result.success:
                return result
            
            # Wait for specific element if requested
            if wait_for:
                import time
                time.sleep(2)  # Simple wait, could be improved
            
            # Get content
            if selector:
                result = browser_tool.execute("get_text", selector=selector)
            else:
                result = browser_tool.execute("get_page_source")
            
            # Cleanup
            browser_tool.execute("close")
            
            return result
            
        except Exception as e:
            browser_tool.execute("close")
            logger.error(f"WebScrapeTool error: {e}")
            return ToolResult(success=False, output=None, error=str(e))

class TavilySearchTool(Tool):
    """Search the web using Tavily AI search API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("TAVILY_API_KEY")
        
        if not TAVILY_AVAILABLE:
            logger.warning("Tavily package not installed")
            self.client = None
        elif not self.api_key:
            logger.warning("TAVILY_API_KEY not found in environment")
            self.client = None
        else:
            self.client = TavilyClient(api_key=self.api_key)
    
    def execute(self, query: str, search_depth: str = "basic", 
                max_results: int = 5, include_answer: bool = True) -> ToolResult:
        """
        Search the web using Tavily
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            max_results: Maximum number of results (1-10)
            include_answer: Whether to include AI-generated answer
            
        Returns:
            ToolResult with search results
        """
        if not self.client:
            return ToolResult(
                success=False,
                output=None,
                error="Tavily not configured. Install: pip install tavily-python\nSet TAVILY_API_KEY in .env"
            )
        
        try:
            # Perform search
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_answer=include_answer
            )
            
            # Format results
            output = []
            
            if include_answer and 'answer' in response:
                output.append(f"**AI Answer:**\n{response['answer']}\n")
            
            output.append(f"**Search Results for: {query}**\n")
            
            for idx, result in enumerate(response.get('results', []), 1):
                output.append(f"\n{idx}. **{result.get('title', 'No title')}**")
                output.append(f"   URL: {result.get('url', 'N/A')}")
                output.append(f"   {result.get('content', 'No content')[:200]}...")
            
            return ToolResult(
                success=True,
                output="\n".join(output)
            )
            
        except Exception as e:
            logger.error(f"TavilySearchTool error: {e}")
            return ToolResult(
                success=False,
                output=None,
                error=f"Search failed: {str(e)}"
            )

class WebExtractTool(Tool):
    """Extract structured data from web pages"""
    
    def execute(self, url: str, data_type: str = "text") -> ToolResult:
        """
        Extract data from a web page
        
        Args:
            url: URL to extract from
            data_type: Type of data (text, links, images, tables)
            
        Returns:
            ToolResult with extracted data
        """
        browser_tool = WebBrowserTool()
        
        try:
            # Navigate
            result = browser_tool.execute("navigate", url=url)
            if not result.success:
                return result
            
            driver = browser_tool._get_driver()
            
            if data_type == "text":
                # Extract all text
                text = driver.find_element(By.TAG_NAME, "body").text
                output = text
            
            elif data_type == "links":
                # Extract all links
                links = driver.find_elements(By.TAG_NAME, "a")
                output = "\n".join([
                    f"[{link.text}]({link.get_attribute('href')})"
                    for link in links if link.get_attribute('href')
                ])
            
            elif data_type == "images":
                # Extract image URLs
                images = driver.find_elements(By.TAG_NAME, "img")
                output = "\n".join([
                    img.get_attribute('src')
                    for img in images if img.get_attribute('src')
                ])
            
            elif data_type == "tables":
                # Extract table data
                tables = driver.find_elements(By.TAG_NAME, "table")
                output = f"Found {len(tables)} tables\n"
                for idx, table in enumerate(tables[:3], 1):  # Limit to 3 tables
                    output += f"\nTable {idx}:\n{table.text}\n"
            
            else:
                browser_tool.execute("close")
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Unknown data_type: {data_type}. Use: text, links, images, tables"
                )
            
            browser_tool.execute("close")
            
            return ToolResult(success=True, output=output)
            
        except Exception as e:
            browser_tool.execute("close")
            logger.error(f"WebExtractTool error: {e}")
            return ToolResult(success=False, output=None, error=str(e))
