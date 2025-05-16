import requests
from bs4 import BeautifulSoup
import random
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import argparse
import os

# Import your existing HumanLikeVisitor class
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time
import logging
import argparse
import random
import os
from selenium.webdriver.common.action_chains import ActionChains

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Target website URL
HIYATH_URL = "https://hiyath.com/?srsltid=AfmBOopcte1TAMhlOHBiV3ewx2Oalldv8NhQf1MeG0TH_z8Yz4W8MPyw"

class HumanLikeVisitor:
    """Class to handle automated visits to the Hiyath website with human-like behavior."""
    
    def __init__(self, headless=False, proxy=None):
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
        
        # Define possible window sizes (simulating different devices/monitors)
        self.window_sizes = [
            (1366, 768),   # Standard laptop
            (1920, 1080),  # Full HD monitor
            (1440, 900),   # MacBook
            (1536, 864),   # Common Windows size
            (1280, 800),   # Small laptop
            (1680, 1050),  # Larger laptop/monitor
        ]
        
        logger.info("HumanLikeVisitor initialized")
    
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
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-extensions')
        options.add_argument('--mute-audio')
        
        # Choose a random window size
        window_size = random.choice(self.window_sizes)
        if random.random() < 0.7:
            # Add minor random variations to window size
            window_size = (
                window_size[0] + random.randint(-50, 50),
                window_size[1] + random.randint(-30, 30)
            )
        
        # Apply window size
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        logger.info(f"Setting window size to {window_size[0]}x{window_size[1]}")
        
        # Add random user agent to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/109.0.5414.83 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1'
        ]
        selected_user_agent = random.choice(user_agents)
        options.add_argument(f'user-agent={selected_user_agent}')
        logger.info(f"Using user-agent: {selected_user_agent[:30]}...")
        
        # Apply proxy if provided
        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')
            logger.info(f"Using proxy: {self.proxy}")
        
        # Create and return the driver
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)  # Set page load timeout
        
        # Randomize window position slightly
        x_pos = random.randint(0, 100)
        y_pos = random.randint(0, 50)
        driver.set_window_position(x_pos, y_pos)
        
        return driver
    
    def _human_like_typing(self, element, text, min_delay=0.05, max_delay=0.25):
        """
        Type text into an element with human-like variations in timing.
        
        Args:
            element: Selenium WebElement to type into
            text: Text to type
            min_delay: Minimum delay between keystrokes
            max_delay: Maximum delay between keystrokes
        """
        for char in text:
            element.send_keys(char)
            # Random delay between keystrokes
            time.sleep(random.uniform(min_delay, max_delay))
            
            # Occasionally pause as if thinking
            if random.random() < 0.1:
                time.sleep(random.uniform(0.5, 1.5))
    
    def _perform_natural_scrolling(self, driver, duration=15):
        """
        Scroll the page in a natural, human-like pattern.
        
        Args:
            driver: Selenium WebDriver instance
            duration: Maximum time to spend scrolling (in seconds)
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
            
            # Reading patterns
            reading_patterns = [
                # Pattern: [scroll amount, pause time]
                [(50, 150), (0.8, 1.5)],     # Slow, careful reading
                [(100, 300), (0.5, 1.2)],    # Normal reading pace
                [(200, 500), (0.3, 0.8)],    # Skimming
                [(400, 800), (0.2, 0.5)],    # Fast scrolling
            ]
            
            # Select a primary reading pattern for this session
            primary_pattern = random.choice(reading_patterns)
            
            while time.time() < end_time:
                # Calculate remaining time
                remaining_time = end_time - time.time()
                if remaining_time <= 0:
                    break
                
                # Decide current reading pattern
                if random.random() < 0.8:
                    # Use primary pattern 80% of the time
                    pattern = primary_pattern
                else:
                    # Occasionally switch patterns
                    pattern = random.choice(reading_patterns)
                
                # Get pattern details
                scroll_range, pause_range = pattern
                
                # Decide on scroll action based on current position
                position_ratio = current_position / page_height if page_height > 0 else 0
                
                # Determine scroll direction and amount
                if position_ratio > 0.9:
                    # Near bottom - more likely to scroll up
                    if random.random() < 0.7:
                        scroll_direction = -1  # up
                        scroll_amount = random.randint(200, 600)
                    else:
                        scroll_direction = 1  # down
                        scroll_amount = random.randint(30, 100)
                elif position_ratio < 0.1 and current_position > 0:
                    # Near top but not at very top - mixed direction
                    if random.random() < 0.3:
                        scroll_direction = -1  # up
                        scroll_amount = random.randint(50, 150)
                    else:
                        scroll_direction = 1  # down
                        scroll_amount = random.randint(100, 300)
                else:
                    # Middle sections - mostly scrolling down with occasional up scrolls
                    if random.random() < 0.15:
                        scroll_direction = -1  # up
                        scroll_amount = random.randint(100, 350)
                    else:
                        scroll_direction = 1  # down
                        scroll_amount = random.randint(scroll_range[0], scroll_range[1])
                
                # Occasionally simulate "finding something interesting"
                if random.random() < 0.15:
                    # Slow down and make smaller scrolls as if reading something interesting
                    small_scrolls = random.randint(2, 5)
                    for _ in range(small_scrolls):
                        tiny_scroll = random.randint(10, 40)
                        driver.execute_script(f"window.scrollBy(0, {tiny_scroll});")
                        current_position += tiny_scroll
                        time.sleep(random.uniform(0.5, 1.5))
                    
                    # Maybe scroll back up slightly as if re-reading
                    if random.random() < 0.4:
                        back_scroll = random.randint(-100, -20)
                        driver.execute_script(f"window.scrollBy(0, {back_scroll});")
                        current_position += back_scroll
                        time.sleep(random.uniform(0.7, 1.8))
                    
                    continue
                
                # Occasionally jump to a random section (like searching for something)
                if random.random() < 0.08:
                    jump_position = random.randint(0, int(page_height * 0.8))
                    driver.execute_script(f"window.scrollTo(0, {jump_position});")
                    current_position = jump_position
                    logger.debug(f"Jumped to position {jump_position}")
                    time.sleep(random.uniform(1.0, 2.5))
                    continue
                
                # Apply the scroll
                scroll_pixels = scroll_direction * scroll_amount
                driver.execute_script(f"window.scrollBy(0, {scroll_pixels});")
                
                # Update current position
                current_position += scroll_pixels
                current_position = max(0, min(current_position, page_height))
                
                # Wait before next scroll - use pattern's timing
                time.sleep(random.uniform(pause_range[0], pause_range[1]))
                
                # Occasionally pause longer, as if the user got distracted
                if random.random() < 0.05:
                    time.sleep(random.uniform(1.5, 3.0))
                
            logger.info(f"Completed scrolling for {duration} seconds")
            
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")
    
    def _interact_with_random_elements(self, driver, duration=15):
        """
        Interact with random elements on the page in a human-like way.
        
        Args:
            driver: Selenium WebDriver instance
            duration: Maximum time to spend interacting (in seconds)
        """
        logger.info("Starting random element interactions")
        
        # Track interaction time
        start_time = time.time()
        end_time = start_time + duration
        
        # Counter for page navigations
        page_navigations = 0
        max_navigations = random.randint(1, 3)  # Limit navigations away from main page
        
        try:
            while time.time() < end_time and page_navigations < max_navigations:
                # Break if we're getting close to the time limit
                if end_time - time.time() < 3:
                    break
                
                # Decide what kind of elements to interact with
                interaction_type = random.choice([
                    'links', 'buttons', 'hover', 'images', 'text'
                ])
                
                if interaction_type == 'links':
                    # Find clickable links that look interesting
                    try:
                        links = driver.find_elements(By.TAG_NAME, "a")
                        # Filter out empty links or navigation elements
                        visible_links = []
                        for link in links[:20]:  # Check first 20 only for performance
                            try:
                                if link.is_displayed() and link.text.strip() and len(link.text) > 3:
                                    visible_links.append(link)
                            except StaleElementReferenceException:
                                continue
                        
                        if visible_links:
                            chosen_link = random.choice(visible_links)
                            link_text = chosen_link.text.strip()[:30]
                            logger.info(f"Clicking on link: {link_text}...")
                            
                            # Move mouse to element first
                            actions = ActionChains(driver)
                            actions.move_to_element(chosen_link).pause(random.uniform(0.3, 0.8)).perform()
                            
                            # Click the link
                            chosen_link.click()
                            page_navigations += 1
                            
                            # Record current URL to check if we navigated
                            current_url = driver.current_url
                            
                            # Wait on the new page for a bit
                            view_time = random.uniform(3.0, 8.0)
                            logger.info(f"Viewing new page for {view_time:.1f} seconds")
                            time.sleep(view_time)
                            
                            # Do some scrolling on the new page
                            self._brief_scrolling(driver, duration=random.uniform(2.0, 4.0))
                            
                            # Go back to the main page
                            driver.back()
                            logger.info("Navigated back to main page")
                            
                            # Wait for page to reload
                            time.sleep(random.uniform(1.0, 2.0))
                    except Exception as e:
                        logger.error(f"Error interacting with links: {e}")
                
                elif interaction_type == 'buttons':
                    # Find and click a button
                    try:
                        buttons = driver.find_elements(By.TAG_NAME, "button")
                        buttons.extend(driver.find_elements(By.CSS_SELECTOR, ".btn, .button"))
                        
                        visible_buttons = []
                        for button in buttons:
                            try:
                                if button.is_displayed():
                                    visible_buttons.append(button)
                            except StaleElementReferenceException:
                                continue
                        
                        if visible_buttons:
                            chosen_button = random.choice(visible_buttons)
                            button_text = chosen_button.text.strip()[:30] if chosen_button.text else "unnamed button"
                            logger.info(f"Clicking button: {button_text}")
                            
                            # Move mouse to button
                            actions = ActionChains(driver)
                            actions.move_to_element(chosen_button).pause(random.uniform(0.2, 0.6)).perform()
                            
                            # Click the button
                            chosen_button.click()
                            
                            # Wait to see what happens
                            time.sleep(random.uniform(1.5, 3.0))
                            
                            # If a modal appeared, possibly close it
                            try:
                                close_buttons = driver.find_elements(By.CSS_SELECTOR, ".close, .modal-close, [aria-label='Close']")
                                for close_btn in close_buttons:
                                    if close_btn.is_displayed():
                                        logger.info("Closing a modal/popup")
                                        close_btn.click()
                                        time.sleep(random.uniform(0.5, 1.0))
                                        break
                            except Exception:
                                pass
                    except Exception as e:
                        logger.error(f"Error interacting with buttons: {e}")
                
                elif interaction_type == 'hover':
                    # Hover over various elements
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, "a, button, .card, .product, img")
                        visible_elements = []
                        for elem in elements[:30]:  # Check first 30 only
                            try:
                                if elem.is_displayed():
                                    visible_elements.append(elem)
                            except:
                                continue
                        
                        if visible_elements:
                            # Hover over several elements in sequence
                            hover_count = random.randint(2, 5)
                            random.shuffle(visible_elements)
                            
                            actions = ActionChains(driver)
                            for i in range(min(hover_count, len(visible_elements))):
                                try:
                                    elem = visible_elements[i]
                                    logger.debug(f"Hovering over element {i+1}")
                                    actions.move_to_element(elem).pause(random.uniform(0.5, 1.5)).perform()
                                except:
                                    continue
                    except Exception as e:
                        logger.error(f"Error during hover interactions: {e}")
                
                elif interaction_type == 'images':
                    # Look at images
                    try:
                        images = driver.find_elements(By.TAG_NAME, "img")
                        visible_images = []
                        for img in images:
                            try:
                                if img.is_displayed() and img.size['height'] > 50 and img.size['width'] > 50:
                                    visible_images.append(img)
                            except:
                                continue
                        
                        if visible_images:
                            chosen_image = random.choice(visible_images)
                            logger.info("Looking at an image")
                            
                            # Scroll to image
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_image)
                            time.sleep(random.uniform(0.8, 2.0))
                            
                            # Sometimes click the image
                            if random.random() < 0.4:
                                try:
                                    chosen_image.click()
                                    time.sleep(random.uniform(1.0, 3.0))
                                    
                                    # If we navigated, go back
                                    if driver.current_url != current_url:
                                        time.sleep(random.uniform(2.0, 4.0))
                                        driver.back()
                                        time.sleep(random.uniform(1.0, 2.0))
                                        page_navigations += 1
                                except:
                                    pass
                    except Exception as e:
                        logger.error(f"Error interacting with images: {e}")
                
                elif interaction_type == 'text':
                    # Read some text content
                    try:
                        text_elements = driver.find_elements(By.CSS_SELECTOR, "p, h1, h2, h3, .description, .product-description")
                        visible_texts = []
                        for elem in text_elements:
                            try:
                                if elem.is_displayed() and elem.text.strip():
                                    visible_texts.append(elem)
                            except:
                                continue
                        
                        if visible_texts:
                            chosen_text = random.choice(visible_texts)
                            logger.info("Reading some text content")
                            
                            # Scroll to the text
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", chosen_text) 
                            
                            # Simulate reading time based on text length
                            text_length = len(chosen_text.text)
                            reading_time = min(5.0, max(1.0, text_length * 0.02))  # About 50 chars per second
                            time.sleep(reading_time)
                    except Exception as e:
                        logger.error(f"Error reading text content: {e}")
                
                # Wait before next interaction
                time.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            logger.error(f"Error during element interactions: {e}")
    
    def _brief_scrolling(self, driver, duration=3.0):
        """
        Brief scrolling sequence for when viewing a secondary page.
        
        Args:
            driver: Selenium WebDriver instance
            duration: Maximum time to spend scrolling (in seconds)
        """
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            # Simple scrolling pattern
            while time.time() < end_time:
                scroll_amount = random.randint(100, 300)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            logger.debug(f"Error during brief scrolling: {e}")
    
    def _simulate_user_session(self, driver, total_duration=30):
        """
        Simulate a complete user session with various activities.
        
        Args:
            driver: Selenium WebDriver instance
            total_duration: Total time to spend on the site (in seconds)
        """
        # Initial waiting time after page load
        initial_wait = random.uniform(1.0, 3.0)
        logger.info(f"Initial wait for {initial_wait:.1f} seconds")
        time.sleep(initial_wait)
        
        # Adjust remaining time
        remaining_time = total_duration - initial_wait
        
        # Decide how to split time between scrolling and interactions
        # Most time spent scrolling (60-80%), rest on interactions
        scrolling_ratio = random.uniform(0.6, 0.8)
        
        scrolling_time = remaining_time * scrolling_ratio
        interaction_time = remaining_time - scrolling_time
        
        # Randomize order: sometimes interact first, sometimes scroll first
        if random.random() < 0.3:
            # Interact first, then scroll
            logger.info(f"Starting with interactions for {interaction_time:.1f} seconds, then scrolling")
            self._interact_with_random_elements(driver, duration=interaction_time)
            self._perform_natural_scrolling(driver, duration=scrolling_time)
        else:
            # Scroll first, then interact
            logger.info(f"Starting with scrolling for {scrolling_time:.1f} seconds, then interactions")
            self._perform_natural_scrolling(driver, duration=scrolling_time)
            self._interact_with_random_elements(driver, duration=interaction_time)
        
        # Sometimes add some final scrolling if time permits
        if random.random() < 0.5:
            final_scroll_time = random.uniform(1.0, 3.0)
            logger.info("Adding final scroll before leaving")
            self._brief_scrolling(driver, duration=final_scroll_time)
    
    def visit_once(self):
        """
        Visit the Hiyath website once with human-like behavior.
        
        Returns:
            bool: True if the visit was successful, False otherwise
        """
        driver = self._create_driver()
        start_time = time.time()
        
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
            
            # Run the human-like session for 30 seconds
            self._simulate_user_session(driver, total_duration=30)
            
            # Success
            self.successful_visits += 1
            return True
            
        except Exception as e:
            logger.error(f"Error during website visit: {e}")
            self.failed_visits += 1
            return False
            
        finally:
            # Calculate actual session time
            session_time = time.time() - start_time
            logger.info(f"Session completed in {session_time:.1f} seconds")
            
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


# New ProxyManager class to fetch and verify free proxies
# Complete this ProxyManager class that was cut off in the original code
class ProxyManager:
    """Class to fetch, test, and manage free proxies."""
    
    def __init__(self, cache_file="verified_proxies.json", max_proxies=100):
        """
        Initialize the proxy manager.
        
        Args:
            cache_file: File to cache verified proxies
            max_proxies: Maximum number of proxies to maintain
        """
        self.cache_file = cache_file
        self.max_proxies = max_proxies
        self.verified_proxies = []
        self.used_proxies = set()
        
        # IP checking service URLs
        self.ip_check_urls = [
            "https://api.ipify.org",
            "https://ifconfig.me/ip",
            "https://icanhazip.com",
            "https://ipinfo.io/json"
        ]
        
        # Load cached proxies if available
        self._load_cache()
        logger.info(f"ProxyManager initialized with {len(self.verified_proxies)} cached proxies")
    
    def _load_cache(self):
        """Load verified proxies from cache file if it exists."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.verified_proxies = data
                        logger.info(f"Loaded {len(self.verified_proxies)} proxies from cache")
        except Exception as e:
            logger.error(f"Error loading proxy cache: {e}")
            # Start with empty list if cache loading fails
            self.verified_proxies = []
    
    def _save_cache(self):
        """Save verified proxies to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.verified_proxies, f)
            logger.info(f"Saved {len(self.verified_proxies)} proxies to cache")
        except Exception as e:
            logger.error(f"Error saving proxy cache: {e}")
    
    def fetch_free_proxies(self, min_proxies=10):
        """
        Fetch free proxies from various sources.
        
        Args:
            min_proxies: Minimum number of proxies to collect
        
        Returns:
            list: List of proxy strings in format "ip:port"
        """
        logger.info("Fetching free proxies from multiple sources")
        proxies = set()
        
        # Try multiple free proxy sources
        sources = [
            self._fetch_proxies_from_free_proxy_list,
            self._fetch_proxies_from_geonode,
            self._fetch_proxies_from_proxyscrape
        ]
        
        for source_func in sources:
            try:
                new_proxies = source_func()
                proxies.update(new_proxies)
                logger.info(f"Found {len(new_proxies)} proxies from source {source_func.__name__}")
                
                if len(proxies) >= min_proxies:
                    break
            except Exception as e:
                logger.error(f"Error fetching from {source_func.__name__}: {e}")
        
        logger.info(f"Fetched total of {len(proxies)} unique proxies")
        return list(proxies)
    
    def _fetch_proxies_from_free_proxy_list(self):
        """Fetch proxies from free-proxy-list.net."""
        proxies = []
        try:
            response = requests.get("https://free-proxy-list.net/", timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'proxylisttable'})
            
            if not table:
                return proxies
                
            for row in table.tbody.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    ip = cells[0].text.strip()
                    port = cells[1].text.strip()
                    https = cells[6].text.strip()
                    
                    # Only use HTTPS proxies for secure connections
                    if https.lower() == 'yes':
                        proxy = f"{ip}:{port}"
                        proxies.append(proxy)
        except Exception as e:
            logger.error(f"Error fetching from free-proxy-list: {e}")
        
        return proxies
    
    def _fetch_proxies_from_geonode(self):
        """Fetch proxies from geonode.com."""
        proxies = []
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'data' in data:
                for proxy_data in data['data']:
                    ip = proxy_data.get('ip')
                    port = proxy_data.get('port')
                    if ip and port:
                        proxy = f"{ip}:{port}"
                        proxies.append(proxy)
        except Exception as e:
            logger.error(f"Error fetching from geonode: {e}")
        
        return proxies
    
    def _fetch_proxies_from_proxyscrape(self):
        """Fetch proxies from proxyscrape.com."""
        proxies = []
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    if ':' in line:
                        proxies.append(line.strip())
        except Exception as e:
            logger.error(f"Error fetching from proxyscrape: {e}")
        
        return proxies
    
    def verify_proxy(self, proxy, timeout=5):
        """
        Verify if a proxy is working by checking IP.
        
        Args:
            proxy: Proxy string (ip:port)
            timeout: Request timeout in seconds
        
        Returns:
            dict: Information about the proxy if working, None otherwise
        """
        logger.debug(f"Testing proxy: {proxy}")
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"  # Using http:// even for https connections
        }
        
        # Try different IP check services
        for url in self.ip_check_urls:
            try:
                start_time = time.time()
                response = requests.get(
                    url, 
                    proxies=proxy_dict, 
                    timeout=timeout,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                )
                
                if response.status_code == 200:
                    elapsed = time.time() - start_time
                    
                    # Get IP address and geolocation
                    if 'ipinfo.io' in url:
                        data = response.json()
                        ip = data.get('ip')
                        country = data.get('country', 'Unknown')
                        region = data.get('region', 'Unknown')
                        city = data.get('city', 'Unknown')
                        location = f"{city}, {region}, {country}"
                    else:
                        ip = response.text.strip()
                        # Get geolocation for IP
                        try:
                            geo_response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=timeout)
                            if geo_response.status_code == 200:
                                geo_data = geo_response.json()
                                country = geo_data.get('country', 'Unknown')
                                region = geo_data.get('region', 'Unknown')
                                city = geo_data.get('city', 'Unknown')
                                location = f"{city}, {region}, {country}"
                            else:
                                location = "Unknown"
                        except:
                            location = "Unknown"
                    
                    logger.debug(f"Proxy {proxy} is working. IP: {ip}, Location: {location}, Response time: {elapsed:.2f}s")
                    return {
                        "proxy": proxy,
                        "ip": ip,
                        "location": location,
                        "response_time": elapsed
                    }
                
            except Exception as e:
                logger.debug(f"Proxy test failed for {proxy} with {url}: {str(e)}")
        
        logger.debug(f"Proxy {proxy} failed all verification tests")
        return None
    
    def verify_proxies(self, proxy_list, max_workers=10):
        """
        Verify multiple proxies concurrently.
        
        Args:
            proxy_list: List of proxies to verify
            max_workers: Maximum number of concurrent workers
        
        Returns:
            list: List of verified proxy information
        """
        logger.info(f"Verifying {len(proxy_list)} proxies with {max_workers} workers")
        verified = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all verification tasks
            future_to_proxy = {
                executor.submit(self.verify_proxy, proxy): proxy 
                for proxy in proxy_list
            }
            
            # Process results as they complete
            for future in future_to_proxy:
                proxy_info = future.result()
                if proxy_info:
                    verified.append(proxy_info)
                    
                    # Report progress periodically
                    if len(verified) % 5 == 0:
                        logger.info(f"Verified {len(verified)} working proxies so far")
        
        logger.info(f"Completed verification. Found {len(verified)} working proxies")
        return verified
    
    def update_proxy_list(self, min_proxies=20):
        """
        Update the list of verified proxies.
        
        Args:
            min_proxies: Minimum number of proxies to maintain
        """
        # Skip update if we already have enough verified proxies
        if len(self.verified_proxies) >= min_proxies:
            logger.info(f"Already have {len(self.verified_proxies)} verified proxies, skipping update")
            return
            
        logger.info(f"Updating proxy list to reach minimum of {min_proxies} proxies")
        
        # Fetch new proxies
        new_proxies = self.fetch_free_proxies(min_proxies=min_proxies * 5)  # Fetch extra to account for failures
        
        # Filter out already verified or used proxies
        existing_proxy_strings = set(p.get("proxy") for p in self.verified_proxies)
        new_proxies = [p for p in new_proxies if p not in existing_proxy_strings and p not in self.used_proxies]
        
        if not new_proxies:
            logger.warning("No new proxies found to verify")
            return
            
        # Verify the new proxies
        verified_proxies = self.verify_proxies(new_proxies)
        
        # Add new verified proxies to our list
        self.verified_proxies.extend(verified_proxies)
        
        # Keep only the fastest proxies up to max_proxies
        if len(self.verified_proxies) > self.max_proxies:
            self.verified_proxies.sort(key=lambda x: x.get("response_time", 999))
            self.verified_proxies = self.verified_proxies[:self.max_proxies]
        
        # Save updated proxy list
        self._save_cache()
        
        logger.info(f"Proxy list updated. Now have {len(self.verified_proxies)} verified proxies")
    
    def get_proxy(self):
        """
        Get a working proxy from the list of verified proxies.
        
        Returns:
            dict: Proxy information if available, None otherwise
        """
        # Make sure we have proxies available
        if not self.verified_proxies:
            logger.info("No verified proxies available. Fetching new proxies.")
            self.update_proxy_list()
            
            if not self.verified_proxies:
                logger.error("Failed to find any working proxies")
                return None
        
        # Select a proxy from the verified list
        if self.verified_proxies:
            # Prioritize proxies not recently used
            available_proxies = [p for p in self.verified_proxies if p.get("proxy") not in self.used_proxies]
            
            # If all have been used, reset tracking and use all
            if not available_proxies:
                logger.info("All proxies have been used. Resetting tracking.")
                self.used_proxies.clear()
                available_proxies = self.verified_proxies
            
            # Choose a proxy - prefer faster ones with some randomness
            available_proxies.sort(key=lambda x: x.get("response_time", 999))
            # Take from the fastest 75%
            selection_pool = available_proxies[:max(1, int(len(available_proxies) * 0.75))]
            proxy_info = random.choice(selection_pool)
            
            # Mark as used and return
            proxy_string = proxy_info.get("proxy")
            self.used_proxies.add(proxy_string)
            
            logger.info(f"Selected proxy: {proxy_string}, Location: {proxy_info.get('location')}")
            return proxy_info
        
        return None


# Extend the existing HumanLikeVisitor class with IP rotation capabilities
class HumanLikeVisitorWithIPRotation(HumanLikeVisitor):
    """Extended visitor class with IP rotation capabilities."""
    
    def __init__(self, headless=False, use_proxies=True, use_tor=False, proxy_manager=None):
        """
        Initialize the visitor with IP rotation settings.
        
        Args:
            headless: Whether to run browser in headless mode
            use_proxies: Whether to use free proxies
            use_tor: Whether to use Tor network (not implemented yet)
            proxy_manager: Optional existing proxy manager instance
        """
        super().__init__(headless=headless)
        self.use_proxies = use_proxies
        self.use_tor = use_tor
        self.current_ip_info = None
        self.original_ip = None
        
        # Initialize proxy manager if we're using proxies
        if use_proxies:
            self.proxy_manager = proxy_manager if proxy_manager else ProxyManager()
        else:
            self.proxy_manager = None
            
        # Check our original IP
        self._check_original_ip()
        
    def _check_original_ip(self):
        """Check and record our original IP address without proxies."""
        try:
            for url in ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.original_ip = response.text.strip()
                        logger.info(f"Original IP address: {self.original_ip}")
                        break
                except:
                    continue
                    
            if not self.original_ip:
                logger.warning("Could not determine original IP address")
                self.original_ip = "unknown"
        except Exception as e:
            logger.error(f"Error checking original IP: {e}")
            self.original_ip = "unknown"
            
    def _verify_ip_changed(self, driver):
        """
        Verify that our IP address has changed in the browser.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if IP has changed, False otherwise
        """
        logger.info("Verifying IP address change...")
        changed = False
        
        try:
            # Try multiple IP check services
            ip_check_urls = [
                "https://api.ipify.org",
                "https://ifconfig.me/ip",
                "https://icanhazip.com"
            ]
            
            for url in ip_check_urls:
                try:
                    driver.get(url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Get the IP from the page
                    current_ip = driver.find_element(By.TAG_NAME, "body").text.strip()
                    logger.info(f"Current browser IP: {current_ip}")
                    
                    # Check if IP is different from our original IP
                    if current_ip and current_ip != self.original_ip:
                        logger.info(f"IP change verified: {self.original_ip} -> {current_ip}")
                        
                        # Optionally get geolocation info
                        try:
                            driver.get("https://ipinfo.io/json")
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, "pre"))
                            )
                            
                            geo_data = json.loads(driver.find_element(By.TAG_NAME, "pre").text)
                            location = f"{geo_data.get('city', 'Unknown')}, {geo_data.get('region', 'Unknown')}, {geo_data.get('country', 'Unknown')}"
                            logger.info(f"Current location: {location}")
                        except Exception as e:
                            logger.warning(f"Could not get geolocation info: {e}")
                            location = "Unknown"
                            
                        # Store current IP info
                        self.current_ip_info = {
                            "ip": current_ip,
                            "location": location
                        }
                        
                        changed = True
                        break
                except Exception as e:
                    logger.warning(f"Error checking IP with {url}: {e}")
                    continue
            
            if not changed:
                logger.warning("IP address has NOT changed!")
            
            return changed
                
        except Exception as e:
            logger.error(f"Error verifying IP change: {e}")
            return False
    
    def _setup_tor_proxy(self):
        """
        Set up Tor as a proxy (placeholder - would need actual Tor setup logic).
        
        Returns:
            str: Proxy string for Tor (e.g. "127.0.0.1:9050")
        """
        # This is a placeholder - in a real implementation you would:
        # 1. Check if Tor is installed
        # 2. Start the Tor service if needed
        # 3. Configure Tor for your needs
        # 4. Return the SOCKS proxy address
        
        logger.warning("Tor support not fully implemented - this is a placeholder")
        return "127.0.0.1:9050"  # Default Tor SOCKS proxy address
    
    def _create_driver_with_rotation(self):
        """
        Create a driver with IP rotation enabled.
        
        Returns:
            WebDriver: Configured Selenium WebDriver
        """
        proxy_string = None
        
        # Get proxy based on settings
        if self.use_proxies:
            logger.info("Setting up proxy rotation...")
            proxy_info = self.proxy_manager.get_proxy()
            
            if proxy_info:
                proxy_string = proxy_info.get("proxy")
                logger.info(f"Using proxy: {proxy_string}, Location: {proxy_info.get('location')}")
            else:
                logger.warning("No working proxy found. Will use direct connection.")
        
        elif self.use_tor:
            logger.info("Setting up Tor rotation...")
            proxy_string = self._setup_tor_proxy()
            logger.info(f"Using Tor proxy: {proxy_string}")
            
        # Update the proxy for this session
        self.proxy = proxy_string
        
        # Create the driver using the parent method (which will use the updated proxy)
        return self._create_driver()
    
    def visit_once(self):
        """
        Visit the website once with IP rotation.
        
        Returns:
            bool: True if visit was successful, False otherwise
        """
        # Create driver with IP rotation
        driver = self._create_driver_with_rotation()
        start_time = time.time()
        success = False
        
        try:
            # Verify IP has changed
            if not self._verify_ip_changed(driver):
                logger.warning("IP address did not change. Aborting this visit.")
                self.failed_visits += 1
                return False
            
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
            
            # Run the human-like session for 30 seconds
            self._simulate_user_session(driver, total_duration=30)
            
            # Success
            self.successful_visits += 1
            success = True
            return True
            
        except Exception as e:
            logger.error(f"Error during website visit: {e}")
            self.failed_visits += 1
            return False
            
        finally:
            # Calculate actual session time
            session_time = time.time() - start_time
            logger.info(f"Session completed in {session_time:.1f} seconds (success: {success})")
            
            # Always clean up
            try:
                driver.quit()
                logger.debug("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


# Main execution function
def main():
    """Main function to run the program."""
    parser = argparse.ArgumentParser(description="Visit website with human-like behavior and IP rotation")
    parser.add_argument("--count", type=int, default=1000, help="Number of visits to make")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--proxy-file", type=str, help="Path to proxy list file")
    parser.add_argument("--use-tor", action="store_true", help="Use Tor network for IP rotation")
    parser.add_argument("--use-proxies", action="store_true", help="Use free proxies for IP rotation")
    parser.add_argument("--min-proxies", type=int, default=20, help="Minimum number of proxies to maintain")
    
    args = parser.parse_args()
    
    # Set up logging to file and console
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    root_logger = logging.getLogger()
    
    # File handler
    file_handler = logging.FileHandler("website_visitor.log")
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    
    logger.info("Starting website visitor with IP rotation")
    
    # Initialize proxy manager if using proxies
    proxy_manager = None
    if args.use_proxies or args.proxy_file:
        proxy_manager = ProxyManager()
        
        # Update proxy list to ensure we have enough
        if args.proxy_file:
            # Load proxies from file
            logger.info(f"Loading proxies from file: {args.proxy_file}")
            proxies = []
            try:
                with open(args.proxy_file, 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(proxies)} proxies from file")
                
                # Verify these proxies
                verified = proxy_manager.verify_proxies(proxies)
                proxy_manager.verified_proxies = verified
                proxy_manager._save_cache()
            except Exception as e:
                logger.error(f"Error loading proxy file: {e}")
        else:
            # Fetch and verify proxies
            logger.info("Fetching and verifying proxies...")
            proxy_manager.update_proxy_list(min_proxies=args.min_proxies)
    
    # Create visitor with IP rotation
    visitor = HumanLikeVisitorWithIPRotation(
        headless=args.headless,
        use_proxies=args.use_proxies or args.proxy_file is not None,
        use_tor=args.use_tor,
        proxy_manager=proxy_manager
    )
    
    # Run the visits
    logger.info(f"Starting {args.count} visits with IP rotation")
    
    for i in range(args.count):
        try:
            current_time = time.strftime("%H:%M:%S")
            logger.info(f"Visit {i+1}/{args.count} at {current_time}")
            
            success = visitor.visit_once()
            
            # Add a random delay between visits (3-10 seconds)
            if i < args.count - 1:  # Skip delay after last visit
                delay = random.uniform(3, 10)
                logger.info(f"Waiting {delay:.2f} seconds before next visit")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Error in visit iteration {i+1}: {e}")
            visitor.failed_visits += 1
    
    # Print stats
    logger.info(f"All visits completed. Success: {visitor.successful_visits}, Failed: {visitor.failed_visits}")


if __name__ == "__main__":
    main()