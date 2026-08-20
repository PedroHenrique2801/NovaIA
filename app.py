from flask import Flask, render_template, request, jsonify
import ast
import operator
import re
import urllib.parse
import urllib.request
import json

app = Flask(__name__)

# =========================================================
# MEMÓRIA DA NOVAIA
# =========================================================

memoria = {
    "nome": None,
    "gosta": [],
    "nao_gosta": [],
    "assunto": None,
    "fatos": []
}

# =========================================================
# SISTEMA DE CONVERSAS
# =========================================================

conversas = [
    {
        "id": 1,
        "titulo": "Nova conversa",
        "mensagens": []
    }
]

proximo_id = 2

# =========================================================
# CALCULADORA
# =========================================================

def calcular(expressao):
    try:
        expressao = expressao.strip()
        expressao = expressao.replace(",", ".")
        expressao = expressao.replace("×", "*")
        expressao = expressao.replace("÷", "/")
        expressao = expressao.replace("^", "**")

        arvore = ast.parse(expressao, mode="eval")

        operadores = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod
        }

        def resolver(no):

            if isinstance(no, ast.Constant):

                if isinstance(no.value, (int, float)):
                    return no.value

            if isinstance(no, ast.UnaryOp):

                if isinstance(no.op, ast.USub):
                    return -resolver(no.operand)

                if isinstance(no.op, ast.UAdd):
                    return resolver(no.operand)

            if isinstance(no, ast.BinOp):

                esquerda = resolver(no.left)
                direita = resolver(no.right)

                if type(no.op) in operadores:

                    if type(no.op) is ast.Pow and abs(direita) > 100:
                        raise ValueError

                    return operadores[type(no.op)](
                        esquerda,
                        direita
                    )

            raise ValueError

        return resolver(arvore.body)

    except Exception:
        return None


def formatar_resultado(resultado):

    if isinstance(resultado, float):

        if resultado.is_integer():
            return str(int(resultado))

        return str(round(resultado, 10))

    return str(resultado)

# =========================================================
# FRAÇÕES
# =========================================================

def calcular_fracao(texto):

    padrao = re.search(
        r"(\d+)\s*/\s*(\d+)\s*([+\-*])\s*(\d+)\s*/\s*(\d+)",
        texto
    )

    if not padrao:
        return None

    n1 = int(padrao.group(1))
    d1 = int(padrao.group(2))
    operador_fracao = padrao.group(3)
    n2 = int(padrao.group(4))
    d2 = int(padrao.group(5))

    if d1 == 0 or d2 == 0:
        return "Não é possível dividir por zero. ❌"

    if operador_fracao == "+":
        numerador = n1 * d2 + n2 * d1
        denominador = d1 * d2

    elif operador_fracao == "-":
        numerador = n1 * d2 - n2 * d1
        denominador = d1 * d2

    else:
        numerador = n1 * n2
        denominador = d1 * d2

    divisor = abs(__import__("math").gcd(numerador, denominador))

    numerador //= divisor
    denominador //= divisor

    return (
        f"{n1}/{d1} {operador_fracao} {n2}/{d2} = "
        f"{numerador}/{denominador} 🧮"
    )

# =========================================================
# ABREVIAÇÕES
# =========================================================

def normalizar_abreviacoes(texto):

    substituicoes = {

        "vcs": "vocês",
        "vc": "você",
        "oq": "o que",
        "pq": "porque",
        "tbm": "também",
        "tb": "também",
        "blz": "beleza",
        "obg": "obrigado",
        "vlw": "valeu",
        "flw": "falou",
        "dps": "depois",
        "nn": "não",
        "n": "não",

        "phyton": "python",
        "pyton": "python",
        "pyhton": "python"
    }

    for palavra, substituto in substituicoes.items():

        texto = re.sub(
            r"\b" + re.escape(palavra) + r"\b",
            substituto,
            texto
        )

    return texto


def normalizar_texto(texto):

    texto = texto.lower().strip()

    return normalizar_abreviacoes(texto)

# =========================================================
# MEMÓRIA
# =========================================================

