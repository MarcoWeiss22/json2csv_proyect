import io
import sys

import pytest

from src.json2csv import json_to_csv, main, parse_arguments


def test_json_to_csv_basic():
    json_data = '[{"nombre": "Ana", "edad": 30}, {"nombre": "Juan", "edad": 25, "ciudad": "Madrid"}]'
    in_stream = io.StringIO(json_data)
    out_stream = io.StringIO()

    json_to_csv(in_stream, out_stream, delimiter=",")
    result = out_stream.getvalue()

    assert "nombre,edad,ciudad" in result
    assert "Ana,30," in result
    assert "Juan,25,Madrid" in result


def test_json_to_csv_single_object():
    json_data_valid = '{"id": 1, "item": "Laptop"}'
    in_stream = io.StringIO(json_data_valid)
    out_stream = io.StringIO()

    json_to_csv(in_stream, out_stream, delimiter=";")
    result = out_stream.getvalue()

    assert "id;item" in result
    assert "1;Laptop" in result


def test_json_to_csv_invalid_json():
    json_data = '[{"nombre": "Ana"'
    in_stream = io.StringIO(json_data)
    out_stream = io.StringIO()

    with pytest.raises(ValueError, match="Error al decodificar el archivo JSON"):
        json_to_csv(in_stream, out_stream)


def test_json_to_csv_invalid_structure():
    json_data = '"Solo un string, no un objeto ni lista"'
    in_stream = io.StringIO(json_data)
    out_stream = io.StringIO()

    # Actualizado a TypeError según la regla TRY004
    with pytest.raises(TypeError, match="El contenido del JSON debe ser un objeto"):
        json_to_csv(in_stream, out_stream)


def test_json_to_csv_invalid_list_elements():
    json_data = '["string en lugar de objeto"]'
    in_stream = io.StringIO(json_data)
    out_stream = io.StringIO()

    # Actualizado a TypeError según la regla TRY004
    with pytest.raises(TypeError, match="Cada elemento del JSON debe ser un objeto"):
        json_to_csv(in_stream, out_stream)


def test_json_to_csv_empty_list():
    json_data = '[]'
    in_stream = io.StringIO(json_data)
    out_stream = io.StringIO()
    json_to_csv(in_stream, out_stream)
    assert out_stream.getvalue() == ""


def test_parse_arguments(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["json2csv.py", "-i", "input.json", "-o", "output.csv", "-d", ";"])
    args = parse_arguments()
    assert args.input == "input.json"
    assert args.output == "output.csv"
    assert args.delimiter == ";"


def test_main_with_files(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    input_file = d / "input.json"
    input_file.write_text('[{"test": 123}]', encoding="utf-8")
    
    output_file = d / "output.csv"

    sys.argv = ["json2csv.py", "-i", str(input_file), "-o", str(output_file), "-d", ","]
    main()

    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "test" in content
    assert "123" in content


def test_main_with_stdin_stdout(monkeypatch):
    json_data = '[{"stdio": "test"}]'
    monkeypatch.setattr(sys, "stdin", io.StringIO(json_data))
    
    out_stream = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_stream)
    
    monkeypatch.setattr(sys, "argv", ["json2csv.py"])
    
    main()
    result = out_stream.getvalue()
    assert "stdio" in result
    assert "test" in result


def test_main_exception_handling(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["json2csv.py", "-i", "archivo_que_no_existe.json"])
    
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1