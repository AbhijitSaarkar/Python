

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
import argparse
import random
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Target website URL
HIYATH_URL = "https://hiyath.com/?srsltid=AfmBOopcte1TAMhlOHBiV3ewx2Oalldv8NhQf1MeG0TH_z8Yz4W8MPyw"

class HiyathVisitor:
    """Class to handle automated visits to the Hiyath website."""
    
    def __init__(self, headless=True, proxy=None):
        """
        Initialize the visitor with browser settings.
        
        Args:
            headless: Whether to run browser in headless mode
            proxy: Optional proxy string (format: "ip:port")
        """
        self.headless = headless
        self.proxy = proxy
        
        # Track statistics
        self.successful_visits = 0
        self.failed_visits = 0
        
        logger.info("HiyathVisitor initialized")
    
    def _create_driver(self):
        """Create a new Chrome driver instance with current settings."""
        options = webdriver.ChromeOptions()
        
        # Basic browser settings
        if self.headless:
            options.add_argument('--headless')
            logger.info("Running in headless mode")
        else:
            logger.info("Running in visible browser mode")
            
        # Standard settings to avoid detection
        options.add_argument('--disable-notifications')
        options.add_argument('--mute-audio')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        
        # Add random user agent to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # Apply proxy if provided
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            logger.info(f"Using proxy: {self.proxy}")
        
        # Create and return the driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)  # Set page load timeout
        return driver
    
    def _perform_natural_scrolling(self, driver, duration=30):
        """
        Scroll the page in a natural pattern for the specified duration.
        
        Args:
            driver: Selenium WebDriver instance
            duration: How long to scroll the page (in seconds)
        """
        logger.info("Starting natural page scrolling")
        
        # Track scrolling time
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            # Get page dimensions
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            # Current scroll position
            current_position = 0
            
            while time.time() < end_time:
                # Calculate remaining time
                remaining_time = end_time - time.time()
                if remaining_time <= 0:
                    break
                
                # Decide on scroll action based on current position
                position_ratio = current_position / page_height if page_height > 0 else 0
                
                # Different scrolling behaviors
                if position_ratio < 0.2:
                    # Near the top - mostly scroll down
                    scroll_direction = 1  # down
                    scroll_amount = random.randint(100, 300)
                    pause_time = random.uniform(0.7, 2.0)
                elif position_ratio > 0.8:
                    # Near the bottom - more likely to scroll up
                    if random.random() < 0.7:
                        scroll_direction = -1  # up
                        scroll_amount = random.randint(100, 400)
                    else:
                        scroll_direction = 1  # down
                        scroll_amount = random.randint(50, 150)
                    pause_time = random.uniform(1.0, 2.5)
                else:
                    # Middle of page - mixed scrolling
                    if random.random() < 0.2:
                        scroll_direction = -1  # up
                        scroll_amount = random.randint(50, 250)
                    else:
                        scroll_direction = 1  # down
                        scroll_amount = random.randint(100, 350)
                    pause_time = random.uniform(0.5, 2.0)
                
                # Occasionally jump to a random position (like a user looking for something)
                if random.random() < 0.1:
                    jump_position = random.randint(0, int(page_height * 0.8))
                    driver.execute_script(f"window.scrollTo(0, {jump_position});")
                    current_position = jump_position
                    logger.debug(f"Jumped to position {jump_position}")
                    time.sleep(random.uniform(1.5, 3.0))
                    continue
                
                # Apply the scroll
                scroll_pixels = scroll_direction * scroll_amount
                driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
                
                # Update current position
                current_position += scroll_pixels
                current_position = max(0, min(current_position, page_height))
                
                # Wait before next scroll
                time.sleep(pause_time)
                
                # Occasionally simulate user reading (longer pause)
                if random.random() < 0.15:
                    time.sleep(random.uniform(2.0, 4.0))
                
            logger.info(f"Completed scrolling for {duration} seconds")
            
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")
    
    def _simulate_user_interactions(self, driver):
        """
        Simulate additional user interactions on the page.
        
        Args:
            driver: Selenium WebDriver instance
        """
        try:
            # Occasionally hover over elements
            elements = driver.find_elements(By.TAG_NAME, "a")
            if elements and random.random() < 0.3:
                random_element = random.choice(elements[:10] if len(elements) > 10 else elements)
                try:
                    actions = webdriver.ActionChains(driver)
                    actions.move_to_element(random_element).perform()
                    logger.debug("Hovered over an element")
                    time.sleep(random.uniform(0.5, 1.5))
                except Exception:
                    pass
            
            # Occasionally resize window slightly
            if random.random() < 0.2:
                current_size = driver.get_window_size()
                new_width = current_size['width'] + random.randint(-50, 50)
                new_height = current_size['height'] + random.randint(-30, 30)
                new_width = max(800, new_width)  # Don't go too small
                new_height = max(600, new_height)
                driver.set_window_size(new_width, new_height)
                logger.debug(f"Resized window to {new_width}x{new_height}")
        
        except Exception as e:
            logger.debug(f"Error during user interactions: {e}")
    
    def visit_once(self):
        """
        Visit the Hiyath website once with natural behavior.
        
        Returns:
            bool: True if the visit was successful, False otherwise
        """
        driver = self._create_driver()
        
        try:
            # Visit the website
            logger.info(f"Visiting {HIYATH_URL}")
            driver.get(HIYATH_URL)
            
            # Wait for page to load
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info("Page loaded successfully")
            except TimeoutException:
                logger.warning("Page load timed out, continuing anyway")
            
            # Add a short pause after initial load
            time.sleep(random.uniform(1.0, 3.0))
            
            # Occasionally simulate user interactions
            self._simulate_user_interactions(driver)
            
            # Scroll the page naturally for 30 seconds
            self._perform_natural_scrolling(driver, duration=30)
            
            # Success
            self.successful_visits += 1
            return True
            
        except Exception as e:
            logger.error(f"Error during website visit: {e}")
            self.failed_visits += 1
            return False
            
        finally:
            # Always clean up
            try:
                driver.quit()
                logger.debug("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def run_visits(self, count=1000):
        """
        Visit the Hiyath website multiple times.
        
        Args:
            count: Number of visits to make
        """
        logger.info(f"Starting {count} visits to Hiyath website")
        
        for i in range(count):
            try:
                current_time = time.strftime("%H:%M:%S")
                logger.info(f"Visit {i+1}/{count} at {current_time}")
                
                success = self.visit_once()
                
                # Add a random delay between visits (3-10 seconds)
                if i < count - 1:  # Skip delay after last visit
                    delay = random.uniform(3, 10)
                    logger.info(f"Waiting {delay:.2f} seconds before next visit")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error in visit iteration {i+1}: {e}")
                self.failed_visits += 1
        
        # Print stats
        logger.info(f"Visits completed. Success: {self.successful_visits}, Failed: {self.failed_visits}")

    def run_with_proxy_file(self, count=1000, proxy_file=None):
        """
        Run visits using proxies from a file.
        
        Args:
            count: Number of visits to make
            proxy_file: Path to file containing proxies (one per line)
        """
        if not proxy_file or not os.path.exists(proxy_file):
            logger.warning(f"Proxy file not found: {proxy_file}")
            logger.info("Running without proxies")
            self.run_visits(count)
            return
            
        # Load proxies
        try:
            with open(proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            
            if not proxies:
                logger.warning("No proxies found in file. Running without proxies.")
                self.run_visits(count)
                return
                
            logger.info(f"Loaded {len(proxies)} proxies from {proxy_file}")
            
            # Run visits with proxies
            for i in range(count):
                try:
                    if i < len(proxies):
                        self.proxy = proxies[i]
                    else:
                        # Cycle through proxies if we have more visits than proxies
                        self.proxy = proxies[i % len(proxies)]
                        
                    current_time = time.strftime("%H:%M:%S")
                    logger.info(f"Visit {i+1}/{count} at {current_time} with proxy {self.proxy}")
                    
                    success = self.visit_once()
                    
                    # Add a random delay between visits (3-10 seconds)
                    if i < count - 1:  # Skip delay after last visit
                        delay = random.uniform(3, 10)
                        logger.info(f"Waiting {delay:.2f} seconds before next visit")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"Error in visit iteration {i+1}: {e}")
                    self.failed_visits += 1
                    
        except Exception as e:
            logger.error(f"Error processing proxy file: {e}")
            logger.info("Falling back to visits without proxies")
            self.run_visits(count)
            
        # Print stats
        logger.info(f"Visits completed. Success: {self.successful_visits}, Failed: {self.failed_visits}")


def main():
    """Parse command line arguments and run the visitor."""
    parser = argparse.ArgumentParser(description="Hiyath Website Visitor Bot")
    
    parser.add_argument("--count", type=int, default=1000, 
                        help="Number of website visits (default: 1000)")
    parser.add_argument("--visible", action="store_true", 
                        help="Run in visible mode instead of headless")
    parser.add_argument("--proxy-file", type=str, 
                        help="Path to file containing proxies (one per line)")
    parser.add_argument("--demo", action="store_true", 
                        help="Run in demo mode with just 3 visits")
    
    args = parser.parse_args()
    
    # Apply demo mode if selected
    if args.demo:
        args.count = 3
        logger.info("Running in demo mode with just 3 visits")
    
    # Create visitor
    visitor = HiyathVisitor(headless=not args.visible)
    
    # Run with or without proxy file
    if args.proxy_file:
        visitor.run_with_proxy_file(count=args.count, proxy_file=args.proxy_file)
    else:
        visitor.run_visits(count=args.count)


if __name__ == "__main__":
    main()