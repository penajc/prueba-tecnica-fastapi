from unittest.mock import MagicMock, patch
from app.services import _filter_content
from app.dependencies import get_db, SessionLocal

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

def test_get_db_closes_session():
    """Prueba que la sesión de la base de datos se cierra correctamente."""
    mock_db = MagicMock()
    with patch('app.dependencies.SessionLocal', return_value=mock_db):
        db_generator = get_db()
        # Simula la entrada al contexto del generador
        next(db_generator)
        # Simula la salida del contexto del generador (ejecutando el finally)
        db_generator.close()
    mock_db.close.assert_called_once()
