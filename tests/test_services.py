from app.services import _filter_content

def test_filter_content_no_banned_words():
    """Prueba que el contenido no se modifica si no hay palabras prohibidas."""
    content = "Este es un mensaje limpio y seguro."
    filtered = _filter_content(content)
    assert filtered == content

def test_filter_content_with_banned_words():
    """Prueba que las palabras prohibidas son reemplazadas."""
    content = "Este es un mensaje con una palabra inapropiada y otra prohibida."
    expected = "Este es un mensaje con una palabra **** y otra ****."
    # Añadimos las palabras al set para la prueba
    from app import services
    services.BANNED_WORDS = {"inapropiada", "prohibida"}
    filtered = _filter_content(content)
    assert filtered == expected

def test_filter_content_case_insensitive():
    """Prueba que el filtrado no distingue mayúsculas y minúsculas."""
    content = "Mensaje con INAPROPIADA en mayúsculas."
    expected = "Mensaje con **** en mayúsculas."
    from app import services
    services.BANNED_WORDS = {"inapropiada"}
    filtered = _filter_content(content)
    assert filtered == expected
