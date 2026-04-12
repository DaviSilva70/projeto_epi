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

- **Backend**: Django 5.x
- **Frontend**: Bootstrap 5, Font Awesome 6
- **PDF**: xhtml2pdf
- **Banco de dados**: SQLite3

## Como rodar

```bash
cd H:\Projeto_EPI_IURD
venv\Scripts\python.exe manage.py runserver
```

Acesse: http://127.0.0.1:8000

## Estrutura do projeto

```
projetoepi/
├── epi/
│   ├── models.py       # Modelos (EPI, Colaborador, RegistroEPI)
│   ├── views.py        # Views (cadastro, busca, PDF)
│   ├── forms.py        # Formulários
│   ├── urls.py         # Rotas
│   └── admin.py        # Admin Django
├── templates/          # Templates HTML
│   ├── base.html       # Template base
│   ├── home.html       # Página inicial
│   └── ...
├── media/              # Arquivos de mídia (fotos)
├── manage.py
└── requirements.txt    # Dependências
```

## Requisitos

- Python 3.13+
- Django 5.x
- xhtml2pdf
- Pillow

## Screenshots

O sistema conta com:
- Interface moderna com gradientes e animações
- Cards interativos na página inicial
- Estatísticas em tempo real
- Design responsivo para mobile e desktop
- **PDF profissional** com layout otimizado para A4:
  - Cabeçalho com logo e informações da IURD
  - Cards de dados do colaborador
  - Tabela estilizada com badges visuais
  - Rodapé com data de emissão
  - Marca d'água sutil
  - Suporte completo para impressão
