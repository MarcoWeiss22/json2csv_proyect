"""Módulo para convertir archivos de formato JSON a CSV utilizando estrategia de filtro."""

import argparse
import csv
import json
import sys
from contextlib import nullcontext
from typing import TextIO


def json_to_csv(
    input_stream: TextIO, output_stream: TextIO, delimiter: str = ","
) -> None:
    """Convierte un flujo de datos JSON a formato CSV y los escribe en un flujo de salida."""
    try:
        data = json.load(input_stream)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al decodificar el archivo JSON: {e}") from e

    if isinstance(data, dict):
        rows = [data]
    elif isinstance(data, list):
        rows = data
    else:
        raise TypeError(
            "El contenido del JSON debe ser un objeto o una lista de objetos."
        )

    if not rows:
        return

    headers = []
    for row in rows:
        if isinstance(row, dict):
            for key in row:
                if key not in headers:
                    headers.append(key)
        else:
            raise TypeError("Cada elemento del JSON debe ser un objeto (diccionario).")

    writer = csv.DictWriter(output_stream, fieldnames=headers, delimiter=delimiter)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def parse_arguments() -> argparse.Namespace:
    """Analiza los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Convierte un archivo JSON a formato CSV."
    )
    parser.add_argument(
        "-i", "--input", type=str, help="Archivo JSON de entrada (por defecto: stdin)"
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Archivo CSV de salida (por defecto: stdout)"
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        type=str,
        default=",",
        help="Delimitador para el archivo CSV",
    )
    return parser.parse_args()


def main() -> None:
    """Punto de entrada principal para la ejecución por línea de comandos."""
    args = parse_arguments()

    try:
        # Movemos el bloque try para atrapar errores de apertura de archivos (FileNotFoundError/OSError)
        with (
            (
                open(args.input, "r", encoding="utf-8")
                if args.input
                else nullcontext(sys.stdin)
            ) as infile,
            (
                open(args.output, "w", encoding="utf-8", newline="")
                if args.output
                else nullcontext(sys.stdout)
            ) as outfile,
        ):
            json_to_csv(infile, outfile, delimiter=args.delimiter)
    except (OSError, ValueError, TypeError) as e:
        sys.stderr.write(f"Error de ejecución: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
