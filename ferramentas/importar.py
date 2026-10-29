"""Importa um lote de questões novas para uma disciplina.

Uso:  python3 ferramentas/importar.py matematica lote.json
      python3 ferramentas/importar.py portugues lote.json

O lote pode ser uma lista de questões ou {"textos": {...}, "questoes": [...]}.
As questões do lote não precisam de "id": o importador numera a partir do último código.
Também:
  - recusa questões repetidas (mesmo enunciado, texto-base e alternativas);
  - recusa códigos de texto-base que já existem;
  - nas objetivas com alternativas em texto, reposiciona a resposta certa para equilibrar
    A, B, C e D no arquivo (as citações {A}, {B}... do comentário acompanham);
  - alternativas numéricas ficam na ordem em que foram escritas (de preferência crescente).
Depois de importar, rode ferramentas/validar.py.
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

DADOS = Path(__file__).resolve().parent.parent / "dados"
LETRAS = "ABCDE"


def norm(s):
    s = unicodedata.normalize("NFD", s or "")
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c))).strip().lower()


def chave_de(q):
    """Mesma pergunta = mesmo enunciado, mesmo texto-base e mesmas alternativas (em qualquer ordem)."""
    return (norm(q["enunciado"]), q.get("texto"), tuple(sorted(norm(a) for a in q.get("alternativas", []))))


def numerica(alts):
    return all(re.fullmatch(r"[−\-≈ ]*[\d.,/]+[\s\w²³°%$×⁰¹²³⁴⁵⁶⁷⁸⁹⁻√]*|[−\-]?R\$ ?[\d.,]+", a.strip()) for a in alts)


def reposicionar(q, alvo):
    k = len(q["alternativas"])
    atual = LETRAS.index(q["gabarito"])
    ordem = [i for i in range(k) if i != atual]
    ordem.insert(LETRAS.index(alvo), atual)
    q["alternativas"] = [q["alternativas"][i] for i in ordem]
    mapa = {LETRAS[o]: LETRAS[n] for n, o in enumerate(ordem)}
    q["gabarito"] = mapa[q["gabarito"]]
    q["comentario"] = re.sub(r"\{([A-E])\}", lambda m: "{" + mapa[m.group(1)] + "}", q["comentario"])


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    slug, lote_path = sys.argv[1], Path(sys.argv[2])
    arq = DADOS / f"{slug}.json"
    dados = json.loads(arq.read_text(encoding="utf-8"))
    lote = json.loads(lote_path.read_text(encoding="utf-8"))
    novas = lote if isinstance(lote, list) else lote.get("questoes", [])
    textos = {} if isinstance(lote, list) else lote.get("textos", {})

    dados.setdefault("textos", {})
    repetidos = [t for t in textos if t in dados["textos"]]
    if repetidos:
        sys.exit(f"Códigos de texto já existentes: {', '.join(repetidos)}. Use códigos novos.")
    dados["textos"].update(textos)

    vistos = {chave_de(q) for q in dados["questoes"]}
    prefixo = dados["prefixo"]
    n = max((int(q["id"].split("-")[1]) for q in dados["questoes"]), default=0)
    cont = Counter(q["gabarito"] for q in dados["questoes"] if q.get("tipo") == "objetiva")
    entraram, puladas = 0, []

    for q in novas:
        chave = chave_de(q)
        if chave in vistos:
            puladas.append(q["enunciado"][:60])
            continue
        vistos.add(chave)
        q.pop("id", None)
        if q.get("tipo") == "objetiva":
            k = len(q["alternativas"])
            if not numerica(q["alternativas"]) and not q.get("fixar_ordem"):
                alvo = min(LETRAS[:k], key=lambda x: (cont[x], x != q["gabarito"]))
                reposicionar(q, alvo)
            cont[q["gabarito"]] += 1
        q.pop("fixar_ordem", None)
        n += 1
        dados["questoes"].append({"id": f"{prefixo}-{n:04d}", **q})
        entraram += 1

    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{entraram} questões importadas em {arq.name} (total: {len(dados['questoes'])}).")
    for p in puladas:
        print(f"  pulada por repetição: {p}…")


if __name__ == "__main__":
    main()
