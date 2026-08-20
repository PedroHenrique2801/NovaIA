from flask import Flask, render_template, request, jsonify
import ast
import operator
import re
import random

app = Flask(__name__)

# =========================================================
# MEMÓRIA DA NOVAIA
# =========================================================

memoria = {
    "nome": None,
    "gosta": [],
    "nao_gosta": [],
    "assunto": None
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
            ast.Pow: operator.pow
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

    return None


def responder_memoria(texto):

    if (
        "o que voce lembra de mim" in texto
        or "o que lembra de mim" in texto
        or "o que voce sabe sobre mim" in texto
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

        if memoria["assunto"]:

            partes.append(
                "Nosso assunto mais recente é "
                + memoria["assunto"]
                + "."
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
            "O Python funciona através de instruções que "
            "você escreve em código. 🐍💻\n\n"
            "Quando você executa um programa, o Python "
            "interpreta essas instruções e realiza as "
            "ações que você programou.\n\n"
            "Na NovaIA, usamos Python no servidor para "
            "receber mensagens, processá-las e enviar "
            "respostas para o chat."
        )


    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
        or "usado para" in texto
        or "usada para" in texto
        or "serve pra" in texto
    ):

        return (
            "Python é usado para muitas coisas! 🐍💻\n\n"
            "Ele pode ser usado para criar programas, "
            "sites, automações, servidores, ferramentas, "
            "jogos e projetos de inteligência artificial.\n\n"
            "Também é muito usado para trabalhar com dados "
            "e automatizar tarefas."
        )


    if (
        "o que da para fazer" in texto
        or "o que dá para fazer" in texto
        or "o que da pra fazer" in texto
        or "o que dá pra fazer" in texto
        or "o que posso fazer" in texto
        or "o que posso criar" in texto
        or "o que consigo fazer" in texto
    ):

        return (
            "Com Python dá para criar muitos projetos! 🐍🚀\n\n"
            "Por exemplo: calculadoras, programas, "
            "automações, servidores, ferramentas, jogos "
            "simples e sistemas.\n\n"
            "Python também é muito usado em inteligência "
            "artificial e análise de dados."
        )


    if (
        "o que é python" in texto
        or "o que e python" in texto
        or "me explica python" in texto
    ):

        return (
            "Python 🐍 é uma linguagem de programação "
            "muito usada na tecnologia.\n\n"
            "Com ela podemos criar programas, automações, "
            "servidores, ferramentas e projetos de "
            "inteligência artificial."
        )


    return (
        "Python 🐍 é uma linguagem de programação muito "
        "versátil e usada em várias áreas da tecnologia."
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
            "jogos, sistemas, automações e muito mais."
        )


    if "como funciona" in texto:

        return (
            "Programação funciona através de instruções "
            "que o computador executa. 💻\n\n"
            "O programador escreve essas instruções usando "
            "uma linguagem de programação."
        )


    if (
        "o que é" in texto
        or "o que e" in texto
        or "me explica" in texto
    ):

        return (
            "Programação é o processo de escrever instruções "
            "para um computador executar. 💻"
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
            "da computação que busca criar sistemas capazes "
            "de realizar tarefas que normalmente exigiriam "
            "algum tipo de inteligência humana. 🤖🧠\n\n"
            "Uma IA pode analisar informações, reconhecer "
            "padrões, conversar, classificar dados ou gerar "
            "conteúdos, dependendo do sistema."
        )


    if (
        "pra que serve" in texto
        or "para que serve" in texto
        or "serve para que" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "A inteligência artificial pode ser usada "
            "para muitas tarefas! 🤖\n\n"
            "Ela pode ajudar nos estudos, analisar "
            "informações, responder perguntas, reconhecer "
            "padrões e automatizar tarefas."
        )


    if (
        "como funciona" in texto
        or "como a ia funciona" in texto
        or "como funciona uma ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Uma IA funciona usando modelos computacionais "
            "que processam informações e identificam "
            "padrões para realizar determinadas tarefas. 🧠🤖\n\n"
            "Muitos sistemas modernos são treinados usando "
            "grandes quantidades de dados."
        )


    if (
        "o que da para fazer com ia" in texto
        or "o que dá para fazer com ia" in texto
        or "o que da pra fazer com ia" in texto
        or "o que dá pra fazer com ia" in texto
        or "o que posso fazer com ia" in texto
        or "o que posso criar com ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Com inteligência artificial dá para fazer "
            "muitas coisas! 🤖🚀\n\n"
            "Podemos criar assistentes virtuais, analisar "
            "textos, ajudar nos estudos, analisar informações "
            "e automatizar tarefas.\n\n"
            "Também existem IAs que trabalham com imagens, "
            "áudio, vídeo e programação."
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

    if (
        "o que é uma fração" in texto
        or "o que e uma fracao" in texto
    ):

        return (
            "Uma fração representa uma parte de um todo. 🧮\n\n"
            "Por exemplo, 3/4 significa três partes de "
            "um total dividido em quatro partes iguais.\n\n"
            "O número de cima é o numerador e o número "
            "de baixo é o denominador."
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

        return (
            "Bom dia! ☀️\n\n"
            "Espero que seu dia esteja começando bem!"
        )


    if "boa tarde" in texto:

        return (
            "Boa tarde! 😄\n\n"
            "Como posso ajudar?"
        )


    if "boa noite" in texto:

        return (
            "Boa noite! 🌙\n\n"
            "Espero que você tenha tido um ótimo dia!"
        )


    if (
        "obrigado" in texto
        or "obrigada" in texto
    ):

        return (
            "Por nada! 😄\n\n"
            "Fico feliz em ajudar!"
        )


    if "valeu" in texto:

        return "É nós! 😎🤖"


    if "falou" in texto:

        return "Falou! 👋 Até a próxima!"


    if "beleza" in texto:

        return "Beleza! 😎🤖"


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
            "Sou uma assistente virtual que estamos "
            "desenvolvendo juntos.\n\n"
            "Já consigo conversar, lembrar informações, "
            "entender abreviações, resolver contas e "
            "responder perguntas sobre alguns assuntos."
        )


    if "capital do brasil" in texto:

        return "A capital do Brasil é Brasília! 🇧🇷"


    if "piada" in texto:

        piadas = [
            (
                "Por que o computador foi ao médico? 😂\n\n"
                "Porque estava com um vírus! 🖥️"
            ),
            (
                "O que o zero disse para o oito?\n\n"
                "Belo cinto! 😂"
            ),
            (
                "Por que o livro de matemática ficou triste?\n\n"
                "Porque tinha muitos problemas! 😂🧮"
            )
        ]

        return random.choice(piadas)


    if "curiosidade" in texto:

        curiosidades = [
            (
                "Uma curiosidade: Vênus gira em sentido "
                "contrário ao da maioria dos planetas "
                "do Sistema Solar. 🌎"
            ),
            (
                "Uma curiosidade: o polvo possui três corações. 🐙"
            ),
            (
                "Uma curiosidade: a luz do Sol demora "
                "cerca de 8 minutos para chegar à Terra. ☀️"
            )
        ]

        return random.choice(curiosidades)


    if "como você está" in texto or "como voce esta" in texto:

        return (
            "Estou funcionando direitinho! 😎🤖\n\n"
            "E pronta para conversar com você."
        )


    if "o que você consegue fazer" in texto:

        return (
            "Eu consigo fazer algumas coisas! 🤖\n\n"
            "🧮 Resolver contas\n"
            "🧠 Guardar algumas informações\n"
            "🐍 Responder sobre Python\n"
            "💻 Explicar programação\n"
            "🤖 Explicar conceitos de IA\n"
            "😄 Conversar\n\n"
            "E estamos aumentando minhas capacidades aos poucos!"
        )


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

            return (
                f"Seu nome é {memoria['nome']}! 🧠"
            )

        return (
            "Você ainda não me contou seu nome. 😄"
        )


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
    ):

        resposta = resposta_matematica(texto)

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


    # RESPOSTA PADRÃO

    return (
        "Entendi! 🧠\n\n"
        "Ainda estou aprendendo, mas posso "
        "tentar entender se você explicar "
        "um pouco mais."
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

@app.route("/nova_conversa", methods=["POST"])
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