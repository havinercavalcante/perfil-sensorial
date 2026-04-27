# CeciSys - Sistema Django

Sistema para aplicação e análise do questionário **Criança CeciSys** (3 a 14 anos e 11 meses).

## Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Criar banco de dados
```bash
python manage.py migrate
```

### 3. Criar usuário admin (opcional)
```bash
python manage.py createsuperuser
```

### 4. Iniciar servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Funcionalidades

- **Cadastro de pacientes** com dados do responsável e terapeuta
- **Questionário multi-página** com 9 seções (86 itens no total):
  - Processamento Auditivo
  - Processamento Visual
  - Processamento do Tato
  - Processamento de Movimentos
  - Posição do Corpo
  - Sensibilidade Oral
  - Conduta
  - Respostas Socioemocionais
  - Respostas de Atenção
- **Pontuação automática** por seção e por quadrante (EX, EV, SN, OB)
- **Dashboard visual** com:
  - Gráfico radar por seção sensorial
  - Gráfico de barras por quadrante
  - Classificação: Muito menos / Menos / Típico / Mais / Muito mais
  - Barras de progresso por seção
- **Histórico** de avaliações por paciente
- **Painel admin** em /admin/

## Estrutura dos Quadrantes

| Sigla | Nome | Subtítulo |
|-------|------|-----------|
| EX | Exploração | Criança exploradora |
| EV | Esquiva | Criança que se esquiva |
| SN | Sensibilidade | Criança sensível |
| OB | Observação | Criança observadora |
