import string
import os
import sys
import time


HEADER = """
Wellcome to ALang!

for help type 'help'
"""

PS = "$ "
CPS = ""
SP = "\"'"
ex = "+-*/"
CMNT = "//"
MCSTART = "/*"
MCEND = "*/"
ACCEPTET = "\"'" + string.digits + string.ascii_letters
CMPKW = ["=="]
GLOBALS = {
    "INCMNT": False,
    "BLOCK": 0,
    "CMP": 0,
    "CLINE": 0,
    "NEXT": 0,
    "LI": 0,
    "PN": [],
    "PLI": []
}

VARS = {
    "__STRICT": 0,
}

# print("Hello world!")


def _print(args) -> None:
    for t in args:
        print(t, end="")
    print("")

# expr("1 + 5") -> 6


def _expr(args) -> int:
    return eval(args[0])

# clear


def _clear(args) -> None:
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

# help


def _help(args) -> None:
    for name in HELPER:
        print(f"{name}: {HELPER.get(name)}")

# set("x", 5) -> x = 5


def _setVal(args):
    name = args[0]
    if not isValidAsi(name):
        raise ValueError(
            f"Invalid name '{name}', names cannot start with a digit")
    val = args[1]
    VARS[name] = val

# get("x") -> 5


def _getVal(args) -> None:
    print(VARS[args[0]])

# five -> 5


def _five(args) -> int:
    return 5

# wait(1)


def _wait(args: list) -> None:
    time.sleep(args[0] if len(args) > 0 else 1)

# strict -> __STRICT = 1


def _strict(args) -> None:
    VARS["__STRICT"] = 1
"""
cmp(x == 5)
    print("True") // no need for indentation
endcmp
"""

def _cmp(args):
    global CPS
    res = args[0]

    if not res:
        GLOBALS["CMP"] = 1
    cmpps = "\t"
    CPS = cmpps if PS.find(cmpps) == -1 else PS


def _ecmp(args):
    global CPS
    if len(CPS) == 0:
        raise ValueError("Thare is no cmp to end!")
    GLOBALS["CMP"] = 0
    CPS = ""

def _forloop(args):
    s: str = args[0]
    s = s.translate({ord(" "): ""})
    r, l = s.split("in")
    _setVal([r,l])
    if GLOBALS["NEXT"] != 0:
        GLOBALS["PN"].append(GLOBALS["NEXT"])
    
    GLOBALS["NEXT"] = GLOBALS["CLINE"]
    if GLOBALS["LI"] != 0:
        GLOBALS["PLI"].append(GLOBALS["LI"])
    GLOBALS["LI"] = int(l)-1

def _endloop(args):
    if GLOBALS["LI"] <= 0:
        GLOBALS["NEXT"] = 0 if len(GLOBALS["PN"]) == 0 else GLOBALS["PN"].pop()
        if len(GLOBALS["PLI"]) != 0:
            GLOBALS["LI"] = GLOBALS["PLI"].pop()
        return

    if GLOBALS["NEXT"] > 0:
        GLOBALS["CLINE"] = GLOBALS["NEXT"]
        GLOBALS["LI"] -= 1
        return


HELPER = {
    "print": "prints stuff to the stdout",
    "exit": "exits the program",
    "clear": "clears the terminal output",
    "expr": "math expretions",
    "set": "sets a variable to a value",
    "get": "get a variable value",
    "five": "returns the number five",
    "help": "helpful stuff about this language"
}


MAPPER = {"print": _print, "exit": exit, "clear": _clear, "five": _five, "expr": _expr, "set": _setVal,
          "get": _getVal, "wait": _wait, "STRICT": _strict, "cmp": _cmp, "compare": _cmp, "endcmp": _ecmp,
          "endcompare": _ecmp, "help": _help, "for": _forloop, "endloop": _endloop
          }


def toUsableStr(text: str) -> str:
    while (text[0] == " " or text[0] not in ACCEPTET):
        text = text[1:]
    while (text[-1] == " " or text[-1] not in ACCEPTET):
        text = text[:len(text) - 1]
    return text


def toExpr(text) -> int:
    sText = list()
    text = text.translate({ord(" "): ""})
    tmp = text
    for e in ex:
        tmp = tmp.replace(e, " ")

    sText = tmp.split(" ")
    for i in sText:
        i = i.translate({ord(" "): "", ord("\n"): ""})
        text = text.replace(i, str(getType(i)))
    return int(eval(text))


