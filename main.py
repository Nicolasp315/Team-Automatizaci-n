import os
import json #Para que Gemini responda en formato Json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from utils import extraer_texto

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("No se encontró GOOGLE_API_KEY en el archivo .env")

# Importamos los agentes individuales
from agente_txt import agente_beneficios, agente_reglamento, agente_onboarding
from agente_imagenes import agente_imagen

# =====================================================================
# PROMPT DEL ORQUESTADOR 
# =====================================================================
ORCHESTRATOR_TEMPLATE = """You are the Master Orchestrator Agent for a Human Resources AI System.
Your job is to analyze the user's input and determine which specialized agents must be invoked to solve the request.

Available Agents and their domains:
- "agente_beneficios": For questions about salaries, medical insurance, bonuses, paid leave, or financial compensations.
- "agente_reglamento": For questions about internal rules, codes of conduct, office hours, permissions, or vacations.
- "agente_onboarding": For questions about hiring processes, welcoming new staff, training, or recruitment requirements.
- "agente_imagen": For image, photo, or document analysis, visual validation, and document audits.

You can select multiple agents if the query covers more than one topic.
You must respond ONLY with a raw JSON object. Do not include markdown code blocks (```json).

JSON Structure:
{{
    "intent": "Brief description of the user's intent",
    "selected_agents": ["agente_beneficios", "agente_imagen"]
}}

User Input: {user_input}
"""

def agente_orquestador(pregunta_usuario, ruta_imagen=None):#Funcion para interfaz
    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    except Exception as e:
        return f"Error al inicializar el modelo de Gemini: {e}"

    # -----------------------------------------------------------------
    # Clasificar intención a través del LLM
    # -----------------------------------------------------------------
    prompt_orquestador = PromptTemplate.from_template(ORCHESTRATOR_TEMPLATE)#Plantilla para ingresar la pregunta al prompt
    cadena_enrutamiento = prompt_orquestador | model#Rellena la plantilla con la pregunta

    try:
        respuesta_enrutador = cadena_enrutamiento.invoke({"user_input": pregunta_usuario})#Respuesta del modelo, nos dice la intención de la preguntay  agentes seleccionados
        texto_decision = extraer_texto(respuesta_enrutador.content)#Normalizamos la respuesta a un string
        decision = json.loads(texto_decision.replace("```json", "").replace("```", ""))#Pasamos el string a un dict
    except Exception:
        # Fallback de emergencia si falla la generación del JSON o la llamada al modelo
        decision = {"selected_agents": ["agente_reglamento"]}

    lista_agentes_elegidos = decision.get("selected_agents", [])

    # Si se adjuntó una imagen, forzamos la inclusión del agente de imagen
    if ruta_imagen and "agente_imagen" not in lista_agentes_elegidos:
        lista_agentes_elegidos.append("agente_imagen")

    # -----------------------------------------------------------------
    # Trazabilidad de cada agente
    # -----------------------------------------------------------------
    agentes_participantes = []
    fuentes_utilizadas = []
    respuestas_fragmentadas = []

    MAPPING_TEXTO = {#Relacionamos la función con el nombre del txt y el nombre presentado en la trazabilidad
        "agente_beneficios": (agente_beneficios, "01_Beneficios_Compensaciones.txt", "Agente de Beneficios y Compensaciones"),
        "agente_reglamento": (agente_reglamento, "02_Reglamento_Interno.txt", "Agente del Reglamento Interno"),
        "agente_onboarding": (agente_onboarding, "03_Reclutamiento_Onboarding.txt", "Agente de Reclutamiento y Onboarding"),
    }

    # 1. Evaluar e invocar agentes de texto
    for agente_id in lista_agentes_elegidos:
        if agente_id in MAPPING_TEXTO:
            funcion_agente, archivo_txt, nombre_exacto = MAPPING_TEXTO[agente_id]#Desempaquetamos: Funcion, nombre del txt y nombre exacto

            agentes_participantes.append(nombre_exacto)
            fuentes_utilizadas.append(archivo_txt)

            try:
                res_txt = funcion_agente(pregunta_usuario, model)
            except Exception as e:
                res_txt = f"Error al consultar {nombre_exacto}: {e}"#Respuesta si ocurre un eror(Cuota, conexión, etc)

            respuestas_fragmentadas.append(f"**{nombre_exacto} Response:**\n{res_txt}")

    # 2. Evaluar e invocar al agente Multimodal de Imagen
    if "agente_imagen" in lista_agentes_elegidos:
        if ruta_imagen and os.path.exists(ruta_imagen):
            nombre_imagen_exacto = "agente_imagen"
            agentes_participantes.append(nombre_imagen_exacto)
            fuentes_utilizadas.append(os.path.basename(ruta_imagen))

            try:
                res_img = agente_imagen(ruta_imagen, pregunta_usuario, model)
            except Exception as e:
                res_img = f"Error al procesar la imagen: {e}"

            respuestas_fragmentadas.append(f"**{nombre_imagen_exacto} Response:**\n{res_img}")
        else:
            respuestas_fragmentadas.append("No se detecta ninguna imagen.")

    if not respuestas_fragmentadas:
        respuestas_fragmentadas.append("No se necesito de los agentes especializados")

    # -----------------------------------------------------------------
    # Consolidación por el Orquestador e impresión Final
    # -----------------------------------------------------------------
    # Aqui pasamos todas las respuestas parciales de los agentes y el agente orquestador se decide por una
    # En caso de que respondan 2 o mas agentes, el orquestador arma una sola respuesta coherente
    nombres_agentes = ", ".join(agentes_participantes)
    union_respuestas = "\n\n".join(respuestas_fragmentadas)

    PROMPT_CONSOLIDACION = """You are the Master Orchestrator Agent. 
You have received raw responses from one or more specialized human resources sub-agents. 
Your job is to synthesize, clean up redundancies, and deliver a SINGLE unified, professional, and coherent answer to the user's original question in Spanish.

Original User Question: {user_input}

Sub-agents raw responses:
{raw_responses}

Final Consolidated Answer (Write this beautifully in Spanish):"""

    prompt_consolidar = PromptTemplate.from_template(PROMPT_CONSOLIDACION)
    cadena_consolidacion = prompt_consolidar | model

    try:
        respuesta_cruda = cadena_consolidacion.invoke({
            "user_input": pregunta_usuario,
            "raw_responses": union_respuestas,
        })
        respuesta_consolidada = extraer_texto(respuesta_cruda.content)
    except Exception as e:
        respuesta_consolidada = f"Error al consolidar la respuesta final: {e}"

    #Agentes participantes
    template_final = (
        f"\n{respuesta_consolidada}\n\n"
        f"---\n"
        f"Agentes Participantes: {nombres_agentes}\n"
        f"Recursos utilizados: {', '.join(fuentes_utilizadas) if fuentes_utilizadas else 'None'}"
    )

    return template_final
