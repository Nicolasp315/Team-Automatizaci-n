from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
resultado = embeddings.embed_query("hola mundo")
print("Éxito. Dimensiones del vector:", len(resultado))