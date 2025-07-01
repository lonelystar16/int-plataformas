"""
Configuración base para las pruebas de Selenium
"""
import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import pytest


class TestConfig:
    """Configuración para las pruebas"""
    BASE_URL = os.getenv('TEST_BASE_URL', 'http://localhost:8000')
    API_URL = os.getenv('TEST_API_URL', 'http://localhost:8001')
    TIMEOUT = 10
    IMPLICIT_WAIT = 5
    
    # Credenciales de prueba
    TEST_SUPERUSER = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    TEST_USER = {
        'nombre': 'Usuario Test',
        'usuario': 'testuser',
        'correo': 'test@test.com',
        'password': 'testpass123',
        'telefono': '123456789'
    }


class BaseTest:
    """Clase base para todas las pruebas"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Configuración inicial para cada prueba"""
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
        
        # Opciones para entorno de CI/CD
        if os.getenv('HEADLESS', 'false').lower() == 'true':
            chrome_options.add_argument('--headless')
        
        self.driver = None
        
        # Verificar que Chrome esté instalado
        print("🔍 Verificando instalación de Chrome...")
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
                    self.driver.implicitly_wait(TestConfig.IMPLICIT_WAIT)
                    self.wait = WebDriverWait(self.driver, TestConfig.TIMEOUT)
                    break
            except Exception as e:
                print(f"❌ Método {i} falló: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                continue
        
        if not self.driver:
            raise Exception("❌ No se pudo inicializar Chrome con ningún método disponible")
        
        yield
        
        # Limpieza después de cada prueba
        try:
            if hasattr(self, 'driver') and self.driver:
                print("🧹 Cerrando driver...")
                self.driver.quit()
                print("✅ Driver cerrado correctamente")
        except Exception as e:
            print(f"⚠️ Error cerrando driver: {e}")
        finally:
            self.driver = None
    
    def _try_webdriver_manager(self, chrome_options):
        """Intentar usando webdriver-manager"""
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            print("📦 Usando webdriver-manager...")
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
    
    def get_base_url(self):
        """Obtener URL base"""
        return TestConfig.BASE_URL
    
    def navigate_to(self, path=''):
        """Navegar a una ruta específica"""
        url = f"{self.get_base_url()}{path}"
        self.driver.get(url)
        return self
