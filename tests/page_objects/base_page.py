"""
Clase base para Page Objects
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BasePage:
    """Clase base para todos los Page Objects"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.url = ""
    
    def navigate(self, base_url="http://localhost:8000"):
        """Navegar a la página"""
        full_url = f"{base_url}{self.url}"
        self.driver.get(full_url)
        return self
    
    def wait_for_element(self, locator, timeout=10):
        """Esperar a que un elemento esté presente"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            return None
    
    def wait_for_clickable(self, locator, timeout=10):
        """Esperar a que un elemento sea clickeable"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            return None
    
    def wait_for_visible(self, locator, timeout=10):
        """Esperar a que un elemento sea visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            return None
    
    def click_element(self, locator, timeout=10):
        """Hacer click en un elemento"""
        element = self.wait_for_clickable(locator, timeout)
        if element:
            try:
                element.click()
                return True
            except Exception:
                # Si falla el click normal, usar JavaScript
                self.driver.execute_script("arguments[0].click();", element)
                return True
        return False
    
    def send_keys_to_element(self, locator, text, timeout=10):
        """Enviar texto a un elemento"""
        element = self.wait_for_element(locator, timeout)
        if element:
            element.clear()
            element.send_keys(text)
            return True
        return False
    
    def get_element_text(self, locator, timeout=10):
        """Obtener el texto de un elemento"""
        element = self.wait_for_element(locator, timeout)
        return element.text if element else ""
    
    def is_element_present(self, locator):
        """Verificar si un elemento está presente"""
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False
    
    def is_element_visible(self, locator, timeout=5):
        """Verificar si un elemento es visible"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False
    
    def get_current_url(self):
        """Obtener la URL actual"""
        return self.driver.current_url
    
    def get_page_title(self):
        """Obtener el título de la página"""
        return self.driver.title
    
    def scroll_to_element(self, locator):
        """Hacer scroll hasta un elemento"""
        element = self.wait_for_element(locator)
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            return True
        return False
