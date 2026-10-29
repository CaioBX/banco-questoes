"""Confere os arquivos de questões antes de publicar.

Uso:  python3 ferramentas/validar.py
Mostra erros (que quebram o app) e um resumo por ano, eixo e tipo.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "dados"
DIFICULDADES = {"fácil", "média", "difícil"}
TIPOS = {"objetiva", "discursiva"}
LETRAS = "ABCDE"


def validar(arquivo: Path) -> int:
    erros = 0
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ {arquivo.name}: JSON inválido na linha {e.lineno}, coluna {e.colno}: {e.msg}")
        return 1

    def erro(qid, msg):
        nonlocal erros
        erros += 1
        print(f"✗ {arquivo.name} · {qid}: {msg}")

    eixos = set(dados.get("eixos", []))
    textos = dados.get("textos", {})
    prefixo = dados.get("prefixo", "")
    ids = Counter()

    for q in dados.get("questoes", []):
        qid = q.get("id", "(sem id)")
        ids[qid] += 1
        for campo in ("id", "ano", "eixo", "assunto", "dificuldade", "tipo", "enunciado", "comentario"):
            if not q.get(campo):
                erro(qid, f"campo obrigatório vazio: {campo}")
        if prefixo and not qid.startswith(prefixo + "-"):
            erro(qid, f"id deveria começar com {prefixo}-")
        if q.get("ano") not in range(1, 10):
            erro(qid, "ano deve ser um número de 1 a 9")
        if eixos and q.get("eixo") not in eixos:
            erro(qid, f"eixo “{q.get('eixo')}” não está na lista de eixos do arquivo")
        if q.get("dificuldade") not in DIFICULDADES:
            erro(qid, "dificuldade deve ser fácil, média ou difícil")
        if q.get("tipo") not in TIPOS:
            erro(qid, "tipo deve ser objetiva ou discursiva")
        if q.get("texto") and q["texto"] not in textos:
            erro(qid, f"texto {q['texto']} não existe em “textos”")
        if q.get("tipo") == "objetiva":
            alts = q.get("alternativas", [])
            if not 2 <= len(alts) <= 5:
                erro(qid, "objetiva precisa de 2 a 5 alternativas")
            if len(set(alts)) != len(alts):
                erro(qid, "há alternativas repetidas")
            gab = q.get("gabarito", "")
            if gab not in LETRAS[: len(alts)]:
                erro(qid, f"gabarito “{gab}” não corresponde a nenhuma alternativa")
            for ref in re.findall(r"\{([A-Z])\}", q.get("comentario", "")):
                if ref not in LETRAS[: len(alts)]:
                    erro(qid, f"comentário cita a alternativa {{{ref}}}, que não existe")
        if q.get("tipo") == "discursiva" and not q.get("resposta_esperada"):
            erro(qid, "discursiva precisa de resposta_esperada")
        tab = q.get("tabela")
        if tab:
            n = len(tab.get("cabecalho", []))
            if any(len(l) != n for l in tab.get("linhas", [])):
                erro(qid, "tabela com linhas de tamanho diferente do cabeçalho")

    for qid, n in ids.items():
        if n > 1:
            erro(qid, f"id repetido {n} vezes")

    qs = dados.get("questoes", [])
    print(f"\n{dados.get('disciplina')}: {len(qs)} questões, {len(textos)} textos-base")
    print("  por ano:  " + ", ".join(f"{a}º={n}" for a, n in sorted(Counter(q['ano'] for q in qs).items())))
    print("  por eixo: " + ", ".join(f"{e}={n}" for e, n in Counter(q['eixo'] for q in qs).most_common()))
    print("  por tipo: " + ", ".join(f"{t}={n}" for t, n in Counter(q['tipo'] for q in qs).items()))
    print("  gabaritos: " + ", ".join(f"{g}={n}" for g, n in sorted(Counter(q.get('gabarito') for q in qs if q.get('gabarito')).items())))
    return erros


def main():
    lista = json.loads((RAIZ / "disciplinas.json").read_text(encoding="utf-8"))
    total = sum(validar(RAIZ / d["arquivo"]) for d in lista["disciplinas"])
    print("\n✓ Tudo certo." if total == 0 else f"\n{total} erro(s) encontrado(s).")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
