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
            if time.time() - start_time + final_scroll_time <= total_duration:
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


def main():
    """Parse command line arguments and run the visitor."""
    parser = argparse.ArgumentParser(description="Human-Like Hiyath Website Visitor")
    
    parser.add_argument("--count", type=int, default=1000, 
                        help="Number of website visits (default: 1000)")
    parser.add_argument("--headless", action="store_true", 
                        help="Run in headless mode (invisible)")
    parser.add_argument("--proxy-file", type=str, 
                        help="Path to file containing proxies (one per line)")
    parser.add_argument("--demo", action="store_true", 
                        help="Run in demo mode with just 3 visits")
    
    args = parser.parse_args()
    
    # Apply demo mode if selected
    if args.demo:
        args.count = 3
        logger.info("Running in demo mode with just 3 visits")
    
    # Create visitor - Default is visible mode (headless=False)
    visitor = HumanLikeVisitor(headless=args.headless)
    
    # Run with or without proxy file
    if args.proxy_file:
        visitor.run_with_proxy_file(count=args.count, proxy_file=args.proxy_file)
    else:
        visitor.run_visits(count=args.count)


if __name__ == "__main__":
    main()