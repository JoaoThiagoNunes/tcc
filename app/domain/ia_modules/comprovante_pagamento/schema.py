from typing import Dict, Any

COMPROVANTE_PAGAMENTO_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "tipo": {"type": "string"},
        "data": {"type": "string"},
        "valor": {"type": "number"},
        "beneficiario": {"type": "string"},
        "pagador": {"type": "string"},
        "codigo_barras": {"type": "string"},
        "numero_documento": {"type": "string"},
        "banco": {"type": "string"},
        "agencia": {"type": "string"},
        "conta": {"type": "string"}
    },
    "required": ["data", "valor"]
}
