"""
Page Object para el carrito de compras
"""
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage


class ShoppingCartPage(BasePage):
    """Componente del carrito de compras"""
    
    # Localizadores del carrito
    CART_BUTTON = (By.ID, "cart-btn")
    CART_COUNT = (By.ID, "cart-count")
    CART_SUMMARY = (By.ID, "cart-summary")
    CART_ITEMS = (By.ID, "cart-items")
    CART_TOTAL = (By.ID, "cart-total")
    CLEAR_CART_BUTTON = (By.CSS_SELECTOR, "button[onclick*='clearCart']")
    CHECKOUT_BUTTON = (By.CSS_SELECTOR, "button[onclick*='checkout'], a[href*='checkout']")
    CLOSE_CART_BUTTON = (By.CSS_SELECTOR, "button[onclick*='closeCart']")
    
    # Botones de productos
    ADD_TO_CART_BUTTONS = (By.CLASS_NAME, "add-to-cart-btn")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def open_cart(self):
        """Abrir el carrito"""
        try:
            cart_button = self.wait_for_element(self.CART_BUTTON, timeout=5)
            if cart_button:
                cart_button.click()
                time.sleep(0.5)  # Esperar animación
                return True
        except Exception as e:
            print(f"⚠️ No se pudo abrir carrito: {e}")
        return False
    
    def close_cart(self):
        """Cerrar el carrito"""
        try:
            close_button = self.wait_for_element(self.CLOSE_CART_BUTTON, timeout=2)
            if close_button:
                close_button.click()
                time.sleep(0.5)
                return True
        except:
            # Intentar cerrar haciendo click fuera del carrito
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(0.5)
                return True
            except:
                pass
        return False
    
    def get_cart_count(self):
        """Obtener el número de items en el carrito"""
        try:
            count_element = self.wait_for_element(self.CART_COUNT, timeout=5)
            if count_element:
                count_text = count_element.text.strip()
                if count_text.isdigit():
                    return int(count_text)
                elif count_text == '':
                    return 0
            
            # Si no hay elemento visible o no tiene texto, verificar localStorage
            try:
                cart_data = self.driver.execute_script("return localStorage.getItem('cart');")
                if cart_data:
                    cart = json.loads(cart_data)
                    return sum(item.get('cantidad', 0) for item in cart.values() if isinstance(item, dict))
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Error obteniendo contador del carrito: {e}")
            
        return 0
    
    def get_cart_total(self):
        """Obtener el total del carrito"""
        try:
            if self.open_cart():
                total_element = self.wait_for_element(self.CART_TOTAL, timeout=3)
                if total_element:
                    # Extraer el número del texto (ej: "$1000" -> 1000)
                    total_text = total_element.text.replace('$', '').replace(',', '').strip()
                    if total_text and total_text.replace('.', '').isdigit():
                        return float(total_text)
                
                # Si no hay elemento visible, verificar localStorage
                try:
                    cart_data = self.driver.execute_script("return localStorage.getItem('cart');")
                    if cart_data:
                        cart = json.loads(cart_data)
                        total = 0
                        for item in cart.values():
                            if isinstance(item, dict):
                                precio = item.get('precio', 0)
                                cantidad = item.get('cantidad', 0)
                                total += precio * cantidad
                        return total
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Error obteniendo total del carrito: {e}")
            
        return 0.0
    
    def add_first_product_to_cart(self):
        """Agregar el primer producto disponible al carrito"""
        try:
            # Buscar botones de agregar al carrito que no estén deshabilitados
            add_buttons = self.driver.find_elements(*self.ADD_TO_CART_BUTTONS)
            
            for button in add_buttons:
                try:
                    # Verificar que el botón esté visible y habilitado
                    if button.is_displayed() and button.is_enabled():
                        # Scroll hacia el elemento para asegurar que sea clickeable
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        
                        # Hacer click
                        button.click()
                        time.sleep(1)  # Esperar a que se procese
                        print(f"✅ Producto agregado al carrito exitosamente")
                        return True
                        
                except Exception as e:
                    print(f"⚠️ Error con botón: {e}")
                    continue
                    
            print("⚠️ No se encontraron botones de agregar al carrito habilitados")
            
        except Exception as e:
            print(f"⚠️ Error agregando producto al carrito: {e}")
            
        return False
    
    def clear_cart(self):
        """Vaciar el carrito"""
        try:
            if self.open_cart():
                clear_button = self.wait_for_element(self.CLEAR_CART_BUTTON, timeout=3)
                if clear_button:
                    clear_button.click()
                    time.sleep(1)  # Esperar confirmación
                    return True
        except Exception as e:
            print(f"⚠️ Error vaciando carrito: {e}")
        return False
    
    def proceed_to_checkout(self):
        """Proceder al checkout"""
        try:
            if self.open_cart():
                checkout_button = self.wait_for_element(self.CHECKOUT_BUTTON, timeout=3)
                if checkout_button:
                    checkout_button.click()
                    time.sleep(1)
                    return True
        except Exception as e:
            print(f"⚠️ Error procediendo al checkout: {e}")
        return False
    
    def is_cart_empty(self):
        """Verificar si el carrito está vacío"""
        return self.get_cart_count() == 0
    
    def is_cart_visible(self):
        """Verificar si el carrito está visible"""
        try:
            summary = self.wait_for_element(self.CART_SUMMARY, timeout=2)
            if summary:
                # Verificar si el carrito tiene las clases que indican que está visible
                classes = summary.get_attribute("class")
                return "hidden" not in classes and "opacity-0" not in classes
        except:
            pass
        return False
    
    def get_cart_items(self):
        """Obtener lista de items en el carrito"""
        try:
            if self.open_cart():
                items_container = self.wait_for_element(self.CART_ITEMS, timeout=3)
                if items_container:
                    items = items_container.find_elements(By.TAG_NAME, "li")
                    return [item.text for item in items if item.text.strip()]
        except Exception as e:
            print(f"⚠️ Error obteniendo items del carrito: {e}")
        return []
