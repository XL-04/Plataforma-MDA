# PMDA - Plataforma Multimodal para Diagnóstico Asistido

## Descripción
Aplicativo de escritorio (PyQt5) bajo arquitectura MVC para cargar, procesar y analizar imágenes médicas, señales (.mat) y datos tabulares (CSV). Guarda resultados y registro de actividad en base de datos (MongoDB o MySQL).

## Requisitos
- Python 3.8+
- Instalar dependencias: `pip install -r requirements.txt`
- Tener Qt Designer para crear/editar .ui
- MongoDB o MySQL (opcional, para registro)

## Estructura del proyecto
(Ver estructura propuesta en el README del repo.)

## Primeros pasos
1. Clonar repo.
2. Crear `config/users.xml` con usuarios de prueba.
3. Editar `config/app_config.json` si deseas configurar la BD.
4. Ejecutar: `python main.py`

## Flujo de uso
1. Ingresar credenciales en la ventana de login.
2. En la ventana principal:
   - `Capturar foto` → toma foto por webcam, la convierte a gris y guarda en `results/users/<user>/`.
   - `Cargar imagen` → cargar DICOM/NIfTI/JPG/PNG → muestra cortes (sagital/coronal/axial) y aplicables filtros.
   - `Cargar señal` → cargar archivo `.mat` → calcula FFT por canal → despliega tabla y guarda CSV.
   - `Cargar CSV` → visualiza datos y permite seleccionar columnas para graficar.
3. Todas las acciones relevantes quedan registradas en la BD (según configuración).

## Notas de implementación
- Las interfaces `.ui` deben ser editadas en Qt Designer. No escribir la interfaz sólo por código.
- Si la ejecución falla, revisar versiones de PyQt/opencv/pydicom.

## Entregables
- Código comprimido (.zip)
- Link a GitHub (repo)
- Capturas de las interfaces (.png)
- Diagrama de clases (`docs/class_diagram.puml`)
- Manual de usuario (`docs/manual_usuario.md`)
