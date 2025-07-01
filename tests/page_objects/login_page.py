"""
Page Object para la página de login
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class LoginPage(BasePage):
    """Página de inicio de sesión"""
    
    # Localizadores
    USERNAME_INPUT = (By.ID, "usuario")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    TOGGLE_PASSWORD = (By.ID, "togglePassword")
    ERROR_MESSAGES = (By.CSS_SELECTOR, ".text-red-600")
    HOME_LINK = (By.CSS_SELECTOR, "a[href='/']")
    
    # Campos del formulario
    TITLE = (By.TAG_NAME, "h2")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "/login/"
    
    def login(self, username, password):
        """Realizar login"""
        if not self.send_keys_to_element(self.USERNAME_INPUT, username):
            return False
        
        if not self.send_keys_to_element(self.PASSWORD_INPUT, password):
            return False
        
        return self.click_element(self.LOGIN_BUTTON)
    
    def toggle_password_visibility(self):
        """Alternar visibilidad de la contraseña"""
        return self.click_element(self.TOGGLE_PASSWORD)
    
    def get_error_messages(self):
        """Obtener mensajes de error"""
        try:
            error_elements = self.driver.find_elements(*self.ERROR_MESSAGES)
            return [element.text for element in error_elements]
        except:
            return []
    
    def has_error_message(self):
        """Verificar si hay mensajes de error"""
        return len(self.get_error_messages()) > 0
    
    def go_to_home(self):
        """Ir a la página principal"""
        return self.click_element(self.HOME_LINK)
    
    def is_login_form_visible(self):
        """Verificar si el formulario de login es visible"""
        return (self.is_element_visible(self.USERNAME_INPUT) and 
                self.is_element_visible(self.PASSWORD_INPUT) and 
                self.is_element_visible(self.LOGIN_BUTTON))
