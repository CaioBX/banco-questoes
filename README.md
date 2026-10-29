# Banco de Questões Multidisciplinar

Acervo de questões prontas, com resposta comentada, para professores do Ensino Fundamental (1º ao 9º ano).
O professor filtra por componente curricular, ano, unidade temática/eixo, assunto, dificuldade e tipo, seleciona as
questões e monta uma lista de exercícios ou avaliação (impressão/PDF ou Word), ou projeta as questões em sala.

Um único `index.html` serve todas as disciplinas. As questões ficam em arquivos de dados separados, em `dados/`.
Quando um arquivo de dados é atualizado no GitHub, a página incorporada mostra as novas questões sozinha.

## Estrutura

```
index.html                 o app (não precisa mexer para incluir questões)
dados/disciplinas.json     lista de disciplinas disponíveis
dados/portugues.json       textos-base e questões de Língua Portuguesa
dados/matematica.json      questões de Matemática
ferramentas/validar.py     confere os dados antes de publicar
```

## Publicar (GitHub Pages)

1. Crie um repositório (por exemplo, `banco-questoes`) e envie todos os arquivos desta pasta.
2. No repositório: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, pasta `/ (root)`.
3. Em cerca de um minuto o endereço fica disponível: `https://SEU-USUARIO.github.io/banco-questoes/`.

## Incorporar na área de membros

Um bloco de HTML por disciplina, mudando só o final do link:

```html
<!-- Língua Portuguesa -->
<iframe src="https://SEU-USUARIO.github.io/banco-questoes/?d=portugues"
        style="width:100%;height:85vh;min-height:640px;border:0;border-radius:12px"
        allow="fullscreen" allowfullscreen loading="lazy" title="Banco de Questões de Língua Portuguesa"></iframe>

<!-- Matemática -->
<iframe src="https://SEU-USUARIO.github.io/banco-questoes/?d=matematica"
        style="width:100%;height:85vh;min-height:640px;border:0;border-radius:12px"
        allow="fullscreen" allowfullscreen loading="lazy" title="Banco de Questões de Matemática"></iframe>
```

Com `?d=...` a página fica travada naquela disciplina. Sem o parâmetro, aparecem abas para trocar de disciplina.

**Sobre o acesso:** o login da área de membros protege a página onde o iframe está, mas o endereço do GitHub Pages em
si é público. Quem tiver o link direto consegue abrir. Para fechar isso de verdade, o caminho é hospedar no Cloudflare
(Pages + Access ou verificação de token vindo da área de membros).

## Como incluir questões

Edite o arquivo da disciplina em `dados/` e acrescente um item na lista `"questoes"`. O app ordena por ano e código,
então a posição no arquivo não importa.

### Questão objetiva

```json
{
  "id": "MAT-0059",
  "ano": 6,
  "eixo": "Números",
  "assunto": "Frações",
  "dificuldade": "média",
  "tipo": "objetiva",
  "enunciado": "Texto da pergunta. Use \n para quebrar linha.",
  "alternativas": ["primeira", "segunda", "terceira", "quarta"],
  "gabarito": "C",
  "comentario": "Por que C está certa. A alternativa {A} mostra tal erro; {B} indica outro."
}
```

### Questão discursiva

```json
{
  "id": "LP-0049", "ano": 7, "eixo": "Produção de textos", "assunto": "Resumo",
  "dificuldade": "média", "tipo": "discursiva",
  "enunciado": "...",
  "resposta_esperada": "O que se espera da resposta.",
  "comentario": "Critérios de correção para o professor."
}
```

### Regras

- `id`: prefixo da disciplina (`LP-`, `MAT-`) + número com 4 dígitos, sem repetir.
- `ano`: número de 1 a 9.
- `eixo`: precisa ser um dos valores da lista `"eixos"` no topo do arquivo.
- `dificuldade`: `fácil`, `média` ou `difícil`. `tipo`: `objetiva` ou `discursiva`.
- No comentário, cite alternativas como `{A}`, `{B}`... (com chaves). Assim, quando o professor marcar
  “Embaralhar alternativas”, o gabarito comentado acompanha a nova ordem.
- Campos opcionais: `tabela` (`{"cabecalho": [...], "linhas": [[...], ...]}`),
  `texto` (código de um texto-base).

### Textos-base (Língua Portuguesa)

Ficam em `"textos"` e podem ser usados por várias questões:

```json
"T09": { "titulo": "Título", "genero": "Fábula", "conteudo": "Parágrafo 1\nParágrafo 2" }
```

Na questão, informe `"texto": "T09"`. Na impressão, o texto sai uma vez antes do bloco de questões que o usam.
Para poemas, use `"genero": "Poema"` e deixe uma linha vazia (`\n\n`) entre estrofes.

### Conferir antes de publicar

```
python3 ferramentas/validar.py
```

Mostra erros (JSON quebrado, gabarito inválido, id repetido, eixo fora da lista) e um resumo por ano, eixo e gabarito.

## Nova disciplina

1. Copie `dados/matematica.json` como `dados/ciencias.json`, ajuste `disciplina`, `slug`, `prefixo`, `rotulo_eixo`
   e `eixos`, e troque as questões.
2. Acrescente a linha em `dados/disciplinas.json`.
3. Incorpore com `?d=ciencias`.

## Atualização

O GitHub Pages leva até cerca de 10 minutos para refletir uma alteração. O app sempre busca a versão mais recente
dos dados ao abrir.
