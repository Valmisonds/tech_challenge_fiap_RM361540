from flask import Flask, jsonify, request, send_from_directory
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os
from datetime import timedelta
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração do JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'chave-secreta-padrao')  # Ideal usar variável de ambiente
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# URL base do site da Embrapa Vitivinicultura
BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/"

# Mapeamento de opções para as categorias
CATEGORY_OPTIONS = {
    "producao": "opt_02",
    "processamento": "opt_03",
    "comercializacao": "opt_04",
    "importacao": "opt_05",
    "exportacao": "opt_06"
}

# Mapeamento de subcategorias para importação e exportação
SUBCATEGORY_OPTIONS = {
    "importacao": {
        "vinhos": "10",
        "espumantes": "11",
        "uvas_frescas": "12",
        "uvas_passas": "13",
        "suco_uva": "14"
    },
    "exportacao": {
        "vinhos": "10",
        "espumantes": "11",
        "uvas_frescas": "12",
        "suco_uva": "13"
    },
    "processamento": {
        "viniferas": "10",
        "americanas_hibridas": "11",
        "uvas_mesa": "12",
        "sem_classificacao": "13"
    }
}

# Rota para autenticação e obtenção do token JWT
@app.route('/auth', methods=['POST'])
def auth():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    # Verificação simples de usuário e senha (em produção, usar banco de dados)
    if username != 'admin' or password != 'password':
        return jsonify({"msg": "Credenciais inválidas"}), 401
    
    # Criar token de acesso
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Função auxiliar para obter dados do site da Embrapa
def fetch_embrapa_data(category, year=None, subcategory=None):
    """
    Obtém dados do site da Embrapa Vitivinicultura.
    
    Args:
        category (str): Categoria de dados (producao, processamento, comercializacao, importacao, exportacao)
        year (str, optional): Ano dos dados. Se None, usa o ano mais recente disponível.
        subcategory (str, optional): Subcategoria específica dentro da categoria principal.
        
    Returns:
        dict: Dados obtidos do site da Embrapa
    """
    if category not in CATEGORY_OPTIONS:
        return {"error": "Categoria inválida"}
    
    # Construir URL para a categoria
    url = f"{BASE_URL}index.php?opcao={CATEGORY_OPTIONS[category]}"
    
    # Adicionar parâmetros de ano e subcategoria, se fornecidos
    if year:
        url += f"&ano={year}"
    
    # Verificar se a subcategoria é válida para a categoria
    if subcategory and category in SUBCATEGORY_OPTIONS and subcategory in SUBCATEGORY_OPTIONS[category]:
        url += f"&subopcao={SUBCATEGORY_OPTIONS[category][subcategory]}"
    
    try:
        # Fazer requisição ao site da Embrapa
        response = requests.get(url)
        response.raise_for_status()
        
        # Parsear o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extrair título da tabela
        title = "Dados não encontrados"
        
        # Procurar o título em diferentes formatos
        if soup.find('h3'):
            title = soup.find('h3').text.strip()
        elif soup.find('div', class_='conteudo') and soup.find('div', class_='conteudo').find('h3'):
            title = soup.find('div', class_='conteudo').find('h3').text.strip()
        
        # Extrair dados da tabela - procurar em diferentes formatos
        table = None
        if soup.find('table', class_='tabela'):
            table = soup.find('table', class_='tabela')
        else:
            # Tentar encontrar qualquer tabela na página
            tables = soup.find_all('table')
            if tables:
                table = tables[0]  # Usar a primeira tabela encontrada
        
        if not table:
            return {
                "title": title,
                "data": [],
                "message": "Tabela não encontrada",
                "source_url": url
            }
        
        # Extrair cabeçalhos
        headers = []
        header_row = table.find('tr')
        if header_row:
            headers = [th.text.strip() for th in header_row.find_all(['th', 'td'])]
        
        # Se não encontrou cabeçalhos, usar nomes genéricos
        if not headers:
            # Contar o número de colunas na primeira linha
            first_row = table.find('tr')
            if first_row:
                num_cols = len(first_row.find_all('td'))
                headers = [f"Coluna {i+1}" for i in range(num_cols)]
        
        # Extrair linhas de dados
        rows = []
        data_rows = table.find_all('tr')[1:] if headers else table.find_all('tr')  # Pular a linha de cabeçalho se houver
        
        for tr in data_rows:
            cells = tr.find_all('td')
            if cells:  # Verificar se há células na linha
                row = {}
                # Usar o número mínimo entre células e cabeçalhos para evitar erros
                for i in range(min(len(cells), len(headers))):
                    row[headers[i]] = cells[i].text.strip()
                rows.append(row)
        
        return {
            "title": title,
            "headers": headers,
            "data": rows,
            "source_url": url
        }
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro ao acessar o site da Embrapa: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro ao processar os dados: {str(e)}"}

