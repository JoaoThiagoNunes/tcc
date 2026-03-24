# Pre Analysis Service

Serviço de pré-análise de documentos usando IA, construído com FastAPI seguindo arquitetura em camadas.

## 📁 Estrutura do Projeto

```
pre_analysis_service/
│
├── app/
│   ├── main.py                  # Inicialização da API
│   ├── api/                      # Camada de entrada (controllers)
│   ├── application/              # Orquestração
│   ├── domain/                   # Lógica de negócio
│   │   ├── classifier/          # Classificação de documentos
│   │   ├── ocr/                 # Extração de texto
│   │   ├── ia_modules/          # Módulos de IA por tipo
│   │   ├── rules_engine/        # Motor de regras
│   │   └── entities/            # Entidades de domínio
│   ├── infrastructure/          # Infraestrutura
│   │   ├── database/            # Modelos e repositórios
│   │   ├── logging/             # Sistema de logs
│   │   └── external/            # Serviços externos
│   └── config/                  # Configurações
│
├── tests/                       # Testes
├── docker/                      # Configuração Docker
└── logs/                        # Logs da aplicação
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Tesseract OCR (para extração de texto)

### Instalação Local

1. Clone o repositório
2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente (crie um arquivo `.env`):
```env
OPENAI_API_KEY=your_api_key_here
DEBUG=false
DATABASE_URL=sqlite:///./pre_analysis.db
LOG_LEVEL=INFO
```

5. Execute a aplicação:
```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

## 🐳 Docker

### Build e execução com Docker Compose

```bash
docker-compose -f docker/docker-compose.yml up --build
```

## 📚 Documentação da API

Após iniciar a aplicação, acesse:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testes

Execute os testes com:

```bash
pytest tests/
```

## 📋 Funcionalidades

- **Classificação de Documentos**: Identifica automaticamente o tipo de documento
- **OCR**: Extração de texto de imagens e PDFs
- **Análise com IA**: Análise estruturada usando OpenAI
- **Validação por Regras**: Aplicação de regras de negócio
- **Pipeline Completo**: Orquestração de todo o fluxo de análise

## 🔧 Configuração

As configurações podem ser ajustadas em:
- `app/config/settings.py` - Configurações principais
- `.env` - Variáveis de ambiente
- `app/config/constants.py` - Constantes da aplicação

## 📝 Tipos de Documentos Suportados

- Nota Fiscal
- Comprovante de Pagamento
- Consulta CNPJ

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
