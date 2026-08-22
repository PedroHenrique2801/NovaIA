from flask import Flask, render_template, request, jsonify
import ast
import operator
import re
import unicodedata

app = Flask(__name__)

# =========================================================
# MEMÓRIA DA NOVAIA
# =========================================================

memoria = {
    "nome": None,
    "gosta": [],
    "nao_gosta": [],
    "assunto": None,
    "idioma": "portugues"
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
# NORMALIZAÇÃO DE TEXTO
# =========================================================

def remover_acentos(texto):

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    return "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )


def normalizar_abreviacoes(texto):

    substituicoes = {
        "vcs": "voces",
        "vc": "voce",
        "oq": "o que",
        "pq": "porque",
        "tbm": "tambem",
        "tb": "tambem",
        "blz": "beleza",
        "obg": "obrigado",
        "vlw": "valeu",
        "flw": "falou",
        "dps": "depois",
        "nn": "nao",
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
    texto = remover_acentos(texto)
    texto = normalizar_abreviacoes(texto)

    texto = re.sub(
        r"[?!.,;:]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()

# =========================================================
# IDIOMAS E TRADUÇÕES
# =========================================================

def resposta_idiomas(texto):

    if (
        "fale em ingles" in texto
        or "falar em ingles" in texto
        or "responda em ingles" in texto
        or "responder em ingles" in texto
    ):

        memoria["idioma"] = "ingles"

        return (
            "Okay! 🇺🇸🗣️\n\n"
            "A partir de agora posso responder em inglês."
        )

    if (
        "fale em russo" in texto
        or "falar em russo" in texto
        or "responda em russo" in texto
        or "responder em russo" in texto
    ):

        memoria["idioma"] = "russo"

        return (
            "Хорошо! 🇷🇺🗣️\n\n"
            "Agora posso responder em russo."
        )

    if (
        "fale em mandarim" in texto
        or "falar em mandarim" in texto
        or "responda em mandarim" in texto
        or "responder em mandarim" in texto
        or "fale em chines" in texto
    ):

        memoria["idioma"] = "mandarim"

        return (
            "好的! 🇨🇳🗣️\n\n"
            "Agora posso responder em mandarim."
        )

    if (
        "fale em portugues" in texto
        or "falar em portugues" in texto
        or "responda em portugues" in texto
        or "responder em portugues" in texto
        or "volte para portugues" in texto
    ):

        memoria["idioma"] = "portugues"

        return (
            "Beleza! 🇧🇷🗣️\n\n"
            "Voltei a responder em português."
        )

    traducoes = {

        "casa": {
            "ingles": "house 🏠",
            "russo": "дом 🏠",
            "mandarim": "房子 🏠"
        },

        "agua": {
            "ingles": "water 💧",
            "russo": "вода 💧",
            "mandarim": "水 💧"
        },

        "comida": {
            "ingles": "food 🍽️",
            "russo": "еда 🍽️",
            "mandarim": "食物 🍽️"
        },

        "escola": {
            "ingles": "school 🏫",
            "russo": "школа 🏫",
            "mandarim": "学校 🏫"
        },

        "amigo": {
            "ingles": "friend 🧑‍🤝‍🧑",
            "russo": "друг 🧑‍🤝‍🧑",
            "mandarim": "朋友 🧑‍🤝‍🧑"
        },

        "ola": {
            "ingles": "hello 👋",
            "russo": "привет 👋",
            "mandarim": "你好 👋"
        },

        "obrigado": {
            "ingles": "thank you 🙏",
            "russo": "спасибо 🙏",
            "mandarim": "谢谢 🙏"
        },

        "sim": {
            "ingles": "yes",
            "russo": "да",
            "mandarim": "是"
        },

        "nao": {
            "ingles": "no",
            "russo": "нет",
            "mandarim": "不"
        },

        "carro": {
            "ingles": "car 🚗",
            "russo": "машина 🚗",
            "mandarim": "汽车 🚗"
        },

        "cachorro": {
            "ingles": "dog 🐶",
            "russo": "собака 🐶",
            "mandarim": "狗 🐶"
        },

        "gato": {
            "ingles": "cat 🐱",
            "russo": "кошка 🐱",
            "mandarim": "猫 🐱"
        },

        "livro": {
            "ingles": "book 📖",
            "russo": "книга 📖",
            "mandarim": "书 📖"
        },

        "familia": {
            "ingles": "family 👨‍👩‍👧‍👦",
            "russo": "семья 👨‍👩‍👧‍👦",
            "mandarim": "家庭 👨‍👩‍👧‍👦"
        },

        "mae": {
            "ingles": "mother 👩",
            "russo": "мама 👩",
            "mandarim": "妈妈 👩"
        },

        "pai": {
            "ingles": "father 👨",
            "russo": "папа 👨",
            "mandarim": "爸爸 👨"
        },

        "sol": {
            "ingles": "sun ☀️",
            "russo": "солнце ☀️",
            "mandarim": "太阳 ☀️"
        },

        "lua": {
            "ingles": "moon 🌙",
            "russo": "луна 🌙",
            "mandarim": "月亮 🌙"
        },

        "dia": {
            "ingles": "day ☀️",
            "russo": "день ☀️",
            "mandarim": "天 ☀️"
        },

        "noite": {
            "ingles": "night 🌙",
            "russo": "ночь 🌙",
            "mandarim": "夜晚 🌙"
        },

        "feliz": {
            "ingles": "happy 😄",
            "russo": "счастливый 😄",
            "mandarim": "开心 😄"
        },

        "triste": {
            "ingles": "sad 😢",
            "russo": "грустный 😢",
            "mandarim": "悲伤 😢"
        },

        "bola": {
            "ingles": "ball ⚽",
            "russo": "мяч ⚽",
            "mandarim": "球 ⚽"
        },

        "futebol": {
            "ingles": "football ⚽",
            "russo": "футбол ⚽",
            "mandarim": "足球 ⚽"
        },

        "jogo": {
            "ingles": "game 🎮",
            "russo": "игра 🎮",
            "mandarim": "游戏 🎮"
        },

        "computador": {
            "ingles": "computer 💻",
            "russo": "компьютер 💻",
            "mandarim": "电脑 💻"
        },

        "telefone": {
            "ingles": "phone 📱",
            "russo": "телефон 📱",
            "mandarim": "手机 📱"
        }
    }

    padrao = re.search(
        r"como (?:fala|se fala|diz) (.+) em "
        r"(ingles|russo|mandarim|chines)",
        texto
    )

    if padrao:

        palavra = padrao.group(1).strip()
        idioma = padrao.group(2)

        if idioma == "chines":
            idioma = "mandarim"

        if palavra in traducoes:

            traducao = traducoes[palavra][idioma]

            nomes = {
                "ingles": "inglês 🇺🇸",
                "russo": "russo 🇷🇺",
                "mandarim": "mandarim 🇨🇳"
            }

            return (
                f'Em {nomes[idioma]}, "{palavra}" '
                f'é "{traducao}".'
            )

        return (
            "Ainda não tenho essa palavra no meu "
            "dicionário básico. 🧠\n\n"
            "Podemos adicionar mais palavras depois!"
        )

    if (
        "qual idioma voce esta falando" in texto
        or "qual idioma voce esta usando" in texto
        or texto == "qual idioma"
    ):

        nomes = {
            "portugues": "português 🇧🇷",
            "ingles": "inglês 🇺🇸",
            "russo": "russo 🇷🇺",
            "mandarim": "mandarim 🇨🇳"
        }

        return (
            f"Meu idioma atual é {nomes[memoria['idioma']]}."
        )

    return None

# =========================================================
# MEMÓRIA
# =========================================================

def analisar_memoria(texto):

    resultado = re.search(
        r"eu nao gosto de (.+)",
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
                f"{memoria['assunto']}."
            )

        partes.append(
            "Idioma atual: "
            + memoria["idioma"]
            + "."
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

        return "Você ainda não me contou do que não gosta."

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
            "Quando você executa um programa, o Python "
            "interpreta essas instruções e realiza as "
            "ações que você programou.\n\n"
            "Na NovaIA, o Python recebe sua mensagem, "
            "analisa as regras do programa e prepara "
            "uma resposta."
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
            "Na NovaIA, usamos Python no servidor."
        )

    if (
        "o que da para fazer" in texto
        or "o que da pra fazer" in texto
        or "o que posso fazer" in texto
        or "o que posso criar" in texto
    ):

        return (
            "Com Python dá para criar muitos projetos! 🐍🚀\n\n"
            "Calculadoras, programas, automações, servidores, "
            "jogos simples, ferramentas e sistemas.\n\n"
            "Python também é muito usado em inteligência "
            "artificial e análise de dados."
        )

    if (
        "o que e python" in texto
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
            "jogos, sistemas e automações."
        )

    if "como funciona" in texto:

        return (
            "Programação funciona através de instruções "
            "que o computador executa. 💻\n\n"
            "O programador escreve essas instruções usando "
            "uma linguagem de programação."
        )

    if (
        "o que e" in texto
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

    if not (
        "inteligencia artificial" in texto
        or "o que e ia" in texto
        or texto == "ia"
    ):
        return None

    if (
        "o que e inteligencia artificial" in texto
        or "o que e ia" in texto
    ):

        memoria["assunto"] = "inteligência artificial"

        return (
            "Inteligência Artificial, ou IA, é uma área "
            "da computação que busca criar sistemas capazes "
            "de realizar tarefas que normalmente exigiriam "
            "algum tipo de inteligência humana. 🤖🧠\n\n"
            "Uma IA pode analisar informações, reconhecer "
            "padrões, conversar e realizar várias tarefas."
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
            "que processam informações e identificam padrões. 🧠🤖\n\n"
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

    if "o que e uma fracao" in texto:

        return (
            "Uma fração representa uma parte de um todo. 🧮\n\n"
            "Por exemplo, 3/4 significa três partes de um "
            "total dividido em quatro partes iguais.\n\n"
            "O número de cima é o numerador e o número "
            "de baixo é o denominador."
        )

    if (
        "pra que serve" in texto
        or "para que serve" in texto
    ):

        return (
            "A matemática serve para resolver problemas "
            "e entender números, quantidades, formas e relações. 🧮"
        )

    return None

# =========================================================
# CIÊNCIAS
# =========================================================

def resposta_ciencias(texto):

    if "gravidade" in texto:

        memoria["assunto"] = "ciências"

        return (
            "A gravidade é uma força que atrai objetos "
            "que possuem massa. 🌎🧲\n\n"
            "Na Terra, ela faz os objetos serem atraídos "
            "em direção ao nosso planeta.\n\n"
            "A gravidade também mantém a Lua em órbita "
            "ao redor da Terra e ajuda a manter os planetas "
            "em órbita ao redor do Sol."
        )

    if "sistema solar" in texto:

        memoria["assunto"] = "ciências"

        return (
            "O Sistema Solar é formado pelo Sol e pelos "
            "corpos celestes que orbitam ao seu redor. ☀️🪐\n\n"
            "Existem oito planetas: Mercúrio, Vênus, "
            "Terra, Marte, Júpiter, Saturno, Urano e Netuno.\n\n"
            "O Sol é uma estrela e sua gravidade ajuda "
            "a manter os planetas em suas órbitas."
        )

    if (
        "atomo" in texto
        or "atomos" in texto
        or "o que significa atomo" in texto
        or "o que e um atomo" in texto
    ):

        memoria["assunto"] = "ciências"

        return (
            "Um átomo é uma unidade muito pequena que "
            "forma a matéria. ⚛️\n\n"
            "Ele possui um núcleo formado por prótons "
            "e nêutrons, e elétrons que ficam ao redor "
            "do núcleo."
        )

    if (
        texto == "sol"
        or "o que e o sol" in texto
        or "como funciona o sol" in texto
        or "como e o sol" in texto
    ):

        memoria["assunto"] = "ciências"

        return (
            "O Sol é uma estrela localizada no centro "
            "do Sistema Solar. ☀️\n\n"
            "Ele fornece luz e energia para a Terra "
            "e para os outros planetas."
        )

    if (
        texto == "lua"
        or "o que e a lua" in texto
        or "como funciona a lua" in texto
    ):

        memoria["assunto"] = "ciências"

        return (
            "A Lua é o satélite natural da Terra. 🌙🌎\n\n"
            "Ela não produz sua própria luz visível. "
            "A luz que vemos é a luz do Sol refletida "
            "pela superfície da Lua."
        )

    if "corpo humano" in texto:

        memoria["assunto"] = "ciências"

        return (
            "O corpo humano possui vários sistemas "
            "que trabalham juntos. 🧠🫀\n\n"
            "Entre eles estão o sistema respiratório, "
            "circulatório, digestório e nervoso."
        )

    if (
        "universo" in texto
        or "espaco" in texto
    ):

        memoria["assunto"] = "ciências"

        return (
            "O universo contém galáxias, estrelas, "
            "planetas e muitos outros objetos. 🌌✨\n\n"
            "A Terra faz parte do Sistema Solar, "
            "que fica na galáxia Via Láctea."
        )

    if (
        "ciencia" in texto
        or "cientifico" in texto
    ):

        memoria["assunto"] = "ciências"

        return (
            "Ciência é uma forma de estudar e entender "
            "o mundo usando observações, perguntas, "
            "experimentos e evidências. 🔬🧠"
        )

    return None

# =========================================================
# RESPOSTAS EXTRAS
# =========================================================

def resposta_extra(texto):

    if "quem criou voce" in texto:

        return (
            "Eu fui criada através de código! 🤖💻\n\n"
            "E você está desenvolvendo a NovaIA comigo."
        )

    if "voce e uma ia" in texto:

        return (
            "Sim! 🤖\n\n"
            "Eu sou a NovaIA, uma assistente virtual "
            "que estamos construindo com Python."
        )

    if "voce e inteligente" in texto:

        return (
            "Estou ficando cada vez melhor! 😎🧠\n\n"
            "Já consigo conversar, lembrar algumas "
            "informações, fazer contas e responder "
            "perguntas sobre vários assuntos."
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

    if "voce esta ai" in texto:

        return "Estou aqui! 🤖😎 Pode mandar."

    if "voce sabe meu nome" in texto:

        if memoria["nome"]:
            return f"Sei sim! Seu nome é {memoria['nome']}! 🧠"

        return "Ainda não. Me diga seu nome que eu posso lembrar."

    return None

# =========================================================
# CONVERSA
# =========================================================

def resposta_conversa(texto):

    if texto in [
        "oi",
        "ola",
        "oii",
        "oiii",
        "eai",
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

    if "entendi" in texto:

        return (
            "Boa! 😎🧠\n\n"
            "Se quiser continuar esse assunto, "
            "pode mandar outra pergunta."
        )

    if "nao entendi" in texto:

        return (
            "Sem problema! 😄\n\n"
            "Posso explicar de um jeito mais simples "
            "ou dar um exemplo."
        )

    if (
        "seu nome" in texto
        or "como voce se chama" in texto
    ):

        return (
            "Meu nome é NovaIA! 🤖\n\n"
            "Sou a assistente virtual que estamos "
            "construindo juntos."
        )

    if "quem e voce" in texto:

        return (
            "Eu sou a NovaIA! 🤖🧠\n\n"
            "Sou uma assistente virtual que estamos "
            "desenvolvendo juntos.\n\n"
            "Já consigo conversar, lembrar informações, "
            "entender abreviações, resolver contas e "
            "responder perguntas sobre vários assuntos."
        )

    if "capital do brasil" in texto:

        return "A capital do Brasil é Brasília! 🇧🇷"

    if "capital da franca" in texto:

        return "A capital da França é Paris! 🇫🇷"

    if "capital dos estados unidos" in texto:

        return "A capital dos Estados Unidos é Washington, D.C.! 🇺🇸🏛️\n\nWashington, D.C. é a capital federal dos Estados Unidos."

    if "capital do japao" in texto:

        return "A capital do Japão é Tóquio! 🇯🇵🗼\n\nTóquio é uma das maiores e mais importantes cidades do Japão."

    if (
        "formula da agua" in texto
        or "formula quimica da agua" in texto
    ):

        return (
            "A fórmula química da água é H₂O. 💧🧪\n\n"
            "Isso significa que cada molécula de água "
            "possui dois átomos de hidrogênio (H) e um "
            "átomo de oxigênio (O)."
        )

    if (
        "quantos planetas existem" in texto
        or "quantos planetas tem" in texto
        or "numero de planetas" in texto
    ):

        return (
            "Existem 8 planetas no Sistema Solar. 🪐🌎\n\n"
            "Eles são:\n\n"
            "1. Mercúrio ☿️\n"
            "2. Vênus 🟡\n"
            "3. Terra 🌎\n"
            "4. Marte 🔴\n"
            "5. Júpiter 🟠\n"
            "6. Saturno 🪐\n"
            "7. Urano 🔵\n"
            "8. Netuno 🔵\n\n"
            "O Sol é uma estrela e fica no centro do Sistema Solar. ☀️"
        )

    if (
        "maior planeta do sistema solar" in texto
        or "qual e o maior planeta" in texto
    ):

        return (
            "O maior planeta do Sistema Solar é Júpiter! 🪐\n\n"
            "Júpiter é um gigante gasoso e é o maior dos "
            "oito planetas do Sistema Solar. 🌌"
        )

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
# GERAR RESPOSTA
# =========================================================

def gerar_resposta(mensagem):

    texto = normalizar_texto(mensagem)

    # -----------------------------------------------------
    # NOME
    # -----------------------------------------------------

    if texto.startswith("meu nome e "):

        nome = mensagem[len("meu nome é "):].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄\n\n"
            "Agora vou lembrar do seu nome."
        )

    if texto.startswith("me chamo "):

        nome = mensagem[len("me chamo "):].strip()

        memoria["nome"] = nome

        return (
            f"Prazer em te conhecer, {nome}! 😄"
        )

    if (
        "qual e meu nome" in texto
        or "qual e o meu nome" in texto
        or "qual meu nome" in texto
        or "como eu me chamo" in texto
    ):

        if memoria["nome"]:
            return f"Seu nome é {memoria['nome']}! 🧠"

        return "Você ainda não me contou seu nome. 😄"

    # -----------------------------------------------------
    # MEMÓRIA
    # -----------------------------------------------------

    resposta = analisar_memoria(texto)

    if resposta is not None:
        return resposta

    resposta = responder_memoria(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # IDIOMAS
    # -----------------------------------------------------

    resposta = resposta_idiomas(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # CIÊNCIAS
    # -----------------------------------------------------

    resposta = resposta_ciencias(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # PYTHON
    # -----------------------------------------------------

    if "python" in texto:

        resposta = resposta_python(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # IA
    # -----------------------------------------------------

    if (
        "inteligencia artificial" in texto
        or "o que e ia" in texto
        or texto == "ia"
    ):

        resposta = resposta_ia(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # PROGRAMAÇÃO
    # -----------------------------------------------------

    if (
        "programacao" in texto
        or "programar" in texto
    ):

        resposta = resposta_programacao(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # MATEMÁTICA
    # -----------------------------------------------------

    if (
        "matematica" in texto
        or "fracao" in texto
    ):

        resposta = resposta_matematica(texto)

        if resposta is not None:
            return resposta

    # -----------------------------------------------------
    # EXTRAS
    # -----------------------------------------------------

    resposta = resposta_extra(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # CONVERSA
    # -----------------------------------------------------

    resposta = resposta_conversa(texto)

    if resposta is not None:
        return resposta

    # -----------------------------------------------------
    # CALCULADORA CORRIGIDA
    # -----------------------------------------------------

    expressao = texto

    padroes_calculadora = [
        "qual e o resultado de",
        "qual o resultado de",
        "resultado de",
        "quanto e",
        "calcule",
        "calcula"
    ]

    for padrao in padroes_calculadora:

        if expressao.startswith(padrao):

            expressao = expressao[
                len(padrao):
            ].strip()

            break

    # Aceita perguntas como:
    # quanto é 100 + 250
    # calcule 25 + 37
    # resultado de 50 * 2

    resultado = calcular(expressao)

    if resultado is not None:

        memoria["assunto"] = "matemática"

        return (
            "O resultado é "
            + formatar_resultado(resultado)
            + " 🧮"
        )

    # -----------------------------------------------------
    # RESPOSTA PADRÃO
    # -----------------------------------------------------

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
# ABRIR CONVERSA
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

    if conversa_encontrada["titulo"] == "Nova conversa":

        titulo = mensagem[:30]

        if len(mensagem) > 30:
            titulo += "..."

        conversa_encontrada["titulo"] = titulo

    resposta = gerar_resposta(mensagem)

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