import pytest
import logging
import os
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('selenium_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SeleniumConfig:
    """Configuración centralizada para Selenium"""
    
    BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    PAGE_LOAD_TIMEOUT = 20
    
    # Detectar si está en CI/Jenkins
    HEADLESS = os.getenv("CI") == "true" or os.getenv("JENKINS_URL") is not None
    SCREEN_RESOLUTION = (1920, 1080)


@pytest.fixture(scope="session")
def setup_test_session():
    """Setup de la sesión de pruebas"""
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO SESIÓN DE PRUEBAS SELENIUM")
    logger.info(f"📍 Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 URL Base: {SeleniumConfig.BASE_URL}")
    logger.info(f"🎯 Modo Headless: {SeleniumConfig.HEADLESS}")
    logger.info("=" * 70)
    
    yield
    
    logger.info("=" * 70)
    logger.info("✅ SESIÓN DE PRUEBAS FINALIZADA")
    logger.info("=" * 70)


@pytest.fixture(scope="function")
def chrome_driver():
    """Fixture que proporciona un driver de Chrome configurado"""
    
    logger.info(f"🔧 Configurando ChromeDriver...")
    
    options = Options()
    
    # Configurar opciones de Chrome
    if SeleniumConfig.HEADLESS:
        options.add_argument("--headless")
        logger.info("   ✓ Modo Headless activado")
    
    # Opciones de performance
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Anti-detección
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # Deshabilitar notificaciones
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    
    # Deshabilitar logging
    options.add_argument("--log-level=3")
    
    logger.info("   ✓ Opciones configuradas")
    
    # Crear driver con webdriver-manager
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("   ✓ ChromeDriver iniciado")
    except Exception as e:
        logger.error(f"   ❌ Error al iniciar ChromeDriver: {str(e)}")
        raise
    
    # Configurar timeouts
    driver.set_window_size(*SeleniumConfig.SCREEN_RESOLUTION)
    driver.implicitly_wait(SeleniumConfig.IMPLICIT_WAIT)
    driver.set_page_load_timeout(SeleniumConfig.PAGE_LOAD_TIMEOUT)
    
    logger.info(f"   ✓ Resolución: {SeleniumConfig.SCREEN_RESOLUTION}")
    logger.info(f"   ✓ Timeouts configurados")
    
    yield driver
    
    # Cleanup
    logger.info("🔧 Cerrando ChromeDriver...")
    try:
        driver.quit()
        logger.info("   ✓ ChromeDriver cerrado correctamente")
    except Exception as e:
        logger.error(f"   ⚠️ Error al cerrar driver: {str(e)}")


@pytest.fixture(scope="function")
def wait(chrome_driver):
    """Fixture que proporciona WebDriverWait configurado"""
    return WebDriverWait(chrome_driver, SeleniumConfig.EXPLICIT_WAIT)


@pytest.fixture(autouse=True)
def log_test_info(request):
    """Log automático de información del test"""
    logger.info("-" * 70)
    logger.info(f"🧪 TEST: {request.node.name}")
    logger.info(f"📝 Descripción: {request.node.obj.__doc__ or 'Sin descripción'}")
    logger.info("-" * 70)
    
    yield
    
    logger.info(f"✅ TEST FINALIZADO: {request.node.name}\n")


def pytest_configure(config):
    """Configuración de pytest"""
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )   