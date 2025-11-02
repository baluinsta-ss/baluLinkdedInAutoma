import os
import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from dotenv import load_dotenv
import time
import random

load_dotenv()

class LinkedInService:
    def __init__(self):
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = None

    def _human_delay(self, min_sec=1, max_sec=3):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(min_sec, max_sec))

    def _human_type(self, element, text):
        """Type text character by character with random delays to mimic human typing"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))  # Random delay between keystrokes

    def _scroll_randomly(self):
        """Scroll page randomly to mimic human browsing"""
        scroll_amount = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self._human_delay(0.5, 1.5)

    def _move_mouse_to_element(self, element):
        """Move mouse to element before clicking (human-like)"""
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        self._human_delay(0.3, 0.8)

    def _init_driver(self):
        """Initialize undetected chromedriver with Chrome 141 compatibility"""
        if self.driver is None:
            st.write("🔧 Initializing Chrome browser (version 141)...")
            
            options = uc.ChromeOptions()
            
            # Anti-detection options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--start-maximized")
            
            # Set a realistic user agent
            options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
            
            try:
                self.driver = uc.Chrome(
                    options=options,
                    use_subprocess=True,
                    version_main=141
                )
                st.write("✅ Browser initialized successfully.")
            except Exception as e:
                st.error(f"Failed to initialize browser: {e}")
                raise

    def _login(self) -> bool:
        """Login to LinkedIn with human-like behavior"""
        if not self.email or not self.password:
            st.error("❌ LINKEDIN_EMAIL and LINKEDIN_PASSWORD not set in .env!")
            return False

        self._init_driver()
        
        # Check if already logged in
        self.driver.get("https://www.linkedin.com/feed/")
        self._human_delay(3, 5)
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "global-nav-search"))
            )
            st.success("✅ Already logged in!")
            
            # Mimic human browsing after login
            self._scroll_randomly()
            self._human_delay(2, 4)
            
            return True
        except:
            st.write("🔐 Not logged in. Proceeding to login page...")

        # Perform login with human-like behavior
        try:
            self.driver.get("https://www.linkedin.com/login")
            self._human_delay(2, 4)
            
            # Enter email with human typing
            email_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.click()
            self._human_delay(0.5, 1)
            self._human_type(email_field, self.email)
            st.write("📧 Email entered")
            self._human_delay(1, 2)

            # Enter password with human typing
            password_field = self.driver.find_element(By.ID, "password")
            password_field.click()
            self._human_delay(0.5, 1)
            self._human_type(password_field, self.password)
            st.write("🔑 Password entered")
            self._human_delay(1, 2)
            
            # Submit
            password_field.send_keys(Keys.RETURN)
            st.write("🔐 Logging in...")

            # Wait for login with CAPTCHA support
            st.info("⏳ Waiting for login... (Solve CAPTCHA manually if it appears)")
            
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "global-nav-search"))
            )
            st.success("✅ Login successful!")
            
            # Important: Browse like a human after login
            self._human_delay(3, 5)
            self._scroll_randomly()
            self._scroll_randomly()
            self._human_delay(2, 4)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Login failed: {e}")
            self._save_screenshot("linkedin_login_error.png")
            self.quit_driver()
            return False

    def create_post(self, content: str, image_url: str = None) -> str:
        """Create a LinkedIn post with maximum human-like behavior"""
        if not self._login():
            return "Login failed"

        try:
            # Navigate to feed
            self.driver.get("https://www.linkedin.com/feed/")
            self._human_delay(4, 6)
            
            # Scroll and browse like a human BEFORE posting
            st.write("👀 Browsing feed like a human...")
            self._scroll_randomly()
            self._human_delay(2, 3)
            self._scroll_randomly()
            self._human_delay(2, 3)
            
            # Scroll to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            self._human_delay(2, 3)

            # Find "Start a post" button
            st.write("🔍 Looking for 'Start a post' button...")
            
            start_post_btn = None
            selectors = [
                (By.CSS_SELECTOR, "button.share-box-feed-entry__trigger"),
                (By.XPATH, "//button[contains(@class, 'share-box-feed-entry__trigger')]"),
                (By.XPATH, "//button[contains(., 'Start a post')]")
            ]
            
            for selector_type, selector_value in selectors:
                try:
                    start_post_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((selector_type, selector_value))
                    )
                    st.write(f"✅ Found button")
                    break
                except TimeoutException:
                    continue
            
            if not start_post_btn:
                raise Exception("Could not find 'Start a post' button")
            
            # Move mouse to button and click (human-like)
            self._move_mouse_to_element(start_post_btn)
            self._human_delay(0.5, 1)
            
            try:
                start_post_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", start_post_btn)
            
            st.write("✅ Opened post editor")
            self._human_delay(3, 5)  # Wait for modal to fully load

            # Find and enter content with HUMAN TYPING
            st.write("✍️ Typing post content...")
            
            editor = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor"))
            )
            
            # Click editor and wait
            editor.click()
            self._human_delay(1, 2)
            
            # Type content character by character (CRUCIAL for avoiding detection)
            self._human_type(editor, content)
            
            st.write("✅ Content entered")
            self._human_delay(3, 5)  # Pause before posting

            # Upload image if provided
            if image_url and os.path.exists(image_url):
                st.write("📸 Uploading image...")
                try:
                    self._upload_image(image_url)
                except Exception as img_error:
                    st.warning(f"⚠️ Image upload failed: {img_error}. Posting without image...")

            # Click the "Post" button
            st.write("📤 Publishing post...")
            
            post_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.share-actions__primary-action"))
            )
            
            # Move mouse to Post button (human-like)
            self._move_mouse_to_element(post_btn)
            self._human_delay(1, 2)
            
            try:
                post_btn.click()
            except:
                self.driver.execute_script("arguments[0].click();", post_btn)
            
            st.write("✅ Post button clicked")
            self._human_delay(10, 15)  # Wait for post to complete
            
            # Check if post was successful or saved as draft
            try:
                # Look for draft notification
                draft_msg = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'draft')]")
                if draft_msg:
                    st.warning("⚠️ LinkedIn saved the post as draft. This may be due to anti-automation detection.")
                    st.info("💡 Try posting manually from your drafts: https://www.linkedin.com/post/new/drafts")
                    return "Post saved as draft - manual action required"
            except:
                pass
            
            st.success("✅ Post published successfully!")
            return "https://www.linkedin.com/feed/"

        except Exception as e:
            st.error(f"❌ Posting failed: {e}")
            self._save_screenshot("linkedin_post_error.png")
            return f"Posting failed - {e}"

    def _upload_image(self, image_path: str):
        """Upload image with human-like delays"""
        media_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Add media']"))
        )
        self._move_mouse_to_element(media_btn)
        media_btn.click()
        self._human_delay(2, 3)

        file_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        file_input.send_keys(os.path.abspath(image_path))
        st.write("✅ Image uploaded")
        self._human_delay(5, 7)

        try:
            done_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Done')]"))
            )
            self._move_mouse_to_element(done_btn)
            done_btn.click()
            self._human_delay(2, 3)
        except:
            pass

    def _save_screenshot(self, filename: str):
        """Save screenshot"""
        try:
            self.driver.save_screenshot(filename)
            st.image(filename, caption="Error Screenshot", use_column_width=True)
        except:
            st.warning("Could not save screenshot")

    def quit_driver(self):
        """Close browser"""
        if self.driver:
            st.write("🔒 Closing browser...")
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None





    def create_post_with_pdf(self, content: str, pdf_path: str) -> str:
        """Create a LinkedIn post with PDF document attachment"""
        if not self._login():
            return "Login failed"
        
        try:
            # Navigate to feed
            self.driver.get("https://www.linkedin.com/feed/")
            self._human_delay(4, 6)
            
            # Scroll and browse like a human
            st.write("👀 Browsing feed...")
            self._scroll_randomly()
            self._human_delay(2, 3)
            
            # Open post editor
            st.write("🔍 Opening post editor...")
            start_post_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.share-box-feed-entry__trigger"))
            )
            self._move_mouse_to_element(start_post_btn)
            self._human_delay(0.5, 1)
            start_post_btn.click()
            st.write("✅ Opened post editor")
            self._human_delay(3, 5)
            
            # Enter content
            st.write("✍️ Typing post content...")
            editor = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor"))
            )
            editor.click()
            self._human_delay(1, 2)
            self._human_type(editor, content)
            st.write("✅ Content entered")
            self._human_delay(2, 3)
            
            # Upload PDF document
            if pdf_path and os.path.exists(pdf_path):
                st.write("📄 Uploading PDF document...")
                try:
                    # Click "Add document" button
                    doc_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Add a document']"))
                    )
                    self._move_mouse_to_element(doc_btn)
                    doc_btn.click()
                    self._human_delay(2, 3)
                    
                    # Upload file
                    file_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                    )
                    file_input.send_keys(os.path.abspath(pdf_path))
                    st.write("✅ PDF uploaded")
                    self._human_delay(5, 8)  # Wait for upload to complete
                    
                    # Click "Done" if modal appears
                    try:
                        done_btn = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Done')]"))
                        )
                        self._move_mouse_to_element(done_btn)
                        done_btn.click()
                        self._human_delay(2, 3)
                    except:
                        pass
                        
                except Exception as pdf_error:
                    st.warning(f"⚠️ PDF upload failed: {pdf_error}. Posting without document...")
            
            # Publish post
            st.write("📤 Publishing post...")
            post_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.share-actions__primary-action"))
            )
            self._move_mouse_to_element(post_btn)
            self._human_delay(1, 2)
            post_btn.click()
            st.write("✅ Post button clicked")
            self._human_delay(10, 15)
            
            st.success("✅ Post with PDF published successfully!")
            return "https://www.linkedin.com/feed/"
            
        except Exception as e:
            st.error(f"❌ Posting failed: {e}")
            self._save_screenshot("linkedin_pdf_post_error.png")
            return f"Posting failed - {e}"