def analisar_memoria(texto):

    resultado = re.search(
        r"eu não gosto de (.+)",
        texto
    )

    if resultado:

        coisa = resultado.group(1).strip()

        if coisa:

            if coisa not in memoria["nao_gosta"]:
                memoria["nao_gosta"].append(coisa)

            return (
                "Entendi! 🧠\n\n"
                f"Vou lembrar que você não gosta de {coisa}."
            )

    resultado = re.search(
        r"eu gosto de (.+)",
        texto
    )

    if resultado:

        coisa = resultado.group(1).strip()

        if coisa:

            if coisa not in memoria["gosta"]:
                memoria["gosta"].append(coisa)

            return (
                "Legal! 😄🧠\n\n"
                f"Vou lembrar que você gosta de {coisa}."
            )

    resultado = re.search(
        r"eu moro em (.+)",
        texto
    )

    if resultado:

        local = resultado.group(1).strip()

        if local and local not in memoria["fatos"]:
            memoria["fatos"].append(
                f"Mora em {local}"
            )

        return (
            "Entendi! 🧠\n\n"
            "Vou lembrar dessa informação."
        )

    resultado = re.search(
        r"eu tenho (\d+) anos",
        texto
    )

    if resultado:

        idade = resultado.group(1)

        memoria["fatos"] = [
            fato for fato in memoria["fatos"]
            if not fato.startswith("Tem ")
        ]

        memoria["fatos"].append(
            f"Tem {idade} anos"
        )

        return (
            "Entendi! 🧠\n\n"
            "Vou lembrar dessa informação."
        )

    return None


def responder_memoria(texto):

    if (
        "o que voce lembra de mim" in texto
        or "o que lembra de mim" in texto
        or "o que voce sabe sobre mim" in texto
        or "o que você lembra de mim" in texto
        or "o que você sabe sobre mim" in texto
    ):

        partes = []

        if memoria["nome"]:
            partes.append(
                f"Seu nome é {memoria['nome']}."
            )

        if memoria["gosta"]:
            partes.append(
                "Você gosta de "
                + ", ".join(memoria["gosta"])
                + "."
            )

        if memoria["nao_gosta"]:
            partes.append(
                "Você não gosta de "
                + ", ".join(memoria["nao_gosta"])
                + "."
            )

        if memoria["fatos"]:
            partes.extend(memoria["fatos"])

        if memoria["assunto"]:
            partes.append(
                "Nosso assunto mais recente é "
                f"{memoria['assunto']}."
            )

        if not partes:

            return (
                "Por enquanto ainda não tenho muitas "
                "informações guardadas sobre você. 🧠"
            )

        return (
            "Claro! 🧠🤖\n\n"
            + "\n".join(partes)
        )

    if "do que eu gosto" in texto:

        if memoria["gosta"]:

            return (
                "Você me contou que gosta de "
                + ", ".join(memoria["gosta"])
                + ". 😄"
            )

        return "Você ainda não me contou do que gosta. 😄"

    if "do que eu nao gosto" in texto:

        if memoria["nao_gosta"]:

            return (
                "Você me contou que não gosta de "
                + ", ".join(memoria["nao_gosta"])
                + "."
            )

        return (
            "Você ainda não me contou do que não gosta."
        )

    return None

# =========================================================
# PYTHON
# =========================================================

def resposta_python(texto):

    if "python" not in texto:
        return None

    if (
        "como o python funciona" in texto
        or "como python funciona" in texto
        or "como funciona o python" in texto
        or "como funciona python" in texto
    ):

        return (
            "O Python funciona através de instruções "
            "que você escreve em código. 🐍💻\n\n"
            "O programa interpreta essas instruções "
            "e executa as ações programadas.\n\n"
            "Na NovaIA, usamos Python para controlar "
            "o servidor, receber mensagens e gerar respostas."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
        or "usado para" in texto
        or "usada para" in texto
    ):

        return (
            "Python é usado para muitas coisas! 🐍💻\n\n"
            "Ele pode criar programas, sites, "
            "automações, servidores, ferramentas, "
            "jogos e sistemas de inteligência artificial.\n\n"
            "A NovaIA também usa Python."
        )

    if (
        "o que da para fazer" in texto
        or "o que dá para fazer" in texto
        or "o que da pra fazer" in texto
        or "o que dá pra fazer" in texto
        or "o que posso fazer" in texto
        or "o que posso criar" in texto
    ):

        return (
            "Com Python dá para criar muitos projetos! 🐍🚀\n\n"
            "Calculadoras, aplicativos, servidores, "
            "automações, ferramentas, jogos e sistemas "
            "de inteligência artificial."
        )

    if (
        "o que é python" in texto
        or "o que e python" in texto
        or "me explica python" in texto
    ):

        return (
            "Python 🐍 é uma linguagem de programação "
            "muito usada na tecnologia.\n\n"
            "Ela permite criar programas, servidores, "
            "automações, ferramentas e sistemas de IA."
        )

    return (
        "Python 🐍 é uma linguagem de programação "
        "versátil usada em várias áreas da tecnologia."
    )

