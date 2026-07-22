import os
from main import agente_orquestador

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")

def mostrar_bienvenida():
    print("=" * 70)
    print(" MESA DE AYUDA IA - RECURSOS HUMANOS - PATITO S.A.")
    print("=" * 70)
    print("Escribe tu pregunta en lenguaje natural y presiona Enter.")
    print("Comandos disponibles:")
    print("  /imagen <ruta>   -> adjunta una imagen a tu próxima pregunta")
    print("  /salir           -> termina el programa")
    print("=" * 70)
    print()

def main():
    mostrar_bienvenida()
    ruta_imagen_pendiente = None

    while True:
        entrada = input("Tú: ").strip()

        if not entrada:
            continue

        # Comando para salir
        if entrada.lower() in ("/salir", "salir", "exit", "quit"):
            print("\nGracias por usar la Mesa de Ayuda IA de RR. HH. ¡Hasta pronto!")
            break

        # Comando para adjuntar imagen
        if entrada.lower().startswith("/imagen"):
            partes = entrada.split(maxsplit=1)
            if len(partes) < 2:
                print("Uso correcto: /imagen ruta/a/la/imagen.png\n")
                continue

            ruta = partes[1].strip()
            if not os.path.exists(ruta):
                print(f"No se encontró el archivo '{ruta}'. Verifica la ruta.\n")
                continue

            ruta_imagen_pendiente = ruta
            print(f"Imagen '{ruta}' adjuntada. Ahora escribe tu pregunta sobre ella.\n")
            continue

        # Pregunta normal (con o sin imagen adjunta)
        print("\nProcesando tu consulta, un momento...\n")

        try:
            respuesta = agente_orquestador(entrada, ruta_imagen=ruta_imagen_pendiente)
            print(respuesta)
        except Exception as e:
            print(f"Ocurrió un error inesperado al procesar tu consulta: {e}")
        finally:
            # La imagen solo aplica a la siguiente pregunta, luego se limpia
            ruta_imagen_pendiente = None

        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()