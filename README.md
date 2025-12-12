## ✨ Características

- **Auto-Setup completo**: Crea entorno virtual e instala dependencias automáticamente
- **Detección inteligente**: Filtra falsos positivos (tutoriales, blogs, documentos PDF)
- **Escaneo masivo**: Procesa miles de URLs concurrentemente (10-50 workers)
- **Múltiples vectores**: Prueba parámetros URL y formularios
- **Reportes detallados**: Genera resultados en TXT y JSON
- **Interfaz amigable**: Menú interactivo con colores

## 🚀 Instalación Rápida

### Método 1: Ejecución Directa

# Clonar repositorio
git clone https://github.com/Dsigala/Scanner-urls.git
cd Scanner-urls

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar (se auto-configura)
python scannerurls.py

# 📊 Ejemplo de Resultado

[!] VULNERABLE: http://testphp.vulnweb.com/artists.php?artist=1'
    [+] URL_PARAM: Inyección SQL en parámetro: artist
        Payload: http://testphp.vulnweb.com/artists.php?artist=1'

# 🛡️ Seguridad y Ética
# ⚠️ ADVERTENCIA: USO SOLO PARA FINES EDUCATIVOS Y TESTING AUTORIZADO

NUNCA escanees sitios sin permiso explícito por escrito

SOLO usa en entornos controlados de testing

RESPETALAS leyes locales sobre seguridad informática

El autor NO se responsabiliza del uso indebido


# 👤 Autor
Dsigala - GitHub

# 🙏 Agradecimientos
Inspirado en herramientas open-source de seguridad

Comunidad de Python

Sitios de testing legales

Contribuidores y testers