# Rota para obter dados de produção
@app.route('/api/producao', methods=['GET'])
@jwt_required()
def get_producao():
    year = request.args.get('ano')
    return jsonify(fetch_embrapa_data('producao', year))

# Rota para obter dados de processamento
@app.route('/api/processamento', methods=['GET'])
@jwt_required()
def get_processamento():
    year = request.args.get('ano')
    subcategory = request.args.get('subcategoria')
    return jsonify(fetch_embrapa_data('processamento', year, subcategory))

# Rota para obter dados de comercialização
@app.route('/api/comercializacao', methods=['GET'])
@jwt_required()
def get_comercializacao():
    year = request.args.get('ano')
    return jsonify(fetch_embrapa_data('comercializacao', year))

# Rota para obter dados de importação
@app.route('/api/importacao', methods=['GET'])
@jwt_required()
def get_importacao():
    year = request.args.get('ano')
    subcategory = request.args.get('subcategoria')
    return jsonify(fetch_embrapa_data('importacao', year, subcategory))

# Rota para obter dados de exportação
@app.route('/api/exportacao', methods=['GET'])
@jwt_required()
def get_exportacao():
    year = request.args.get('ano')
    subcategory = request.args.get('subcategoria')
    return jsonify(fetch_embrapa_data('exportacao', year, subcategory))

# Rota para listar todas as categorias disponíveis
@app.route('/api/categorias', methods=['GET'])
@jwt_required()
def get_categorias():
    return jsonify({
        "categorias": list(CATEGORY_OPTIONS.keys()),
        "subcategorias": SUBCATEGORY_OPTIONS
    })

# Rota para servir arquivos estáticos da documentação
@app.route('/docs/<path:path>')
def send_docs(path):
    return send_from_directory('docs', path)

