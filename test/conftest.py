"""
conftest.py - Configuración de Pytest para Selenium
CORREGIDO: Sin emojis para compatibilidad con Windows cp1252
"""

import pytest
import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================================
# CONFIGURACIÓN DE LOGGING (SIN EMOJIS)
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_selenium.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================
IMPLICIT_WAIT = 10  # segundos
EXPLICIT_WAIT = 15  # segundos
PAGE_LOAD_TIMEOUT = 30  # segundos

# Base URL desde variable de entorno o default
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")


# ============================================================================
# FIXTURE: Chrome Driver
# ============================================================================
@pytest.fixture(scope="function")
def chrome_driver(request):
    """
    Fixture para inicializar y cerrar ChromeDriver automáticamente.
    Scope: function - Se crea un driver por cada test.
    """
    logger.info("[SETUP] Configurando ChromeDriver...")
    
    # Configurar opciones de Chrome
    chrome_options = Options()
    
    # Opciones para CI/Jenkins
    if os.getenv("CI") == "true":
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        logger.info("[CI MODE] Ejecutando en modo headless")
    
    # Opciones de estabilidad
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Deshabilitar logging de DevTools
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Inicializar el driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Configurar timeouts
        driver.implicitly_wait(IMPLICIT_WAIT)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        
        logger.info("   [OK] ChromeDriver inicializado correctamente")
        logger.info(f"   [INFO] URL Base: {BASE_URL}")
        
    except Exception as e:
        logger.error(f"   [ERROR] Error al inicializar ChromeDriver: {str(e)}")
        raise
    
    # Yield driver al test
    yield driver
    
    # Teardown: Cerrar el driver
    try:
        logger.info("[TEARDOWN] Cerrando ChromeDriver...")
        driver.quit()
        logger.info("   [OK] ChromeDriver cerrado correctamente")
    except Exception as e:
        logger.error(f"   [ERROR] Error al cerrar ChromeDriver: {str(e)}")


# ============================================================================
# FIXTURE: WebDriverWait
# ============================================================================
@pytest.fixture(scope="function")
def wait(chrome_driver):
    """
    Fixture para WebDriverWait con tiempo de espera explícito.
    """
    return WebDriverWait(chrome_driver, EXPLICIT_WAIT)


# ============================================================================
# FIXTURE: Base URL
# ============================================================================
@pytest.fixture(scope="session")
def base_url():
    """
    Fixture para obtener la URL base de la aplicación.
    """
    return BASE_URL


# ============================================================================
# FIXTURE: Log de información del test
# ============================================================================
@pytest.fixture(scope="function", autouse=True)
def log_test_info(request):
    """
    Fixture para loguear información antes y después de cada test.
    """
    logger.info("-" * 70)
    logger.info(f"[TEST] {request.node.name}")
    logger.info(f"[DESC] {request.node.obj.__doc__ or 'Sin descripción'}")
    logger.info("-" * 70)
    
    yield
    
    logger.info(f"[COMPLETED] {request.node.name}\n")


# ============================================================================
# HOOKS DE PYTEST
# ============================================================================
def pytest_configure(config):
    """
    Hook ejecutado antes de iniciar los tests.
    """
    logger.info("=" * 70)
    logger.info("INICIANDO SUITE DE PRUEBAS SELENIUM")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"CI Mode: {os.getenv('CI', 'false')}")
    logger.info("=" * 70)


def pytest_sessionfinish(session, exitstatus):
    """
    Hook ejecutado después de finalizar todos los tests.
    """
    logger.info("=" * 70)
    logger.info("FINALIZANDO SUITE DE PRUEBAS SELENIUM")
    logger.info(f"Exit Status: {exitstatus}")
    logger.info("=" * 70)


def pytest_runtest_makereport(item, call):
    """
    Hook para capturar el resultado de cada test.
    """
    if call.when == "call":
        if call.excinfo is not None:
            logger.error(f"[FAILED] {item.name}: {call.excinfo.value}")
        else:
            logger.info(f"[PASSED] {item.name}")
