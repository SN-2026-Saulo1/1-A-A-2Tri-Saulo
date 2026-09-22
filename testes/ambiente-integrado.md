# Evidências — Ambiente de Desenvolvimento Integrado com IA

Data da validação: 22/09/2026  
Repositório: https://github.com/SN-2026-Saulo1/1-A-A-2Tri-Saulo  
Painel publicado: https://sn-2026-saulo1.github.io/1-A-A-2Tri-Saulo/

## Trilhas configuradas

### A — GitHub Copilot Free

- A página de configurações da conta mostra **GitHub Copilot Free**.
- Uso verificado em 22/09/2026: 0% de sugestões inline e 0% de créditos incluídos.
- Recursos Copilot Chat no GitHub.com e Copilot CLI aparecem como habilitados.
- A autenticação do GitHub CLI foi concluída para a conta `Sauloopf`.

### E — Continue.dev com Groq

- A extensão `continue.continue` foi instalada no VS Code.
- O arquivo local `%USERPROFILE%/.continue/config.yaml` usa `provider: groq`.
- A credencial é referenciada como `${{ secrets.GROQ_API_KEY }}`; nenhum segredo foi incluído no repositório.
- Dois perfis foram configurados: `Groq GPT-OSS 20B` (chat, edit e apply) e `Groq GPT-OSS 20B Autocomplete`.
- A chamada autenticada ao endpoint oficial da Groq retornou `OK` usando `openai/gpt-oss-20b`.

## Ferramentas e extensões verificadas

```text
VS Code 1.138.0 (x64)
continue.continue
github.vscode-pull-request-github
maattdd.gitless
ms-ceintl.vscode-language-pack-pt-br

gh version 2.101.0
github.com: Logged in as Sauloopf
Organização: SN-2026-Saulo1
```

`GitHub.copilot` e `GitHub.copilot-chat` são extensões internas da versão instalada do VS Code; por isso não aparecem em `code --list-extensions`.

## Validações do projeto

```text
Python 3.12.14
scripts/fetch_flights.py: sem erros de sintaxe
deduplicar(): localizada e utilizada
sys.exit(1): 4 ocorrências

Estruturas SQL verificadas: 23
ROW LEVEL SECURITY e GRANT SELECT/GRANT ALL: presentes

index.html: innerHTML = 15; escapeHtml = 24
Workflow: permissions, concurrency e timeout-minutes presentes
data/airports.json: 65 aeroportos; SBCA, SBCT, SBGR, SBSP, SBGL, SBBR, SBFL e SBPA presentes
```

## Publicação

O painel foi validado em GitHub Pages. A execução mais recente de publicação de páginas está concluída com sucesso. As execuções manuais dos pipelines SIROS e VRA permanecem em fila no GitHub Actions e serão acompanhadas separadamente.