# Rota para a documentação da API
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Vitivinicultura - Embrapa</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1000px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #2980b9;
                margin-top: 30px;
            }
            h3 {
                color: #16a085;
            }
            code {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 3px;
                font-family: monospace;
                padding: 2px 5px;
            }
            pre {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 10px;
                overflow-x: auto;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                text-align: left;
                padding: 12px;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            .endpoint {
                margin-bottom: 30px;
                padding: 15px;
                background-color: #f9f9f9;
                border-left: 4px solid #3498db;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                margin-right: 10px;
            }
            .get {
                background-color: #2ecc71;
            }
            .post {
                background-color: #e74c3c;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>API de Vitivinicultura - Embrapa</h1>
            <p>Esta API fornece acesso aos dados de vitivinicultura da Embrapa, disponíveis no site <a href="http://vitibrasil.cnpuv.embrapa.br/" target="_blank">Vitibrasil</a>.</p>
            
            <h2>Autenticação</h2>
            <p>A API utiliza autenticação JWT (JSON Web Token). Para acessar os endpoints protegidos, é necessário obter um token de acesso.</p>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <code>/auth</code>
                <p>Endpoint para autenticação e obtenção do token JWT.</p>
                <h3>Corpo da Requisição:</h3>
                <pre>
{
    "username": "admin",
    "password": "password"
}
                </pre>
                <h3>Resposta:</h3>
                <pre>
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
                </pre>
            </div>
            
            <h2>Endpoints Disponíveis</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/categorias</code>
                <p>Retorna todas as categorias e subcategorias disponíveis na API.</p>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/producao</code>
                <p>Retorna dados de produção de vinhos, sucos e derivados.</p>
                <h3>Parâmetros:</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Tipo</th>
                        <th>Descrição</th>
                    </tr>
                    <tr>
                        <td>ano</td>
                        <td>string</td>
                        <td>Ano dos dados (opcional). Exemplo: 2023</td>
                    </tr>
                </table>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/processamento</code>
                <p>Retorna dados de processamento de uvas.</p>
                <h3>Parâmetros:</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Tipo</th>
                        <th>Descrição</th>
                    </tr>
                    <tr>
                        <td>ano</td>
                        <td>string</td>
                        <td>Ano dos dados (opcional). Exemplo: 2023</td>
                    </tr>
                    <tr>
                        <td>subcategoria</td>
                        <td>string</td>
                        <td>Subcategoria de processamento (opcional). Valores: viniferas, americanas_hibridas, uvas_mesa, sem_classificacao</td>
                    </tr>
                </table>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/comercializacao</code>
                <p>Retorna dados de comercialização de vinhos e derivados.</p>
                <h3>Parâmetros:</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Tipo</th>
                        <th>Descrição</th>
                    </tr>
                    <tr>
                        <td>ano</td>
                        <td>string</td>
                        <td>Ano dos dados (opcional). Exemplo: 2023</td>
                    </tr>
                </table>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/importacao</code>
                <p>Retorna dados de importação de produtos vitivinícolas.</p>
                <h3>Parâmetros:</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Tipo</th>
                        <th>Descrição</th>
                    </tr>
                    <tr>
                        <td>ano</td>
                        <td>string</td>
                        <td>Ano dos dados (opcional). Exemplo: 2023</td>
                    </tr>
                    <tr>
                        <td>subcategoria</td>
                        <td>string</td>
                        <td>Subcategoria de importação (opcional). Valores: vinhos, espumantes, uvas_frescas, uvas_passas, suco_uva</td>
                    </tr>
                </table>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <code>/api/exportacao</code>
                <p>Retorna dados de exportação de produtos vitivinícolas.</p>
                <h3>Parâmetros:</h3>
                <table>
                    <tr>
                        <th>Parâmetro</th>
                        <th>Tipo</th>
                        <th>Descrição</th>
                    </tr>
                    <tr>
                        <td>ano</td>
                        <td>string</td>
                        <td>Ano dos dados (opcional). Exemplo: 2023</td>
                    </tr>
                    <tr>
                        <td>subcategoria</td>
                        <td>string</td>
                        <td>Subcategoria de exportação (opcional). Valores: vinhos, espumantes, uvas_frescas, suco_uva</td>
                    </tr>
                </table>
                <h3>Cabeçalhos:</h3>
                <pre>
Authorization: Bearer {seu_token_jwt}
                </pre>
            </div>
            
            <h2>Exemplo de Uso</h2>
            <p>Exemplo de como usar a API com curl:</p>
            <pre>
# Obter token de autenticação
curl -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"password"}' http://localhost:5000/auth

# Usar o token para acessar dados de produção
curl -X GET -H "Authorization: Bearer {seu_token_jwt}" http://localhost:5000/api/producao?ano=2023
            </pre>
            
            <h2>Plano de Arquitetura</h2>
            <p>Esta API foi projetada para servir como fonte de dados para um modelo de Machine Learning. A arquitetura completa inclui:</p>
            <ol>
                <li><strong>Ingestão de Dados:</strong> API REST que consulta o site da Embrapa</li>
                <li><strong>Armazenamento:</strong> Banco de dados para persistência dos dados coletados</li>
                <li><strong>Processamento:</strong> ETL para transformação e preparação dos dados</li>
                <li><strong>Análise:</strong> Modelo de ML para análise preditiva</li>
                <li><strong>Visualização:</strong> Dashboard para apresentação dos resultados</li>
            </ol>
            
            <h2>Contato</h2>
            <p>Para mais informações, entre em contato com a equipe de desenvolvimento.</p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    # Criar diretório para documentação se não existir
    os.makedirs('docs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
