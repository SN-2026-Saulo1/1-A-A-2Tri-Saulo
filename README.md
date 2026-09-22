# Painel SIROS/ANAC + Supabase — versão 2

Projeto da atividade de Serviços em Nuvem. A base foi importada do repositório
SN-2026-GIL/01-06-2026-Anac-Supabase e atualizada conforme o gabarito da
atividade complementar.

## Links

- Painel: https://sn-2026-saulo1.github.io/1-A-A-2Tri-Saulo/
- Repositório: https://github.com/SN-2026-Saulo1/1-A-A-2Tri-Saulo
- Fonte dos voos previstos: https://sas.anac.gov.br/sas/siros_api/
- Fonte histórica: https://sistemas.anac.gov.br/dadosabertos/

## Arquitetura

~~~text
GitHub Actions
  ├─ Pipeline SIROS → Supabase (4 vezes por dia)
  │    └─ scripts/fetch_flights.py
  └─ Importar Histórico ANAC/VRA (mensal e manual)
       └─ scripts/fetch_historico_anac.py
             ↓
Supabase/PostgreSQL
  ├─ aeroportos
  ├─ voos
  ├─ execucoes
  └─ historico_vra
             ↓
GitHub Pages
  └─ index.html consulta a API REST pública com RLS
~~~

## Conteúdo da versão 2

- `sql/setup.sql`: tabelas, constraints de upsert, índices, RLS, políticas,
  permissões, view segura e carga dos 41 aeroportos.
- `scripts/fetch_flights.py`: coleta diária do SIROS, normalização,
  deduplicação, upsert em lotes e log de execução.
- `scripts/fetch_historico_anac.py`: URL atual do VRA, detecção do cabeçalho
  depois da linha “Atualizado em”, compatibilidade de codificação, filtro,
  deduplicação e upsert.
- `.github/workflows/update-flights.yml`: permissões mínimas, concorrência e
  timeout de 10 minutos.
- `.github/workflows/importar-historico.yml`: importação mensal e execução
  manual por `ano_mes`.
- `index.html`: voos, histórico VRA, log do pipeline, paginação, ordenação e
  escape de conteúdo recebido da API.

## Configuração do GitHub

Em **Settings → Secrets and variables → Actions**:

| Tipo | Nome | Valor |
|---|---|---|
| Secret | `SUPABASE_URL` | URL do projeto Supabase |
| Secret | `SUPABASE_SERVICE_KEY` | chave `service_role`; nunca vai no código |
| Variable | `AIRPORTS` | ICAOs separados por vírgula |

O `index.html` contém somente a URL e a chave pública `anon`, próprias para
consultas protegidas por RLS. A chave `service_role` fica apenas nos Secrets.

## Execução

### Pipeline SIROS

~~~bash
pip install requests supabase
SUPABASE_URL=https://SEU-PROJETO.supabase.co \
SUPABASE_SERVICE_KEY=SUA_SERVICE_ROLE \
AIRPORTS=SBCA,SBGR \
python scripts/fetch_flights.py
~~~

### Histórico VRA

~~~bash
SUPABASE_URL=https://SEU-PROJETO.supabase.co \
SUPABASE_SERVICE_KEY=SUA_SERVICE_ROLE \
AIRPORTS=SBCA,SBGR \
ANO_MES=2026-07 \
python scripts/fetch_historico_anac.py
~~~

Sem `ANO_MES`, o importador procura o mês fechado mais recente disponível,
retrocedendo até quatro meses. Com `ANO_MES`, uma ausência no portal é tratada
como erro para impedir um workflow verde sem dados.

## Verificações rápidas

~~~bash
python -m py_compile scripts/fetch_flights.py scripts/fetch_historico_anac.py
python -c "import json; d=json.load(open('data/airports.json', encoding='utf-8')); print(len(d))"
~~~

Os resultados dos testes da entrega ficam em [testes/README.md](testes/README.md).
