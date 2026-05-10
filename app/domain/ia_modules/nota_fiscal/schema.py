from typing import Dict, Any

NOTA_FISCAL_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "numero": {"type": "string"},
        "serie": {"type": "string"},
        "data_emissao": {"type": "string"},
        "valor_total": {"type": "number"},
        "emitente": {
            "type": "object",
            "properties": {
                "nome": {"type": "string"},
                "cnpj": {"type": "string"}
            }
        },
        "destinatario": {
            "type": "object",
            "properties": {
                "nome": {"type": "string"},
                "cpf_cnpj": {"type": "string"}
            }
        },
        "itens": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "descricao": {"type": "string"},
                    "quantidade": {"type": "number"},
                    "valor_unitario": {"type": "number"},
                    "valor_total": {"type": "number"}
                }
            }
        }
    },
    "required": ["numero", "data_emissao", "valor_total"]
}
