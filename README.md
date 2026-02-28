# Chatbot Corporativo - ICT Itaú

## Descrição

Protótipo de chatbot corporativo para atendimento interno, utilizando arquitetura baseada em RAG (Retrieval-Augmented Generation).

O sistema foi projetado para:

- Responder dúvidas sobre políticas internas
- Reduzir tickets de baixa complexidade
- Oferecer rastreabilidade e governança
- Permitir evolução incremental

---

## Arquitetura Simplificada

- FastAPI (backend)
- Base documental local
- Camada de embeddings e busca vetorial (ChromaDB)
- Integração opcional com OpenAI via variável de ambiente
- Modo fallback (mock) caso não exista chave de API configurada

---

## Diagrama de Arquitetura (Simplificado)

Usuário  
   ↓  
FastAPI (/chat)  
   ↓  
Camada RAG  
   ├─ Embeddings (Local ou OpenAI)  
   ├─ ChromaDB (Base Vetorial Persistente)  
   ↓  
Geração de Resposta  
   ├─ Modo Local (sem API)  
   └─ Modo LLM (com API Key)

Persistência: .chroma/
Logs estruturados via logging padrão Python

---

## Estrutura da API

### Endpoint de Saúde

GET /

Retorna status do serviço.

### Endpoint de Chat

POST /chat

#### Payload esperado

{
  "question": "Como solicitar férias?"
}

#### Exemplo de Resposta (modo mock)

{
  "answer": "Resposta simulada para a pergunta...",
  "source": "mock",
  "mode": "mock"
}

---

## Execução Local

Instalar dependências:

pip install -r requirements.txt

Executar servidor:

uvicorn src.app:app --reload

Acessar documentação automática:

http://127.0.0.1:8000/docs

---

## Variáveis de Ambiente

Para ativar integração real com OpenAI:

Criar arquivo `.env` com:

OPENAI_API_KEY=sua_chave_aqui

Caso a chave não esteja configurada, o sistema opera em modo mock.

---

## Estrutura do Projeto

chatbot-corporativo-ict-itau/
│
├── requirements.txt
├── README.md
│
├── src/
│   └── app.py
│
├── data/
│   └── base_exemplo.txt
│
└── tests/

---

## Observação

Este projeto representa um MVP técnico estruturado para validação de arquitetura, governança e viabilidade de uso corporativo.

---

## Logs

O sistema registra:

- Perguntas recebidas
- Modo de execução (local ou LLM)
- Erros de integração
- Falhas de indexação

Formato estruturado com timestamp e nível de severidade.

---

## Testes Técnicos

Arquivo: tests/test_load.py

Permite simular múltiplas requisições ao endpoint /chat
para avaliação de latência e estabilidade.

Execução:

python tests/test_load.py

---

## Governança e Riscos

Este protótipo considera:

- Mitigação de alucinação via RAG restrito ao contexto
- Operação em modo local caso LLM esteja indisponível
- Logs estruturados para auditoria
- Separação entre código e credenciais
- Arquitetura modular para troca de provedor LLM

Não utiliza dados sensíveis no MVP.

---

## Checklist de Entrega

✔ Arquitetura RAG implementada  
✔ Busca vetorial com persistência  
✔ Embeddings locais ou OpenAI  
✔ API REST documentada  
✔ Logs estruturados  
✔ Teste simples de carga  
✔ Configuração via variável de ambiente  
✔ Governança básica considerada  

Projeto estruturado para evolução incremental.