# Projeto 2 de Sistemas Distribuídos

Para iniciar os containers que simularão as entidades do processo fabril, execute:
```bash
docker compose -f docker-compose.yml up -d
```

Então, para visualizar o monitoramento dos estoques, instale as dependências do projeto:
```bash
pip install -r requirements.txt
```
 e execute em um terminal:
```bash
python run.py
```