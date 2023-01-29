# Resource Management API
API REST de gerenciamento de recursos

## Instalação
1. Após clonar o projeto, crie um arquivo .env a partir do arquivo .env-example bem como adicione as váriáveis de ambiente que faltam (você pode gerar a SECRET_KEY por esse site https://djecrety.ir/):
```
cp .env-example .env
```
2. Suba os containers do Docker:
```
docker-compose up -d --build
```
3. Rode os testes e o flake8 para ver se tudo está ok:
```
docker-compose exec web python manage.py test && flake8
```
4. Crie um super usuário:
```
docker-compose exec web python manage.py createsuperuser
```
5. Teste a instalação acessando o servidor de desenvolvimento, a documentação da API está disponível em http://127.0.0.1:8000/documentation/.

### VSCode
Caso use o Visual Studio Code e tenha versão 3.10.2 do Python instalada no seu sistema operacional, você pode integrar a ele as bibliotecas Flake8 e AutoPEP8 com os seguintes passos abaixo.
1. Na pasta do projeto, crie um ambiente virtual:
```
python3 -m venv venv
```
2. Ative o ambiente virtual:
```
source venv/bin/activate
```
3. Instale as dependências:
```
(venv) pip install -r requirements.txt
```
4. Por fim, abra um arquivo com a extensão .py no VSCode e selecione o interpretador do Python do ambiente virtal criado (está disponível no diretório ./venv/bin/python).
**Você também precisa ter as extensões do Python instaladas.**
