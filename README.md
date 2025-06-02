# API de Vitivinicultura - Embrapa

Este projeto implementa uma API REST em Flask para consulta de dados de vitivinicultura da Embrapa, disponíveis no site [Vitibrasil](http://vitibrasil.cnpuv.embrapa.br/).

## Funcionalidades

A API permite consultar dados das seguintes categorias:

- Produção
- Processamento
- Comercialização
- Importação
- Exportação

## Requisitos

- Python 3.10+
- Flask
- Flask-JWT-Extended
- Requests
- BeautifulSoup4
- Python-dotenv

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/api-vitivinicultura.git
cd api-vitivinicultura
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```
cp .env.example .env
```
Edite o arquivo `.env` com suas configurações.

## Execução

Para iniciar a API localmente:

```
python app.py
```

A API estará disponível em `http://localhost:5000`.

## Docker

Para executar a API usando Docker:

```
docker-compose up -d
```

## Autenticação

A API utiliza autenticação JWT. Para obter um token de acesso:

```
curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}' http://localhost:5000/auth
```

## Endpoints

### Autenticação

- `POST /auth`: Obtém um token JWT

### Dados

- `GET /api/categorias`: Lista todas as categorias e subcategorias disponíveis
- `GET /api/producao`: Dados de produção de vinhos, sucos e derivados
- `GET /api/processamento`: Dados de processamento de uvas
- `GET /api/comercializacao`: Dados de comercialização de vinhos e derivados
- `GET /api/importacao`: Dados de importação de produtos vitivinícolas
- `GET /api/exportacao`: Dados de exportação de produtos vitivinícolas

## Documentação

A documentação completa da API está disponível na rota raiz (`/`).

## Arquitetura

A arquitetura completa do projeto está descrita no arquivo [arquitetura.md](arquitetura.md).

## Testes

Para executar os testes da API:

```
python test_api.py
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

## Licença

Este projeto está licenciado sob a licença MIT.
