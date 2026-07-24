import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_core.prompts import PromptTemplate
from utils import extraer_texto
# =====================================================================
# CONFIGURACIÓN COMPARTIDA
# =====================================================================
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

MENSAJE_SIN_INFO = "No encontré información suficiente en la base documental proporcionada."

def consultar_base_rag(carpeta_indice, pregunta, model, rol_prompt):
    """
    Abre el índice vectorial YA PERSISTIDO para el agente correspondiente
    y responde usando únicamente los fragmentos recuperados.
    """
    if not os.path.isdir(carpeta_indice):
        return (
            f"Error: no se encontró el índice en '{carpeta_indice}'. "
            f"Ejecuta build_index.py antes de usar este agente."#Recordatorio para ejecutar el index
        )

    try:
        db = Chroma(
            persist_directory=carpeta_indice,
            embedding_function=embeddings,
            client_settings=Settings(anonymized_telemetry=False),)#Cargamos los embeddings de build_index.py
        retriever = db.as_retriever(search_kwargs={"k": 3})#Tomamos los 3 chunks mas relevantes por consulta

        #Guardamos el contenido de los 3 chunks mas relevantes
        fragmentos_recuperados = retriever.invoke(pregunta)
    except Exception as e:
        return f"Error al acceder a la base de conocimiento: {e}"

    if not fragmentos_recuperados:#En caso de tener respuestas vacias
        return MENSAJE_SIN_INFO

    contexto = "\n".join([d.page_content for d in fragmentos_recuperados])#Juntamos los 3 chunks mas relevantes

    # 3. Prompt estricto
    template = (
        "You are an intelligent " + rol_prompt + ". "
        "Your job is to answer the user's question accurately using ONLY the provided document content.\n\n"
        "User Question: {input}\n\n"
        "Extracted content from relevant documents:\n"
        "{contexto}\n\n"
        "Strict Guidelines for your response:\n"
        "1. Provide ONLY the direct, helpful, and professional answer in Spanish.\n"
        "2. DO NOT include any introductory analysis, bullet points, step-by-step reasoning, "
        "or file references. Go straight to the answer.\n"
        f"3. If you cannot find the answer in the provided context, respond EXACTLY with this "
        f"Spanish sentence and nothing else: \"{MENSAJE_SIN_INFO}\""
    )

    prompt = PromptTemplate.from_template(template)
    cadena = prompt | model

    try:
        resultado = cadena.invoke({"input": pregunta, "contexto": contexto})
        return extraer_texto(resultado.content)
    except Exception as e:
        return f"Error al generar la respuesta: {e}"


# =====================================================================
# EXPORTACIÓN DE LOS 3 AGENTES INDEPENDIENTES
# =====================================================================

def agente_beneficios(pregunta_usuario, model):
    """Agente Experto — índice: vectorstores/beneficios"""
    return consultar_base_rag(
        carpeta_indice="vectorstores/beneficios",
        pregunta=pregunta_usuario,
        model=model,
        rol_prompt="Benefits & Compensation Expert",
    )

def agente_reglamento(pregunta_usuario, model):
    """Agente Experto — índice: vectorstores/reglamento"""
    return consultar_base_rag(
        carpeta_indice="vectorstores/reglamento",
        pregunta=pregunta_usuario,
        model=model,
        rol_prompt="Internal Regulations Expert",
    )

def agente_onboarding(pregunta_usuario, model):
    """Agente Experto — índice: vectorstores/onboarding"""
    return consultar_base_rag(
        carpeta_indice="vectorstores/onboarding",
        pregunta=pregunta_usuario,
        model=model,
        rol_prompt="Recruitment & Onboarding Expert",
    )