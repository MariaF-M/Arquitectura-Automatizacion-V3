"""Registro de generadores por lenguaje (agregar un lenguaje = agregar una clase aquí; OCP)."""
from .python_gen import GeneradorPython

GENERADORES = {"python": GeneradorPython}

try:
    from .java_gen import GeneradorJava
    GENERADORES["java"] = GeneradorJava
except ImportError:  # pragma: no cover
    pass
try:
    from .csharp_gen import GeneradorCSharp
    GENERADORES["csharp"] = GeneradorCSharp
except ImportError:  # pragma: no cover
    pass