# =========================================================
# PROGRAMAÇÃO
# =========================================================

def resposta_programacao(texto):

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "Programação serve para criar instruções "
            "que fazem o computador realizar tarefas. 💻\n\n"
            "Com ela podemos criar aplicativos, sites, "
            "jogos, sistemas e automações."
        )

    if "como funciona" in texto:

        return (
            "Programação funciona através de instruções "
            "que o computador executa. 💻\n\n"
            "O programador escreve essas instruções "
            "usando uma linguagem de programação."
        )

    if (
        "o que é" in texto
        or "o que e" in texto
        or "me explica" in texto
    ):

        return (
            "Programação é o processo de escrever "
            "instruções para um computador executar. 💻"
        )

    return None

# =========================================================
# INTELIGÊNCIA ARTIFICIAL
# =========================================================

def resposta_ia(texto):

    if (
        "o que é inteligência artificial" in texto
        or "o que e inteligencia artificial" in texto
        or "o que é ia" in texto
        or "o que e ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Inteligência Artificial, ou IA, é uma área "
            "da computação que cria sistemas capazes "
            "de realizar tarefas de forma inteligente. 🤖🧠\n\n"
            "Dependendo do sistema, ela pode analisar "
            "informações, reconhecer padrões, conversar "
            "e gerar conteúdo."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "A inteligência artificial pode ajudar "
            "em muitas tarefas! 🤖\n\n"
            "Ela pode analisar informações, responder "
            "perguntas, reconhecer padrões, ajudar "
            "nos estudos e automatizar tarefas."
        )

    if (
        "como funciona" in texto
        or "como a ia funciona" in texto
        or "como funciona uma ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Uma IA processa informações usando modelos "
            "computacionais capazes de identificar padrões. 🧠🤖\n\n"
            "Em sistemas modernos, modelos podem ser "
            "treinados com muitos dados para aprender "
            "padrões e produzir resultados."
        )

    return (
        "A inteligência artificial é uma área enorme "
        "da tecnologia. 🤖🧠\n\n"
        "Posso explicar o que é IA, para que ela serve "
        "ou como ela funciona."
    )

# =========================================================
# MATEMÁTICA
# =========================================================

def resposta_matematica(texto):

    fracao = calcular_fracao(texto)

    if fracao:
        memoria["assunto"] = "matemática"
        return fracao

    if (
        "o que é uma fração" in texto
        or "o que e uma fracao" in texto
    ):

        return (
            "Uma fração representa uma parte de um todo. 🧮\n\n"
            "Por exemplo, 3/4 significa três partes "
            "de um total dividido em quatro partes iguais.\n\n"
            "O número de cima é o numerador e o número "
            "de baixo é o denominador."
        )

    if "porcentagem" in texto:

        return (
            "Porcentagem representa uma parte de 100. 🧮\n\n"
            "Por exemplo, 25% significa 25 de cada 100."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "A matemática serve para resolver problemas "
            "e entender números, quantidades, formas "
            "e relações. 🧮"
        )

    return None

# =========================================================
# RESPOSTAS EXTRAS
# =========================================================

