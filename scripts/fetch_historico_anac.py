"""Importa o histórico mensal VRA/ANAC para o Supabase.

Trata o caminho atual do portal, a linha ``Atualizado em:`` antes do
cabeçalho e pequenas variações de nomes de coluna.
"""

from __future__ import annotations

import csv
import io
import os
import sys
import unicodedata
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
AIRPORTS = {a.strip().upper() for a in os.environ.get("AIRPORTS", "SBCA").split(",") if a.strip()}
LOTE = 500
BRT = ZoneInfo("America/Sao_Paulo")
MESES = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}


def falhar(mensagem: str) -> None:
    print(f"[ERRO CRÍTICO] {mensagem}")
    raise SystemExit(1)


def validar_configuracao() -> None:
    if not SUPABASE_URL or not SUPABASE_KEY:
        falhar("SUPABASE_URL e SUPABASE_SERVICE_KEY são obrigatórios.")
    invalidos = sorted(a for a in AIRPORTS if len(a) != 4)
    if not AIRPORTS or invalidos:
        falhar(f"AIRPORTS inválido: {', '.join(invalidos) or 'vazio'}")


def chave(valor: str) -> str:
    valor = unicodedata.normalize("NFKD", valor or "")
    sem_acentos = "".join(c for c in valor if not unicodedata.combining(c))
    return " ".join(sem_acentos.replace("_", " ").lower().split())


ALIASES = {
    "empresa": ("icao empresa aerea", "empresa sigla", "sg empresa icao"),
    "voo": ("numero voo", "nr voo"),
    "origem": ("icao aerodromo origem", "origem", "sg icao origem"),
    "destino": ("icao aerodromo destino", "destino", "sg icao destino"),
    "partida_prev": ("partida prevista", "dt partida prevista"),
    "partida_real": ("partida real", "dt partida real"),
    "chegada_prev": ("chegada prevista", "dt chegada prevista"),
    "chegada_real": ("chegada real", "dt chegada real"),
    "situacao": ("situacao voo", "situacao"),
    "motivo": ("codigo justificativa", "motivo", "motivo alteracao"),
}


def valor(row: dict[str, str], campo: str) -> str:
    dados = {chave(k): (v or "").strip() for k, v in row.items()}
    return next((dados[n] for n in ALIASES[campo] if n in dados), "")


def periodo_anterior(referencia: date, meses: int) -> str:
    primeiro = referencia.replace(day=1)
    for _ in range(meses):
        primeiro = (primeiro - timedelta(days=1)).replace(day=1)
    return primeiro.strftime("%Y-%m")


def periodos_candidatos() -> list[str]:
    solicitado = os.environ.get("ANO_MES", "").strip()
    if solicitado:
        try:
            datetime.strptime(solicitado, "%Y-%m")
        except ValueError:
            falhar("ANO_MES deve usar o formato AAAA-MM.")
        return [solicitado]
    hoje = datetime.now(BRT).date()
    return [periodo_anterior(hoje, atraso) for atraso in range(1, 5)]


def url_vra(ano_mes: str) -> str:
    ano, mes_txt = ano_mes.split("-")
    mes = int(mes_txt)
    pasta = requests.utils.quote(f"{mes:02d} - {MESES[mes]}")
    return (
        "https://sistemas.anac.gov.br/dadosabertos/"
        "Voos%20e%20opera%C3%A7%C3%B5es%20a%C3%A9reas/"
        f"Voo%20Regular%20Ativo%20%28VRA%29/{ano}/{pasta}/VRA_{ano}{mes}.csv"
    )


