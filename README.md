# Mesa de Ayuda IA con Agentes Especializados — RR. HH. Patito S.A.

Prototipo funcional de una mesa de ayuda de inteligencia artificial para el Departamento de Recursos Humanos de **Patito S.A.** (datos ficticios), desarrollado como proyecto final del Semillero de Inteligencia Artificial.

El sistema está compuesto por **agentes especializados construidos con LangChain** que colaboran entre sí, coordinados por un **agente orquestador**, para responder consultas de los colaboradores en lenguaje natural usando una base documental ficticia.

> **Nota:** este es un prototipo funcional con fines educativos, no una solución productiva completa.

---

## 1. Objetivo

Permitir que un usuario realice una pregunta en lenguaje natural y que el sistema:

1. Identifique qué agente o agentes especializados deben intervenir.
2. Consulte la base de conocimiento correspondiente (RAG).
3. Entregue una respuesta consolidada, trazable y basada únicamente en los documentos proporcionados.

---

## 2. Arquitectura

```
                         ┌─────────────────────┐
                         │   Usuario (CLI)      │
                         └──────────┬───────────┘
                                    │ pregunta (+ imagen opcional)
                                    ▼
                         ┌─────────────────────┐
                         │  Agente Orquestador  │
                         │  (Gemini + LangChain)│
                         └──────────┬───────────┘
                                    │ clasifica intención (JSON)
              ┌─────────────────────┼─────────────────────┬───────────────────┐
              ▼                     ▼                     ▼                   ▼
   ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │ Agente Beneficios y │ │ Agente Políticas    │ │ Agente Reclutamiento │ │ Agente Multimodal   │
   │ Compensaciones (RAG)│ │ Internas (RAG)       │ │ y Onboarding (RAG)   │ │ de Imagen (Visión)  │
   │ vectorstores/       │ │ vectorstores/         │ │ vectorstores/         │ │ Gemini Vision       │
   │ beneficios           │ │ reglamento             │ │ onboarding             │ │                      │
   └──────────┬──────────┘ └──────────┬───────────┘ └──────────┬───────────┘ └──────────┬───────────┘
              │                        │                          │                       │
              └────────────────────────┴──────────────────────────┴───────────────────────┘
                                            │ respuestas parciales + fuentes
                                            ▼
                                 ┌─────────────────────┐
                                 │  Consolidación final  │
                                 │  (Agente Orquestador) │
                                 └──────────┬───────────┘
                                            ▼
                         Respuesta final + agentes participantes + fuentes usadas
```

### Flujo de ejecución

1. El usuario escribe una pregunta en la interfaz CLI (opcionalmente adjunta una imagen con `/imagen <ruta>`).
2. El **agente orquestador** (`main.py`) recibe la pregunta y usa un LLM de Gemini para clasificar la intención, devolviendo un JSON con la lista de agentes que deben intervenir.
3. Si el usuario adjuntó una imagen, el sistema **fuerza** la inclusión del agente de imagen en la lista de agentes a invocar, sin depender exclusivamente de que el LLM lo detecte por el texto.
4. Se invoca cada agente seleccionado:
   - Los **agentes de lectura (RAG)** (`agente_txt.py`) abren su índice vectorial ya persistido (generado previamente por `build_index.py`), recuperan los fragmentos más relevantes y generan una respuesta basada únicamente en ese contexto.
   - El **agente multimodal** (`agente_imagenes.py`) analiza la imagen adjunta usando la capacidad de visión de Gemini.
5. El orquestador **consolida** todas las respuestas parciales en una única respuesta final, coherente y en español.
6. Se devuelve la respuesta junto con los **agentes participantes** y las **fuentes utilizadas** (trazabilidad).

---

## 3. Agentes implementados

| Agente | Tipo | Base de conocimiento | Archivo |
|---|---|---|---|
| Beneficios y Compensaciones | RAG | `01_Beneficios_Compensaciones.txt` | `agente_txt.py` |
| Políticas Internas (Reglamento) | RAG | `02_Reglamento_Interno.txt` | `agente_txt.py` |
| Reclutamiento y Onboarding | RAG | `03_Reclutamiento_Onboarding.txt` | `agente_txt.py` |
| Multimodal de Imagen | Visión (sin RAG) | N/A — analiza la imagen adjunta directamente | `agente_imagenes.py` |
| Orquestador | Enrutamiento + consolidación | N/A | `main.py` |

