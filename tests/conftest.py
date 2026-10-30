# Se agrega `src/` al path para que `reservas` (paquete dentro de src/)
# sea importable por los tests sin instalar el proyecto.
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