def decodificar(conteudo: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return conteudo.decode(encoding)
        except UnicodeDecodeError:
            pass
    return conteudo.decode("utf-8", errors="replace")


def baixar_vra() -> tuple[str, list[dict[str, str]]]:
    solicitado = bool(os.environ.get("ANO_MES", "").strip())
    for ano_mes in periodos_candidatos():
        url = url_vra(ano_mes)
        print(f"GET {url}")
        try:
            resposta = requests.get(url, timeout=180)
        except requests.RequestException as exc:
            if solicitado:
                falhar(f"Falha ao baixar {ano_mes}: {exc}")
            print(f"  Indisponível: {exc}")
            continue
        if resposta.status_code == 404:
            print(f"  VRA de {ano_mes} ainda não publicado (HTTP 404).")
            if solicitado:
                falhar(f"O VRA solicitado ({ano_mes}) não está disponível.")
            continue
        try:
            resposta.raise_for_status()
        except requests.RequestException as exc:
            falhar(f"Portal ANAC respondeu com erro: {exc}")

        linhas = decodificar(resposta.content).splitlines()
        if linhas and linhas[0].lstrip("\ufeff").lower().startswith("atualizado em:"):
            print(f"  {linhas.pop(0).lstrip(chr(0xfeff))}")
        reader = csv.DictReader(io.StringIO("\n".join(linhas)), delimiter=";")
        registros = list(reader)
        if not reader.fieldnames or not registros:
            falhar(f"O VRA de {ano_mes} não contém registros válidos.")
        print(f"  VRA carregado: {len(registros)} linhas brutas")
        print(f"  Cabeçalho detectado: {', '.join(reader.fieldnames)}")
        return ano_mes, registros
    falhar("Nenhum dos últimos quatro meses fechados está disponível no portal ANAC.")


FORMATOS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M")


def parse_data(texto: str) -> datetime | None:
    for formato in FORMATOS:
        try:
            return datetime.strptime(texto.strip(), formato).replace(tzinfo=BRT)
        except (ValueError, AttributeError):
            pass
    return None


def minutos(previsto: datetime | None, real: datetime | None) -> int | None:
    return round((real - previsto).total_seconds() / 60) if previsto and real else None


def processar(ano_mes: str, linhas: list[dict[str, str]]) -> list[dict]:
    resultado = []
    descartados = 0
    for row in linhas:
        origem, destino = valor(row, "origem").upper(), valor(row, "destino").upper()
        if origem not in AIRPORTS and destino not in AIRPORTS:
            continue
        empresa, nr_voo = valor(row, "empresa").upper(), valor(row, "voo")
        pp, pr = parse_data(valor(row, "partida_prev")), parse_data(valor(row, "partida_real"))
        cp, cr = parse_data(valor(row, "chegada_prev")), parse_data(valor(row, "chegada_real"))
        referencia = pp or cp or pr or cr
        if not empresa or not nr_voo or not origem or not destino or not referencia:
            descartados += 1
            continue
        resultado.append({
            "ano_mes": ano_mes, "icao_empresa": empresa, "nr_voo": nr_voo,
            "icao_origem": origem, "icao_destino": destino,
            "dt_referencia": referencia.date().isoformat(),
            "partida_real": pr.isoformat() if pr else None,
            "chegada_real": cr.isoformat() if cr else None,
            "atraso_partida": minutos(pp, pr), "atraso_chegada": minutos(cp, cr),
            "situacao": valor(row, "situacao").lower() or None,
            "motivo_alteracao": valor(row, "motivo") or None,
        })
    campos = ("ano_mes", "icao_empresa", "nr_voo", "icao_origem", "icao_destino", "dt_referencia")
    unicos = {tuple(r[c] for c in campos): r for r in resultado}
    print(f"  Registros filtrados: {len(resultado)}")
    print(f"  Registros inválidos descartados: {descartados}")
    print(f"  Duplicados removidos: {len(resultado) - len(unicos)}")
    return list(unicos.values())


def main() -> None:
    validar_configuracao()
    db = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"Supabase conectado: {SUPABASE_URL}")
    print(f"Aeroportos filtrados: {', '.join(sorted(AIRPORTS))}")
    ano_mes, linhas = baixar_vra()
    print(f"Período histórico selecionado: {ano_mes}")
    registros = processar(ano_mes, linhas)
    if not registros:
        falhar("Nenhum registro corresponde aos aeroportos configurados.")
    processados = erros = 0
    for inicio in range(0, len(registros), LOTE):
        lote = registros[inicio:inicio + LOTE]
        numero = inicio // LOTE + 1
        try:
            db.table("historico_vra").upsert(lote, on_conflict="ano_mes,icao_empresa,nr_voo,icao_origem,icao_destino,dt_referencia").execute()
            processados += len(lote)
            print(f"  Lote {numero}: {len(lote)} registros enviados/processados")
        except Exception as exc:
            erros += 1
            print(f"  [ERRO] Lote {numero}: {exc}")
    print(f"Concluído — {processados} registros históricos enviados/processados.")
    if erros:
        falhar(f"{erros} lote(s) falharam durante o upsert.")


if __name__ == "__main__":
    main()