def resposta_extra(texto):

    if (
        "quem criou você" in texto
        or "quem criou voce" in texto
    ):

        return (
            "Eu fui criada através de código! 🤖💻\n\n"
            "E você está desenvolvendo a NovaIA comigo."
        )

    if (
        "você é uma ia" in texto
        or "voce e uma ia" in texto
    ):

        return (
            "Sim! 🤖\n\n"
            "Eu sou a NovaIA, uma assistente virtual "
            "que estamos construindo com Python."
        )

    if (
        "você é inteligente" in texto
        or "voce e inteligente" in texto
    ):

        return (
            "Estou ficando cada vez melhor! 😎🧠\n\n"
            "Já consigo conversar, lembrar informações, "
            "fazer contas e responder perguntas."
        )

    if (
        "me ajuda" in texto
        or "me ajude" in texto
    ):

        return (
            "Claro! 😄🤖\n\n"
            "Pode me falar o que você precisa."
        )

    if "tudo bem" in texto:

        return (
            "Tudo certo por aqui! 😎🤖\n\n"
            "E com você?"
        )

    if (
        "você está aí" in texto
        or "voce esta ai" in texto
    ):

        return "Estou aqui! 🤖😎 Pode mandar."

    if (
        "você sabe meu nome" in texto
        or "voce sabe meu nome" in texto
    ):

        if memoria["nome"]:
            return f"Sei sim! Seu nome é {memoria['nome']}! 🧠"

        return (
            "Ainda não. Me diga seu nome que eu posso lembrar."
        )

    if "obrigado" in texto or "obrigada" in texto:
        return "Por nada! 😄🤖"

    return None

# =========================================================
# CONVERSA
# =========================================================

def resposta_conversa(texto):

    if texto in [
        "oi",
        "olá",
        "ola",
        "oii",
        "oiii",
        "eai",
        "e aí",
        "e ai",
        "hey",
        "hello"
    ]:

        if memoria["nome"]:

            return (
                f"Olá, {memoria['nome']}! 😄\n\n"
                "Que bom te ver novamente!\n\n"
                "Como posso ajudar hoje?"
            )

        return (
            "Olá! 😄\n\n"
            "Eu sou a NovaIA! 🤖\n\n"
            "Como posso ajudar você hoje?"
        )

    if "bom dia" in texto:
        return "Bom dia! ☀️\n\nComo posso ajudar hoje?"

    if "boa tarde" in texto:
        return "Boa tarde! 😄\n\nComo posso ajudar?"

    if "boa noite" in texto:
        return "Boa noite! 🌙\n\nComo posso ajudar?"

    if "valeu" in texto:
        return "É nós! 😎🤖"

    if "falou" in texto:
        return "Falou! 👋 Até a próxima!"

    if "beleza" in texto:
        return "Beleza! 😎🤖"

    if "entendi" in texto:

        return (
            "Boa! 😎🧠\n\n"
            "Pode continuar o assunto."
        )

    if (
        "não entendi" in texto
        or "nao entendi" in texto
    ):

        return (
            "Sem problema! 😄\n\n"
            "Posso explicar de um jeito mais simples "
            "ou dar um exemplo."
        )

    if (
        "seu nome" in texto
        or "como você se chama" in texto
        or "como voce se chama" in texto
    ):

        return (
            "Meu nome é NovaIA! 🤖\n\n"
            "Sou a assistente virtual que estamos "
            "construindo juntos."
        )

    if (
        "quem é você" in texto
        or "quem e voce" in texto
    ):

        return (
            "Eu sou a NovaIA! 🤖🧠\n\n"
            "Sou uma assistente virtual feita com Python.\n\n"
            "Já consigo conversar, lembrar informações, "
            "resolver contas e responder sobre vários assuntos."
        )

    if "capital do brasil" in texto:
        return "A capital do Brasil é Brasília! 🇧🇷"

    if "piada" in texto:

        return (
            "Claro! 😂\n\n"
            "Por que o computador foi ao médico?\n\n"
            "Porque estava com um vírus! 🖥️😂"
        )

    if "curiosidade" in texto:

        return (
            "Claro! 🧠🌎\n\n"
            "Uma curiosidade interessante é que Vênus "
            "gira em sentido contrário ao da maioria "
            "dos planetas do Sistema Solar."
        )

    return None

# =========================================================
# PESQUISA NA INTERNET
# =========================================================

