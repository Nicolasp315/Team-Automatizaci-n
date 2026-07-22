import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("No se encontró GOOGLE_API_KEY en el archivo .env")

# =====================================================================
# CONFIGURACIÓN
# =====================================================================
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Mapeo: archivo fuente -> carpeta donde se persiste su índice
DOCUMENTOS = {
    "01_Beneficios_Compensaciones.txt": "vectorstores/beneficios",
    "02_Reglamento_Interno.txt": "vectorstores/reglamento",
    "03_Reclutamiento_Onboarding.txt": "vectorstores/onboarding",
}

def construir_indice(nombre_archivo, carpeta_destino):
    print(f"Procesando: {nombre_archivo} -> {carpeta_destino}")

    if not os.path.exists(nombre_archivo):
        print(f"  ERROR: no se encontró el archivo '{nombre_archivo}'. Se omite.")
        return

    try:
        # 1. Cargar y trocear el documento
        loader = TextLoader(nombre_archivo, encoding="utf-8")
        documentos = loader.load()
        fragmentos = text_splitter.split_documents(documentos)
        print(f"  {len(fragmentos)} fragmentos generados.")

        # 2. Crear el vector store vacío y persistido
        db = Chroma(
            embedding_function=embeddings,
            persist_directory=carpeta_destino,
        )

        # 3. Agregar los documentos (esto genera los embeddings vía Gemini)
        db.add_documents(fragmentos)
        print(f"  Índice guardado en '{carpeta_destino}'.")

    except Exception as e:
        print(f"  ERROR al indexar '{nombre_archivo}': {e}")


if __name__ == "__main__":
    print("=== Construcción de índices vectoriales (Gemini embeddings) ===\n")
    for archivo, carpeta in DOCUMENTOS.items():
        construir_indice(archivo, carpeta)
    print("\n=== Proceso de indexación finalizado ===")