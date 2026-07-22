def extraer_texto(contenido):
    """
    Normaliza la respuesta del modelo: algunos modelos devuelven .content
    como string, otros como lista de fragmentos (dicts con 'text').
    """
    if isinstance(contenido, str):
        return contenido.strip()
    if isinstance(contenido, list):
        partes = []
        for item in contenido:
            if isinstance(item, str):
                partes.append(item)
            elif isinstance(item, dict) and "text" in item:
                partes.append(item["text"])
        return "".join(partes).strip()
    return str(contenido).strip()