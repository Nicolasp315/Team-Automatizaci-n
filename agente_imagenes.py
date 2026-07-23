import os
import base64 #Para convertir datos binarios a texto
import mimetypes #Detecta el formato (.png .jpg etc)
from langchain_core.messages import HumanMessage #Un input de texto+imagen
from utils import extraer_texto

def agente_imagen(ruta_imagen, pregunta_usuario, model):
    if not os.path.exists(ruta_imagen):
        return f"No se encuentra la imagen en la ruta {ruta_imagen}"

    mime_type, _ = mimetypes.guess_type(ruta_imagen)
    mime_type = mime_type or "image/png"

    try:
        with open(ruta_imagen, "rb") as image_file:
            imagen_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        return f"Error al leer la imagen: {e}"

    prompt_sistema = """You are an expert HR Document Auditor.
    Analyze the attached document image and:
    1. Validate if the document has: Identification, banking details, benefits form, and signed contract.
    2. If all information is present, respond only: "El documento ha sido ingresado con éxito"
    3. If information is missing, list in Spanish what is missing."""

    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": f"{prompt_sistema}\n\nUser Question: {pregunta_usuario}"},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{imagen_base64}"},
            },
        ]
    )

    try:
        respuesta = model.invoke([mensaje])
        return extraer_texto(respuesta.content)
    except Exception as e:
        return f"Error al procesar la imagen: {e}"