**Decisión de alcance:** de los dos agentes adicionales sugeridos por el enunciado (multimodal de imagen o agente de acción), se implementó **únicamente el agente multimodal de imagen**, cumpliendo así el requisito mínimo de incluir al menos uno de los dos. No se implementó el agente de acción (registro en `.txt`) para mantener el prototipo enfocado y dentro del alcance de tiempo del semillero.

---

## 4. Stack tecnológico

- **Lenguaje:** Python 3.10+
- **Framework de agentes:** LangChain
- **LLM:** Google Gemini vía `langchain-google-genai` (`ChatGoogleGenerativeAI`), modelo `gemini-3.5-flash`
- **Embeddings:** Google Gemini vía `GoogleGenerativeAIEmbeddings`, modelo `gemini-embedding-001`
- **Vector store:** Chroma, con persistencia en disco (un índice independiente por agente de lectura)
- **Interfaz:** CLI (línea de comandos)
- **Gestión de secretos:** variables de entorno vía `.env` (`python-dotenv`)

---

## 5. Estructura del proyecto

```
├── main.py                          # Agente orquestador
├── agente_txt.py                    # Agentes de lectura RAG (Beneficios, Reglamento, Onboarding)
├── agente_imagenes.py               # Agente multimodal de imagen
├── build_index.py                   # Script de indexación (genera los vector stores)
├── interfaz_cli.py                  # Interfaz de línea de comandos
├── utils.py                         # Funciones auxiliares compartidas
├── 01_Beneficios_Compensaciones.txt # Base documental — Beneficios
├── 02_Reglamento_Interno.txt        # Base documental — Reglamento
├── 03_Reclutamiento_Onboarding.txt  # Base documental — Reclutamiento
├── imagen_prueba.png                # Imagen de prueba para el agente multimodal
├── requirements.txt                 # Dependencias del proyecto
├── .env.example                     # Plantilla de variables de entorno
├── .gitignore
└── vectorstores/                    # Índices vectoriales persistidos (generados, no versionados)
    ├── beneficios/
    ├── reglamento/
    └── onboarding/
```

---

## 6. Instrucciones de ejecución

### 6.1 Requisitos previos

