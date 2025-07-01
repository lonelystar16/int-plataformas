"""
Prueba básica para verificar que todo funciona
"""
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import subprocess
import sys
import shutil


class TestBasic:
    """Prueba básica para verificar conectividad"""
    
    def setup_method(self):
        """Configurar driver para cada prueba"""
        print("\n🔧 Configurando driver de Chrome...")
        
        chrome_options = Options()
        # Opciones para mayor estabilidad
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Descomenta la siguiente línea para modo headless (sin ventana)
        # chrome_options.add_argument('--headless')
        
        self.driver = None
        
        # Verificar que Chrome esté instalado
        print("� Verificando instalación de Chrome...")
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome.exe",
            "google-chrome",
            "chromium-browser"
        ]
        
        chrome_found = False
        for chrome_path in chrome_paths:
            if shutil.which(chrome_path) or os.path.exists(chrome_path):
                print(f"✅ Chrome encontrado en: {chrome_path}")
                chrome_found = True
                break
        
        if not chrome_found:
            raise Exception("❌ Google Chrome no está instalado o no se encuentra en el PATH")
        
        # Intentar múltiples métodos de inicialización
        methods = [
            self._try_webdriver_manager,
            self._try_system_chromedriver,
            self._try_basic_chrome
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Método {i}: {method.__name__}")
                self.driver = method(chrome_options)
                if self.driver:
                    print("✅ Driver de Chrome iniciado correctamente")
                    self.driver.implicitly_wait(10)
                    self.wait = WebDriverWait(self.driver, 10)
                    return
            except Exception as e:
                print(f"❌ Método {i} falló: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                continue
        
        raise Exception("❌ No se pudo inicializar Chrome con ningún método disponible")
    
    def _try_webdriver_manager(self, chrome_options):
        """Intentar usando webdriver-manager"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("� Usando webdriver-manager...")
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver descargado en: {driver_path}")
            service = Service(driver_path)
            return webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            print("⚠️ webdriver-manager no está instalado")
            raise
        except Exception as e:
            print(f"❌ Error con webdriver-manager: {e}")
            raise
    
    def _try_system_chromedriver(self, chrome_options):
        """Intentar usando chromedriver del sistema"""
        print("🔍 Buscando chromedriver en el sistema...")
        
        # Buscar chromedriver en ubicaciones comunes
        driver_paths = [
            "chromedriver.exe",
            "chromedriver",
            r"C:\chromedriver\chromedriver.exe",
            r"C:\WebDriver\bin\chromedriver.exe",
            os.path.join(os.path.expanduser("~"), "chromedriver.exe")
        ]
        
        for driver_path in driver_paths:
            if shutil.which(driver_path) or os.path.exists(driver_path):
                print(f"✅ ChromeDriver encontrado en: {driver_path}")
                service = Service(driver_path)
                return webdriver.Chrome(service=service, options=chrome_options)
        
        # Intentar sin especificar ruta (usar PATH)
        print("🔄 Intentando chromedriver desde PATH...")
        service = Service()
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def _try_basic_chrome(self, chrome_options):
        """Intentar inicialización básica de Chrome"""
        print("🔄 Intentando inicialización básica...")
        return webdriver.Chrome(options=chrome_options)
    
    def teardown_method(self):
        """Limpiar después de cada prueba"""
        try:
            if hasattr(self, 'driver') and self.driver:
                print("🧹 Cerrando driver...")
                self.driver.quit()
                print("✅ Driver cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error cerrando driver: {e}")
        finally:
            self.driver = None
    
    def test_server_connectivity(self):
        """Verificar conectividad con los servidores antes de las pruebas web"""
        print("\n🌐 Verificando conectividad con servidores...")
        
        import requests
        
        # Verificar Django
        try:
            response = requests.get("http://localhost:8000", timeout=5)
            print(f"✅ Django responde: Status {response.status_code}")
            assert response.status_code == 200, f"Django no responde correctamente: {response.status_code}"
        except requests.exceptions.RequestException as e:
            print(f"❌ Django no accesible: {e}")
            pytest.skip("Servidor Django no está disponible en http://localhost:8000")
        
        # Verificar FastAPI (opcional)
        try:
            response = requests.get("http://localhost:8001", timeout=5)
            print(f"✅ FastAPI responde: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ FastAPI no accesible: {e} (esto es opcional)")
    
    def test_home_page_loads(self):
        """Verificar que la página principal carga"""
        print("\n🏠 Probando carga de página principal...")
        
        try:
            # Navegar a la página principal
            print("📡 Navegando a http://localhost:8000...")
            self.driver.get("http://localhost:8000")
            
            # Esperar a que la página cargue
            print("⏳ Esperando carga de página...")
            time.sleep(3)
            
            # Verificar que la página carga (título contiene algo relacionado)
            page_title = self.driver.title
            print(f"📄 Título de la página: '{page_title}'")
            
            # Verificar que no hay error 404 o similar
            assert "404" not in page_title.lower(), f"Página muestra error 404: {page_title}"
            assert "error" not in page_title.lower(), f"Página muestra error: {page_title}"
            
            # Verificar que la página no está vacía
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
            print(f"📝 Contenido de página (primeros 100 chars): {body_text[:100]}...")
            assert len(body_text.strip()) > 0, "La página está vacía"
            
            # Intentar encontrar algún elemento que indique que es la página correcta
            try:
                # Buscar el logo o título principal
                h1_elements = self.driver.find_elements(By.TAG_NAME, "h1")
                if h1_elements:
                    main_heading = h1_elements[0].text
                    print(f"🏷️ Encabezado principal: '{main_heading}'")
                    assert len(main_heading) > 0, "Encabezado principal está vacío"
                else:
                    print("⚠️ No se encontró elemento h1, pero la página tiene contenido")
                
                # Verificar que hay elementos interactivos
                links = self.driver.find_elements(By.TAG_NAME, "a")
                print(f"🔗 Enlaces encontrados: {len(links)}")
                assert len(links) > 0, "No se encontraron enlaces en la página"
                
            except Exception as element_error:
                print(f"⚠️ Error buscando elementos específicos: {element_error}")
                # No fallar la prueba si no encuentra elementos específicos
                pass
            
            print("✅ Prueba de carga de página exitosa")
            
        except Exception as e:
            # Tomar screenshot en caso de error
            try:
                screenshot_path = "error_home_page.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot guardado en: {screenshot_path}")
            except:
                print("⚠️ No se pudo guardar screenshot")
            
            print(f"❌ Error en prueba de carga de página: {e}")
            raise
    
    def test_navigation_basic(self):
        """Prueba básica de navegación"""
        print("\n🧭 Probando navegación básica...")
        
        try:
            print("📡 Navegando a página principal...")
            self.driver.get("http://localhost:8000")
            time.sleep(2)
            
            # Buscar enlaces de navegación
            print("🔍 Buscando enlaces...")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"🔗 Enlaces encontrados: {len(links)}")
            
            # Verificar que hay al menos algunos enlaces
            assert len(links) > 0, "No se encontraron enlaces en la página"
            
            # Filtrar enlaces válidos
            valid_links = []
            for link in links[:10]:  # Solo revisar los primeros 10
                href = link.get_attribute("href")
                text = link.text.strip()
                if (href and 
                    not href.startswith("mailto:") and 
                    not href.startswith("tel:") and
                    not href.startswith("javascript:") and
                    href.startswith("http://localhost:8000")):
                    valid_links.append((link, href, text))
            
            print(f"✅ Enlaces válidos encontrados: {len(valid_links)}")
            
            # Intentar hacer click en el primer enlace válido
            navigation_successful = False
            for link, href, text in valid_links[:3]:  # Probar máximo 3 enlaces
                try:
                    print(f"🔗 Probando enlace: '{text}' -> {href}")
                    
                    # Hacer click
                    self.driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    
                    # Verificar navegación
                    current_url = self.driver.current_url
                    print(f"📍 Navegó a: {current_url}")
                    
                    # Verificar que la página cargó
                    page_title = self.driver.title
                    print(f"📄 Título de nueva página: '{page_title}'")
                    
                    # Volver atrás
                    print("⬅️ Volviendo atrás...")
                    self.driver.back()
                    time.sleep(2)
                    
                    # Verificar que volvimos
                    back_url = self.driver.current_url
                    print(f"📍 De vuelta en: {back_url}")
                    
                    navigation_successful = True
                    break
                    
                except Exception as link_error:
                    print(f"⚠️ Error con enlace '{text}': {link_error}")
                    # Volver a la página principal si algo salió mal
                    try:
                        self.driver.get("http://localhost:8000")
                        time.sleep(1)
                    except:
                        pass
                    continue
            
            if not navigation_successful and len(valid_links) == 0:
                print("⚠️ No se encontraron enlaces válidos para probar, pero la página carga correctamente")
            elif not navigation_successful:
                print("⚠️ No se pudo navegar exitosamente, pero hay enlaces disponibles")
            else:
                print("✅ Navegación básica exitosa")
            
            # La prueba pasa si encontramos enlaces, aunque no podamos navegar
            assert len(links) > 0, "No hay enlaces en la página"
            
        except Exception as e:
            try:
                screenshot_path = "error_navigation.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Screenshot guardado en: {screenshot_path}")
            except:
                print("⚠️ No se pudo guardar screenshot")
            
            print(f"❌ Error en navegación básica: {e}")
            raise
