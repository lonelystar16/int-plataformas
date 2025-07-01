"""
Funciones auxiliares para las pruebas
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import random
import string


class TestHelpers:
    """Clase con métodos auxiliares para las pruebas"""
    
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
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
    
    def safe_click(self, locator, timeout=10):
        """Hacer click de forma segura"""
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
    
    def safe_send_keys(self, locator, text, timeout=10):
        """Enviar texto de forma segura"""
        element = self.wait_for_element(locator, timeout)
        if element:
            element.clear()
            element.send_keys(text)
            return True
        return False
    
    def scroll_to_element(self, element):
        """Hacer scroll hasta el elemento"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
    
    def get_cart_count(self):
        """Obtener el contador del carrito"""
        try:
            cart_count = self.driver.find_element(By.ID, "cart-count")
            return int(cart_count.text) if cart_count.text.isdigit() else 0
        except:
            return 0
    
    def generate_random_email(self):
        """Generar email aleatorio para pruebas"""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test_{random_string}@test.com"
    
    def generate_random_username(self):
        """Generar nombre de usuario aleatorio"""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"user_{random_string}"
    
    def take_screenshot(self, name):
        """Tomar captura de pantalla"""
        timestamp = int(time.time())
        filename = f"screenshot_{name}_{timestamp}.png"
        self.driver.save_screenshot(f"tests/screenshots/{filename}")
        return filename
    
    def wait_for_page_load(self, timeout=10):
        """Esperar a que la página cargue completamente"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False
    
    def hover_over_element(self, locator):
        """Pasar el mouse sobre un elemento"""
        element = self.wait_for_element(locator)
        if element:
            ActionChains(self.driver).move_to_element(element).perform()
            return True
        return False
    
    def is_element_present(self, locator):
        """Verificar si un elemento está presente"""
        try:
            self.driver.find_element(*locator)
            return True
        except:
            return False
    
    def get_current_url(self):
        """Obtener URL actual"""
        return self.driver.current_url
    
    def get_page_title(self):
        """Obtener título de la página"""
        return self.driver.title
