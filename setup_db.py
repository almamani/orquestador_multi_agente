import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "data" / "ventas.db"

# Los importes se guardan en centavos.
VENTAS_EJEMPLO = [
    ("Cruceta GMB", "2026-09", 10, 10_000_000),
    ("Cruceta GMB", "2026-10", 12, 12_000_000),
    ("Óptica Kangoo", "2026-09", 10, 8_000_000),
    ("Óptica Kangoo", "2026-10", 9, 7_200_000),
    ("Tanza redonda", "2026-09", 0, 0),
    ("Tanza redonda", "2026-10", 5, 2_500_000),
]


def crear_base():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS ventas_mensuales (
                producto TEXT NOT NULL,
                periodo TEXT NOT NULL,
                unidades INTEGER NOT NULL CHECK (unidades >= 0),
                importe_centavos INTEGER NOT NULL
                    CHECK (importe_centavos >= 0),
                PRIMARY KEY (producto, periodo)
            )
            """
        )

        conexion.executemany(
            """
            INSERT INTO ventas_mensuales (
                producto,
                periodo,
                unidades,
                importe_centavos
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT (producto, periodo) DO NOTHING
            """,
            VENTAS_EJEMPLO,
        )

        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM ventas_mensuales"
        ).fetchone()[0]

    print(f"Base preparada: {DB_PATH}")
    print(f"Registros disponibles: {cantidad}")


if __name__ == "__main__":
    crear_base()