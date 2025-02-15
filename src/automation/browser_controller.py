from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from typing import Dict, List, Optional
import asyncio
from urllib.parse import urlparse


class BrowserController:
    def __init__(self):
        self.drivers = {}
        self.supported_browsers = ['chrome', 'firefox']

    async def execute_action(self, action_data: Dict) -> Dict:
        """Execute browser action"""
        try:
            action = action_data.get('action')
            browser = action_data.get('browser', 'chrome').lower()

            if browser not in self.supported_browsers:
                raise ValueError(f"Unsupported browser: {browser}")

            if action == 'open':
                return await self._open_url(
                    browser,
                    action_data.get('url'),
                    action_data.get('private', False)
                )
            elif action == 'search':
                return await self._perform_search(
                    browser,
                    action_data.get('search_terms', ''),
                    action_data.get('private', False)
                )
            elif action == 'close':
                return await self._close_browser(browser)
            else:
                raise ValueError(f"Unsupported action: {action}")

        except Exception as e:
            print(f"Error in browser action: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def execute_actions(self, actions: List[Dict]) -> List[Dict]:
        """Execute multiple browser actions"""
        results = []
        for action in actions:
            result = await self.execute_action(action)
            results.append(result)
        return results

    async def _open_url(self, browser: str, url: Optional[str], private: bool = False) -> Dict:
        """Open URL in specified browser"""
        try:
            driver = await self._get_driver(browser, private)

            if url:
                # Add https if no protocol specified
                if not urlparse(url).scheme:
                    url = f"https://{url}"

                driver.get(url)
                await asyncio.sleep(1)  # Wait for page to load

                return {
                    "status": "success",
                    "message": f"Opened {url} in {browser}",
                    "url": url
                }
            else:
                return {
                    "status": "success",
                    "message": f"Opened new {browser} window"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to open URL: {str(e)}"
            }

    async def _perform_search(self, browser: str, search_terms: str, private: bool = False) -> Dict:
        """Perform search in specified browser"""
        try:
            driver = await self._get_driver(browser, private)

            # Go to Google
            driver.get("https://www.google.com")

            # Wait for search box and perform search
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(search_terms)
            search_box.send_keys(Keys.RETURN)

            await asyncio.sleep(1)  # Wait for results

            return {
                "status": "success",
                "message": f"Performed search for '{search_terms}' in {browser}",
                "search_terms": search_terms
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to perform search: {str(e)}"
            }

    async def _close_browser(self, browser: str) -> Dict:
        """Close specified browser"""
        try:
            if browser in self.drivers:
                self.drivers[browser].quit()
                del self.drivers[browser]
                return {
                    "status": "success",
                    "message": f"Closed {browser}"
                }
            return {
                "status": "success",
                "message": f"No {browser} instance to close"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to close browser: {str(e)}"
            }

    async def _get_driver(self, browser: str, private: bool = False):
        """Get or create webdriver for specified browser"""
        if browser not in self.drivers:
            if browser == 'chrome':
                options = ChromeOptions()
                if private:
                    options.add_argument("--incognito")
                options.add_argument("--start-maximized")
                self.drivers[browser] = webdriver.Chrome(options=options)
            elif browser == 'firefox':
                options = FirefoxOptions()
                if private:
                    options.add_argument("-private")
                options.add_argument("--start-maximized")
                self.drivers[browser] = webdriver.Firefox(options=options)

        return self.drivers[browser]

    def get_supported_browsers(self) -> List[str]:
        """Get list of supported browsers"""
        return self.supported_browsers

    async def cleanup(self):
        """Clean up all browser instances"""
        for browser, driver in self.drivers.items():
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()