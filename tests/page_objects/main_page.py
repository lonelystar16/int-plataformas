"""
Page Object para la página principal
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class MainPage(BasePage):
    """Página principal de FerramasStore"""
    
    # Localizadores
    LOGO = (By.CSS_SELECTOR, "img[alt*='FERREMA']")
    TITLE = (By.TAG_NAME, "h1")
    
    # Enlaces de categorías
    HERRAMIENTAS_MANUALES = (By.CSS_SELECTOR, "a[href*='herra-manuales']")
    MATERIALES_BASICOS = (By.CSS_SELECTOR, "a[href*='materiales-basicos']")
    EQUIPOS_SEGURIDAD = (By.CSS_SELECTOR, "a[href*='equipos-seguridad']")
    TORNILLOS_ANCLAJES = (By.CSS_SELECTOR, "a[href*='tornillos-anclaje']")
    FIJACIONES = (By.CSS_SELECTOR, "a[href*='fijaciones']")
    EQUIPOS_MEDICION = (By.CSS_SELECTOR, "a[href*='equipos-medicion']")
    
    # Botones de autenticación
    LOGIN_BUTTON = (By.CSS_SELECTOR, "a[href*='login']")
    REGISTER_BUTTON = (By.CSS_SELECTOR, "a[href*='register']")
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "a[href*='logout']")
    
    # Elementos de usuario autenticado
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "p:contains('¡Hola')")
    
    # Popup de suscripción
    SUBSCRIPTION_POPUP = (By.ID, "subscription-popup")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "/"
    
    def navigate_to_category(self, category):
        """Navegar a una categoría específica"""
        category_map = {
            'herramientas': self.HERRAMIENTAS_MANUALES,
            'materiales': self.MATERIALES_BASICOS,
            'seguridad': self.EQUIPOS_SEGURIDAD,
            'tornillos': self.TORNILLOS_ANCLAJES,
            'fijaciones': self.FIJACIONES,
            'medicion': self.EQUIPOS_MEDICION
        }
        
        if category in category_map:
            return self.click_element(category_map[category])
        return False
    
    def is_user_logged_in(self):
        """Verificar si el usuario está logueado"""
        return self.is_element_present(self.WELCOME_MESSAGE)
    
    def click_login(self):
        """Hacer click en el botón de login"""
        return self.click_element(self.LOGIN_BUTTON)
    
    def click_register(self):
        """Hacer click en el botón de registro"""
        return self.click_element(self.REGISTER_BUTTON)
    
    def click_logout(self):
        """Hacer click en el botón de logout"""
        return self.click_element(self.LOGOUT_BUTTON)
    
    def get_page_title(self):
        """Obtener el título de la página"""
        title_element = self.wait_for_element(self.TITLE)
        return title_element.text if title_element else ""
    
    def is_logo_present(self):
        """Verificar si el logo está presente"""
        return self.is_element_present(self.LOGO)