def pesquisar_web(pergunta):

    try:

        consulta = urllib.parse.quote(pergunta)

        url = (
            "https://api.duckduckgo.com/"
            f"?q={consulta}"
            "&format=json"
            "&no_html=1"
            "&skip_disambig=1"
        )

        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent": "NovaIA/1.0"
            }
        )

        with urllib.request.urlopen(
            requisicao,
            timeout=5
        ) as resposta:

            dados = json.loads(
                resposta.read().decode("utf-8")
            )

        resumo = dados.get(
            "AbstractText",
            ""
        )

        titulo = dados.get(
            "Heading",
            ""
        )

        if resumo:

            memoria["assunto"] = pergunta

            return (
                f"Encontrei uma informação sobre "
                f"**{titulo or pergunta}**. 🌐\n\n"
                f"{resumo}"
            )

        resultados = dados.get(
            "RelatedTopics",
            []
        )

        for item in resultados:

            if isinstance(item, dict):

                texto = item.get(
                    "Text",
                    ""
                )

                if texto:

                    memoria["assunto"] = pergunta

                    return (
                        "Encontrei isto na pesquisa: 🌐\n\n"
                        + texto
                    )

    except Exception:
        pass

    return None

# =========================================================
# GERAR RESPOSTA
# =========================================================