- Python 3.10 o superior.
- Una API key de Google Gemini, obtenida en [Google AI Studio](https://aistudio.google.com/apikey).

### 6.2 Instalación

- Debemos abrir una carpeta nueva en VSCode y abrimos su terminal

```bash
# 1. Clonar el repositorio
git clone https://github.com/Nicolasp315/Team_Automatizacion_Netlife.git
cd Team_Automatizacion_Netlife

# 2. Crear y activar un entorno virtual
python -m venv entorno
entorno\Scripts\activate      # Windows
source entorno/bin/activate   # macOS / Linux

en caso de tener errores para activar el entorno hay que ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Y reintentar activar el entorno

# 3. Instalar dependencias dentro del entorno
pip install -r requirements.txt
```

### 6.3 Configurar variables de entorno

Crea un archivo ".env" y copia el formato de ".env.example" con tu clave API real:

```
GOOGLE_API_KEY=tu_api_key_real_aqui
```


### 6.4 Generar los índices vectoriales (paso obligatorio antes del primer uso) ejecutando build_index.py

```bash
python build_index.py
```

Este script lee los tres documentos `.txt`, los trocea, genera sus embeddings con Gemini y persiste un índice vectorial independiente por agente en la carpeta `vectorstores/`. Solo es necesario volver a ejecutarlo si cambian los documentos fuente.

### 6.5 Ejecutar la interfaz

```bash
python interfaz_cli.py
```

Comandos disponibles dentro de la CLI:

| Comando | Descripción |
|---|---|
| `<pregunta>` | Envía una pregunta en lenguaje natural al sistema |
| `/imagen <ruta>` | Adjunta una imagen a la siguiente pregunta (para el agente multimodal) | Ejemplo /imagen C:\Users\nicol\Documents\Proyecto Final Netlife\imagen_prueba.png
| `/salir` | Termina el programa |

### Ejemplos de uso

**Consulta a un solo agente:**
```
Tú: ¿Cuántos días de vacaciones me corresponden al año?
```

**Consulta mixta (invoca varios agentes):**
```
Tú: Voy a tomar mis vacaciones y además quiero agregar a mi pareja al seguro médico.
    ¿Cuántos días me corresponden, cómo los solicito y qué necesito para inscribir
    a un dependiente en el beneficio?
```

**Consulta con imagen:**
```
Tú: /imagen imagen_prueba.png
Tú: ¿Está completo este formulario de inscripción de dependientes?
```

---

## 7. Trazabilidad y control de alucinaciones

- Cada agente de lectura responde **únicamente** con base en los fragmentos recuperados de su propio índice vectorial; no mezcla conocimiento entre agentes.
- Si un agente no encuentra información suficiente, responde explícitamente: *"No encontré información suficiente en la base documental proporcionada."*, sin inventar contenido.
- Cada respuesta final incluye los **agentes participantes** y las **fuentes documentales utilizadas**, para que el usuario pueda verificar el origen de la información.

---

## 8. Decisiones técnicas y trade-offs

| Decisión | Justificación |
|---|---|
| **Separar indexación (`build_index.py`) de consulta (`agente_txt.py`)** | Evita regenerar embeddings en cada pregunta del usuario, lo cual sería lento y consumiría cuota de la API innecesariamente. El índice se genera una vez y se reutiliza. |
| **Modelo de embeddings `gemini-embedding-001`** | El modelo originalmente sugerido, `text-embedding-004`, fue descontinuado por Google. Se migró al modelo vigente equivalente. |
| **Modelo de LLM `gemini-3.5-flash`** | El modelo originalmente usado, `gemini-2.5-flash`, dejó de estar disponible para nuevas cuentas de la API. Se migró al modelo de la familia Flash vigente. |
| **`chunk_size=1000`, `chunk_overlap=200`** | Balance entre mantener contexto suficiente por fragmento y permitir que el retriever distinga subtemas dentro de cada documento. |
| **`k=3` en el retriever** | Se recuperan los 3 fragmentos más relevantes por consulta como balance entre cobertura de contexto y ruido irrelevante. |
| **Un solo agente adicional (multimodal de imagen)** | Cumple el requisito mínimo del enunciado (al menos uno de dos) manteniendo el alcance del prototipo acotado. |
| **Normalización de respuestas (`utils.py` → `extraer_texto`)** | Algunas versiones recientes de Gemini devuelven el contenido de la respuesta como lista de fragmentos en vez de string plano; esta función unifica ambos formatos. |

---

## 9. Riesgos y limitaciones conocidas

- **Cuota del free tier de Gemini:** la capa gratuita de la API tiene límites de solicitudes por minuto y por día. En uso intensivo (varias preguntas seguidas), el sistema puede recibir errores `429 RESOURCE_EXHAUSTED`. Para un entorno productivo se recomendaría un plan de pago y/o lógica de reintentos con backoff.
- **Cambios frecuentes en el catálogo de modelos de Google:** durante el desarrollo, tanto el modelo de LLM como el de embeddings originalmente sugeridos fueron descontinuados por Google. Se recomienda no hardcodear nombres de modelo en producción sin un mecanismo de verificación/actualización periódica.
- **Telemetría interna de Chroma:** en el entorno de desarrollo aparecen advertencias `Failed to send telemetry event` al usar Chroma. Son inofensivas (no afectan la funcionalidad) y provienen de una incompatibilidad entre versiones internas de la librería. Pueden silenciarse configurando `ANONYMIZED_TELEMETRY=False`.
- **Prototipo, no solución productiva:** no incluye autenticación de usuarios, control de acceso por documento/agente, logging estructurado, ni monitoreo de costos/latencia — quedan como mejoras futuras.
- **Base documental ficticia y acotada:** los documentos de prueba entregados son breves; en un escenario real, con documentos más extensos, el sistema tendría mayor margen para la recuperación semántica.

---

## 10. Mejoras futuras

- Implementar el agente de acción (registro de solicitudes en archivo `.txt` con validación de datos obligatorios).
- Agregar una interfaz web o API REST (FastAPI) como alternativa a la CLI.
- Incorporar manejo de reintentos ante errores de cuota (`429`) con backoff exponencial.
- Añadir logging estructurado evitando registrar información sensible.
- Definir un esquema de permisos por documento/agente para escenarios multiusuario.
- Añadir monitoreo de tokens consumidos, latencia por consulta y feedback de usuarios.

---