def getFuncName(text: str) -> str:
    first = text.find("(") if text.find("(") != -1 else len(text)
    space = text.find(" ") if text.find(" ") != -1\
        and text.find(" ") < first else 0
    first = first - (first - space) if space > 0 else first
    return toUsableStr(text[:first])


def encodeSp(text: str) -> str:
    for s in SP:
        if s in text:
            text = text.replace(f"\\{s}", "\\" + str(ord(s)))
    return text


def decodeSp(text: str) -> str:
    for s in SP:
        text = text.replace("\\" + str(ord(s)), s)
    return text


def toString(text: str) -> str:
    text = text.replace("\\n", "\n").replace("\\t", "\t")
    text = encodeSp(text)
    first = text.find("\"")
    if first == -1:
        return None
    text = text[first+1:]
    first = text.find("\"")
    if first == -1:
        return None
    text = text[:first]
    text = decodeSp(text)
    return text


def getType(text: str):

    s = toString(text)
    if s:
        return s
    if text in VARS:
        return VARS[text]
    text = text.translate({ord(" "): ""})
    isD = 0
    for c in text:
        if c in string.digits:
            isD += 1
    if len(text) - isD == 0:
        return int(text)
    for kw in CMPKW:
        if kw in text:
            return toCmp(text, kw)
    for e in ex:
        if e in text:
            expr = toExpr(text)
            if expr != None:
                return expr
    f, a, blk = toFunc(text)
    if f and blk == 0:
        return f(a)
    raise TypeError(f"{text} has no known types.")
    return text


def toFunc(text: str):
    fName: str = getFuncName(text).replace("\n", "")
    if fName not in MAPPER:
        return None, None, None
    args: list = getFuncArgs(text)

    return MAPPER[fName], args, GLOBALS["CMP"]


def getFuncArgs(text: str) -> list:
    first = text.find("(")
    last = text[first:].find(")")
    if last == -1 and first == -1:
        return []
    elif last == -1 or first == -1:
        raise TypeError(f"Invalid function call '{text}'.")
    argsText: str = text[first+1:][:last]
    argsList = argsText.split(",")
    if len(argsList) <= 1 and argsList[0] == ')':
        return []
    for i, arg in enumerate(argsList):
        arg = toUsableStr(arg)
        argsList[i] = getType(arg)

    return argsList


def toCmp(text: str, cmpType) -> int:
    l, r = text.split(cmpType)
    l, r = (toUsableStr(l), toUsableStr(r))
    l, r = (getType(l), getType(r))
    if "==" in cmpType:
        return int(l == r)

def isValidAsi(name: str):
    if name[0] in string.digits:
        return False
    return True



def toAsi(text: str) -> bool:
    first = text.find("=") if text.find("=") != -1 else len(text)
    itext = text[:first]
    space = itext.find(" ") if itext.find(" ") != - \
        1 and itext.find(" ") < first else 0
    name = itext if space == 0 else itext[:space]
    vi = text[first:][1:]
    if not isValidAsi(name):
        raise ValueError(
            f"Invalid name '{name}', names cannot start with a digit")

    for v in vi:
        vi = toUsableStr(vi)
    name = toUsableStr(name)
    VARS[name] = getType(vi)
    return name in VARS and (VARS["__STRICT"] == 0 or VARS[name] != None)


def toInst(text: str):
    if text[:2] == MCSTART:
        GLOBALS["INCMNT"] = True
        return
    elif text.find(MCEND) != -1:
        GLOBALS["INCMNT"] = False
        return
    if text[:2] == CMNT or GLOBALS["INCMNT"]:
        return
    func, args, cmp = toFunc(text)
    if func:
        if cmp == 0 or func == _ecmp:
            func(args)
        return
    if "=" in text:
        if toAsi(text):
            return

    raise TypeError(f"Invalid syntax '{text[:-1]}' is undefined!")


def main():
    while True:
        i = input(CPS if CPS else PS)
        toInst(i)


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc == 1:
        print(HEADER)
        main()

    if argc > 2:
        print(f"Usage: {sys.argv[0]} <file>")
        exit()

    maxLines = 0
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
        maxLines = len(lines) 
        while GLOBALS["CLINE"] < maxLines:
            line = lines[GLOBALS["CLINE"]]
            nlchk = line.translate({ord(" "): ""})
            GLOBALS["CLINE"] += 1
            if nlchk == "\n":
                continue
            toInst(line)
