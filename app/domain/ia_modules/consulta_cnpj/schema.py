from typing import Dict, Any

CONSULTA_CNPJ_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "cnpj": {"type": "string"},
        "razao_social": {"type": "string"},
        "nome_fantasia": {"type": "string"},
        "situacao": {"type": "string"},
        "data_abertura": {"type": "string"},
        "capital_social": {"type": "number"},
        "endereco": {
            "type": "object",
            "properties": {
                "logradouro": {"type": "string"},
                "numero": {"type": "string"},
                "complemento": {"type": "string"},
                "bairro": {"type": "string"},
                "cidade": {"type": "string"},
                "uf": {"type": "string"},
                "cep": {"type": "string"}
            }
        },
        "atividades_principais": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["cnpj", "razao_social"]
}
