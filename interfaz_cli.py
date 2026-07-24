import os
from art import text2art
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

from main import agente_orquestador

console = Console()

def mostrar_bienvenida():
    banner = text2art("Patito S.A.", font="small")
    console.print(Text(banner, style="bold cyan"))
    console.print(Panel.fit(
        "[bold]Mesa de Ayuda IA — Recursos Humanos[/bold]\n\n"
        "Escribe tu pregunta en lenguaje natural y presiona Enter.\n\n"
        "[dim]Comandos disponibles:[/dim]\n"
        "  [yellow]/imagen[/yellow] <ruta>   → adjunta una imagen a tu próxima pregunta\n"
        "  [yellow]/salir[/yellow]           → termina el programa",
        border_style="cyan",
        title="Bienvenido",
    ))
    console.print()

def main():
    mostrar_bienvenida()
    ruta_imagen_pendiente = None

    while True:
        entrada = console.input("[bold green]Tú:[/bold green] ").strip()

        if not entrada:
            continue

        if entrada.lower() in ("/salir", "salir", "exit", "quit"):
            console.print("\n[bold cyan]Gracias por usar la Mesa de Ayuda IA de RR. HH. ¡Hasta pronto![/bold cyan]")
            break

        if entrada.lower().startswith("/imagen"):
            partes = entrada.split(maxsplit=1)
            if len(partes) < 2:
                console.print("[red]Uso correcto:[/red] /imagen ruta/a/la/imagen.png\n")
                continue

            ruta = partes[1].strip()
            if not os.path.exists(ruta):
                console.print(f"[red]No se encontró el archivo '{ruta}'. Verifica la ruta.[/red]\n")
                continue

            ruta_imagen_pendiente = ruta
            console.print(f"[green]Imagen '{ruta}' adjuntada.[/green] Ahora escribe tu pregunta sobre ella.\n")
            continue

        try:
            with console.status("[bold cyan]Procesando tu consulta...[/bold cyan]", spinner="dots"):
                respuesta = agente_orquestador(entrada, ruta_imagen=ruta_imagen_pendiente)

            console.print(Panel(
                Markdown(respuesta),
                title="[bold]Respuesta[/bold]",
                border_style="green",
            ))
        except Exception as e:
            console.print(f"[bold red]Ocurrió un error inesperado al procesar tu consulta:[/bold red] {e}")
        finally:
            ruta_imagen_pendiente = None

        console.print()


if __name__ == "__main__":
    main()