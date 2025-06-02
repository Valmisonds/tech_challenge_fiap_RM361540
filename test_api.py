import requests
import json

def test_api():
    """
    Testa os endpoints da API de Vitivinicultura.
    """
    base_url = "http://localhost:5000"
    
    print("Testando API de Vitivinicultura...")
    
    # Teste de autenticação
    print("\n1. Testando autenticação...")
    auth_response = requests.post(
        f"{base_url}/auth",
        json={"username": "admin", "password": "password"}
    )
    
    if auth_response.status_code == 200:
        print("✅ Autenticação bem-sucedida!")
        token = auth_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Teste de categorias
        print("\n2. Testando endpoint de categorias...")
        categorias_response = requests.get(f"{base_url}/api/categorias", headers=headers)
        if categorias_response.status_code == 200:
            print("✅ Endpoint de categorias funcionando!")
            print(f"   Categorias disponíveis: {', '.join(categorias_response.json().get('categorias', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de categorias: {categorias_response.status_code}")
            print(categorias_response.text)
        
        # Teste de produção
        print("\n3. Testando endpoint de produção...")
        producao_response = requests.get(f"{base_url}/api/producao", headers=headers)
        if producao_response.status_code == 200:
            print("✅ Endpoint de produção funcionando!")
            data = producao_response.json()
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Número de registros: {len(data.get('data', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de produção: {producao_response.status_code}")
            print(producao_response.text)
        
        # Teste de processamento
        print("\n4. Testando endpoint de processamento...")
        processamento_response = requests.get(
            f"{base_url}/api/processamento?subcategoria=viniferas", 
            headers=headers
        )
        if processamento_response.status_code == 200:
            print("✅ Endpoint de processamento funcionando!")
            data = processamento_response.json()
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Número de registros: {len(data.get('data', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de processamento: {processamento_response.status_code}")
            print(processamento_response.text)
        
        # Teste de comercialização
        print("\n5. Testando endpoint de comercialização...")
        comercializacao_response = requests.get(f"{base_url}/api/comercializacao", headers=headers)
        if comercializacao_response.status_code == 200:
            print("✅ Endpoint de comercialização funcionando!")
            data = comercializacao_response.json()
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Número de registros: {len(data.get('data', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de comercialização: {comercializacao_response.status_code}")
            print(comercializacao_response.text)
        
        # Teste de importação
        print("\n6. Testando endpoint de importação...")
        importacao_response = requests.get(
            f"{base_url}/api/importacao?subcategoria=vinhos", 
            headers=headers
        )
        if importacao_response.status_code == 200:
            print("✅ Endpoint de importação funcionando!")
            data = importacao_response.json()
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Número de registros: {len(data.get('data', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de importação: {importacao_response.status_code}")
            print(importacao_response.text)
        
        # Teste de exportação
        print("\n7. Testando endpoint de exportação...")
        exportacao_response = requests.get(
            f"{base_url}/api/exportacao?subcategoria=vinhos", 
            headers=headers
        )
        if exportacao_response.status_code == 200:
            print("✅ Endpoint de exportação funcionando!")
            data = exportacao_response.json()
            print(f"   Título: {data.get('title', 'N/A')}")
            print(f"   Número de registros: {len(data.get('data', []))}")
        else:
            print(f"❌ Erro ao acessar endpoint de exportação: {exportacao_response.status_code}")
            print(exportacao_response.text)
        
        print("\nTestes concluídos!")
    else:
        print(f"❌ Erro na autenticação: {auth_response.status_code}")
        print(auth_response.text)

if __name__ == "__main__":
    test_api()
