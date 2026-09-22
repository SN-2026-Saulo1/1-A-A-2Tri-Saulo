# Evidências de testes — atividade complementar SIROS/ANAC

Data da validação: 22/09/2026.

## Testes locais dos coletores

| Verificação | Resultado |
| --- | --- |
| Compilação de `fetch_flights.py` e `fetch_historico_anac.py` | Aprovada |
| Consulta à API SIROS em 22/09/2026 | HTTP 200; 3.005 registros retornados |
| Filtro SIROS para `SBCA,SBGR` | 819 voos após deduplicação |
| Arquivo VRA de julho/2026 | HTTP 200; cabeçalho após a linha `Atualizado em` reconhecido |
| Leitura do VRA com amostra de 50.000 linhas | 10.908 registros únicos prontos para upsert após filtro dos aeroportos |

## Teste publicado do painel

Painel validado em [GitHub Pages](https://sn-2026-saulo1.github.io/1-A-A-2Tri-Saulo/?v=366aa1b):

- Estado: Paraná; município: Cascavel; aeroporto: SBCA.
- Data: 06/07/2026.
- Resultado: **5 chegadas** e **5 partidas**, com companhia, aeronave, assentos e origem/destino preenchidos.
- A lista de aeroportos carregou pelo Supabase sem o erro `Failed to fetch`.

## Execuções GitHub Actions

As execuções manuais foram solicitadas após a atualização dos secrets e da variável `AIRPORTS`:

- [Pipeline SIROS → Supabase — execução #250](https://github.com/SN-2026-Saulo1/1-A-A-2Tri-Saulo/actions/runs/35746919324)
- [Importar Histórico ANAC/VRA — execução #5, período 2026-07](https://github.com/SN-2026-Saulo1/1-A-A-2Tri-Saulo/actions/runs/35746948786)

Os dois links preservam o log completo e permitem verificar a execução no GitHub. O workflow SIROS registra o resultado em `execucoes`; o workflow VRA popula `historico_vra`.