def gerar_resposta(mensagem):

    texto = normalizar_texto(mensagem)

    # NOME

    if texto.startswith("meu nome é "):

        nome = mensagem[
            len("meu nome é "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄\n\n"
            "Agora vou lembrar do seu nome."
        )

    if texto.startswith("meu nome e "):

        nome = mensagem[
            len("meu nome e "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄"
        )

    if texto.startswith("me chamo "):

        nome = mensagem[
            len("me chamo "):
        ].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄"
        )

    if (
        "qual é meu nome" in texto
        or "qual e meu nome" in texto
        or "qual é o meu nome" in texto
        or "qual e o meu nome" in texto
        or "qual meu nome" in texto
        or "como eu me chamo" in texto
    ):

        if memoria["nome"]:
            return f"Seu nome é {memoria['nome']}! 🧠"

        return "Você ainda não me contou seu nome. 😄"

    # MEMÓRIA

    resposta = analisar_memoria(texto)

    if resposta is not None:
        return resposta

    resposta = responder_memoria(texto)

    if resposta is not None:
        return resposta

    # PYTHON

    if "python" in texto:

        resposta = resposta_python(texto)

        if resposta is not None:
            return resposta

    # IA

    if (
        "inteligência artificial" in texto
        or "inteligencia artificial" in texto
        or "o que é ia" in texto
        or "o que e ia" in texto
        or texto == "ia"
    ):

        resposta = resposta_ia(texto)

        if resposta is not None:
            return resposta

    # PROGRAMAÇÃO

    if (
        "programação" in texto
        or "programacao" in texto
        or "programar" in texto
    ):

        resposta = resposta_programacao(texto)

        if resposta is not None:
            return resposta

    # MATEMÁTICA

    if (
        "matemática" in texto
        or "matematica" in texto
        or "fração" in texto
        or "fracao" in texto
        or re.search(
            r"\d+\s*/\s*\d+\s*[+\-*]\s*\d+\s*/\s*\d+",
            texto
        )
    ):

        resposta = resposta_matematica(texto)

        if resposta is not None:
            return resposta

    # RESPOSTAS EXTRAS

    resposta = resposta_extra(texto)

    if resposta is not None:
        return resposta

    # CONVERSA

    resposta = resposta_conversa(texto)

    if resposta is not None:
        return resposta

    # CALCULADORA

    expressao = texto

    palavras = [
        "quanto é",
        "quanto e",
        "calcule",
        "calcula",
        "resultado de",
        "qual o resultado de",
        "qual é o resultado de",
        "qual e o resultado de"
    ]

    for palavra in palavras:

        expressao = expressao.replace(
            palavra,
            ""
        )

    expressao = expressao.strip()

    resultado = calcular(expressao)

    if resultado is not None:

        memoria["assunto"] = "matemática"

        return (
            "O resultado é "
            f"{formatar_resultado(resultado)} 🧮"
        )

    # PESQUISA

    palavras_pesquisa = [
        "pesquise",
        "pesquisa",
        "procure",
        "procura",
        "pesquisar",
        "quem é",
        "quem foi",
        "quando foi",
        "onde fica",
        "últimas notícias",
        "notícias sobre"
    ]

    deve_pesquisar = False

    for palavra in palavras_pesquisa:

        if palavra in texto:

            deve_pesquisar = True
            break

    if deve_pesquisar:

        pergunta = texto

        for palavra in palavras_pesquisa:
            pergunta = pergunta.replace(
                palavra,
                ""
            )

        pergunta = pergunta.strip()

        resultado_web = pesquisar_web(
            pergunta
        )

        if resultado_web:
            return resultado_web

        return (
            "Tentei pesquisar na internet, "
            "mas não consegui encontrar uma "
            "resposta agora. 🌐"
        )

    # RESPOSTA PADRÃO

    return (
        "Entendi! 🧠🤖\n\n"
        "Ainda estou aprendendo esse assunto.\n\n"
        "Você pode tentar perguntar de outra forma "
        "ou pedir para eu pesquisar na internet."
    )

# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )

# =========================================================
# LISTAR CONVERSAS
# =========================================================

@app.route("/conversas")
def listar_conversas():

    resultado = []

    for conversa in conversas:

        titulo = conversa["titulo"]

        if (
            titulo == "Nova conversa"
            and len(conversa["mensagens"]) > 0
        ):

            primeira = conversa["mensagens"][0]

            titulo = primeira["texto"][:30]

            if len(primeira["texto"]) > 30:
                titulo += "..."

        resultado.append({

            "id": conversa["id"],
            "titulo": titulo

        })

    return jsonify(resultado)

# =========================================================
# ABRIR UMA CONVERSA
# =========================================================

@app.route("/conversa/<int:id>")
def abrir_conversa(id):

    for conversa in conversas:

        if conversa["id"] == id:

            return jsonify(conversa)

    return jsonify({
        "erro": "Conversa não encontrada."
    }), 404

# =========================================================
# NOVA CONVERSA
# =========================================================

@app.route(
    "/nova_conversa",
    methods=["POST"]
)
def nova_conversa():

    global proximo_id

    nova = {

        "id": proximo_id,

        "titulo": "Nova conversa",

        "mensagens": []

    }

    conversas.append(nova)

    proximo_id += 1

    return jsonify(nova)

# =========================================================
# EXCLUIR CONVERSA
# =========================================================

@app.route(
    "/excluir_conversa/<int:id>",
    methods=["DELETE"]
)
def excluir_conversa(id):

    global conversas

    if len(conversas) <= 1:

        return jsonify({

            "sucesso": False,

            "mensagem":
                "Você precisa ter pelo menos uma conversa."

        })

    for conversa in conversas:

        if conversa["id"] == id:

            conversas.remove(conversa)

            return jsonify({

                "sucesso": True

            })

    return jsonify({

        "sucesso": False,

        "mensagem": "Conversa não encontrada."

    }), 404

# =========================================================
# CHAT
# =========================================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    dados = request.get_json()

    mensagem = dados.get(
        "mensagem",
        ""
    ).strip()

    if not mensagem:

        return jsonify({

            "resposta":
                "Digite alguma coisa para conversar comigo. 😄"

        })

    conversa_id = dados.get(
        "conversa_id",
        1
    )

    conversa_encontrada = None

    for conversa in conversas:

        if conversa["id"] == conversa_id:

            conversa_encontrada = conversa

            break

    if conversa_encontrada is None:

        conversa_encontrada = conversas[0]

    conversa_encontrada["mensagens"].append({

        "tipo": "usuario",

        "texto": mensagem

    })

    if (
        conversa_encontrada["titulo"]
        == "Nova conversa"
    ):

        titulo = mensagem[:30]

        if len(mensagem) > 30:
            titulo += "..."

        conversa_encontrada["titulo"] = titulo

    resposta = gerar_resposta(
        mensagem
    )

    conversa_encontrada["mensagens"].append({

        "tipo": "ia",

        "texto": resposta

    })

    return jsonify({

        "resposta": resposta,

        "conversa_id":
            conversa_encontrada["id"]

    })

# =========================================================
# INICIAR SERVIDOR
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )