# Sistema de Controle de EPI 

Sistema Django para gerenciamento de Equipamentos de Proteção Individual (EPI) para a Igreja Universal do Reino de Deus.

## Funcionalidades

1. **Cadastrar EPI**
   - CA (Certificado de Aprovação)
   - Descrição completa
   - Foto do EPI
   - Busca por CA ou descrição

2. **Cadastrar Colaborador**
   - Nome completo
   - Matrícula
   - Função
   - Setor
   - Edição e exclusão de colaboradores

3. **Registrar Retirada**
   - Relaciona colaborador ao EPI
   - Define quantidade
   - Histórico completo de retiradas

4. **Buscar EPIs por Matrícula**
   - Consulta os EPIsRETIRADOS POR UM COLABORADOR
   - Visualização detalhada

5. **Download PDF**
   - Gera relatório em PDF dos EPIs do colaborador

## Tecnologias

- **Backend**: Django 6.0.3
- **Frontend**: Bootstrap 5, Font Awesome 6
- **PDF**: xhtml2pdf
- **Banco de dados**: MySQL 9.x (configurável via variáveis de ambiente)

## Como rodar

```bash
cd H:\Projeto_EPI_IURD
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Configuração de ambiente

O projeto utiliza variáveis de ambiente para configuração. Crie um arquivo `.env` na raiz do projeto:

```env
DEBUG=True
DJANGO_SECRET_KEY=sua-chave-secreta
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados MySQL
DB_ENGINE=mysql
DB_NAME=universal_epi
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306

# Configurações adicionais
ALLOW_SELF_REGISTRATION=True
LIST_PAGE_SIZE=10
```

Para produção, defina:

```env
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Estrutura do projeto

```
projetoepi/
├── epi/
│   ├── models.py       # Modelos (EPI, Colaborador, RegistroEPI)
│   ├── views.py        # Views (cadastro, busca, PDF)
│   ├── forms.py        # Formulários
│   ├── urls.py         # Rotas
│   ├── admin.py        # Admin Django
│   └── context_processors.py  # Variáveis globais
├── templates/          # Templates HTML
│   ├── base.html       # Template base
│   ├── home.html       # Página inicial
│   ├── login.html      # Login
│   └── ...
├── projetoepi/         # Configurações Django
│   ├── settings.py     # Configurações principais
│   └── urls.py         # URLs globais
├── media/              # Arquivos de mídia (fotos)
├── .env               # Variáveis de ambiente
├── manage.py
└── requirements.txt    # Dependências
```

## Dependências

```
Django==6.0.3
Pillow==12.2.0
xhtml2pdf==0.2.17
reportlab==4.4.10
PyMySQL==1.1.0
python-dotenv==1.0.0
```

## Requisitos

- Python 3.13+
- MySQL Server 8.0+ (ou superior)
- Django 6.x

## Screenshots

O sistema conta com:
- Interface moderna com gradientes e animações
- Cards interativos na página inicial
- Estatísticas em tempo real
- Design responsivo para mobile e desktop
- **PDF profissional** com layout otimizado para A4:
  - Cabeçalho com logo e informações.
  - Cards de dados do colaborador
  - Tabela estilizada com badges visuais
  - Rodapé com data de emissão
  - Marca d'água sutil
  - Suporte completo para impressão
