import pytest
from backend.code_parser import parse_source_code
import os

def test_python_code_parsing():
    """Valida se o parser identifica blocos em arquivos Python."""
    code = """
def calculate_temp(raw_val):
    # Converte valor bruto para Celsius
    return raw_val * 0.1

class ThermalController:
    def __init__(self):
        self.temp = 0
    """
    blocks = parse_source_code(code, "py")
    
    # Deve encontrar pelo menos a função e a classe
    assert len(blocks) >= 2
    assert any("calculate_temp" in b for b in blocks)
    assert any("ThermalController" in b for b in blocks)

def test_c_code_parsing():
    """Valida se o parser identifica funções em arquivos C."""
    code = """
void start_heater(int power) {
    // Liga o aquecedor na potência X
    pwm_write(HEATER_PIN, power);
}

int read_sensor() {
    return analogRead(SENSOR_PIN);
}
    """
    blocks = parse_source_code(code, "c")
    
    assert len(blocks) >= 2
    assert any("start_heater" in b for b in blocks)
    assert any("read_sensor" in b for b in blocks)
