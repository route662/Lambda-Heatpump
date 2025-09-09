"""API for communicating with Lambda Heatpump via Modbus TCP."""
from pymodbus.client import ModbusTcpClient

async def detect_lambda_model(ip_address):
    """Detect the Lambda Heatpump model."""
    client = ModbusTcpClient(ip_address)
    try:
        # Beispiel: Lese ein spezifisches Register, um das Modell zu identifizieren
        model_register = 1000  # Ersetze dies durch das tatsächliche Register
        # result = client.read_holding_registers(model_register, 1)
        result = client.read_holding_registers(model_register, count=1, device_id=1)
        if result.isError():
            return None
        return f"Model {result.registers[0]}"
    finally:
        client.close()
