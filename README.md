# Pre Analysis Service

Serviço de pré-análise de documentos de Prestação de Contas usando OCR e um motor de regras, com FastAPI em camadas.

## Arquitetura (fluxo)

```
HTTP (upload) → Orquestrador → OCR + Classificador → Extratores (texto / regex) → Motor de regras → Resposta da pré-análise
```

- **OCR**: extração de texto (imagens, PDF escaneado; PDF textual via camada de leitura).
- **Classificador**: infere o tipo de documento a partir do nome do arquivo e do texto.
- **Extratores**: convertem o texto OCR em campos estruturados **sem modelos de IA** (heurísticas / regex — expansível no TCC).
- **Motor de regras**: validações por tipo de documento.

## Estrutura do projeto

```
app/
├── api/                 # Rotas HTTP
├── application/         # Orquestrador + pipeline extração + regras
├── domain/
│   ├── classifier/
│   ├── extraction/      # Parsers determinísticos por tipo
│   ├── ocr/
│   ├── rules_engine/
│   └── entities/
├── infrastructure/    # (opcional: integrações externas)
└── config/
tests/
main.py
```

As regras e os extratores podem ser refinados conforme cada layout real de documento.
