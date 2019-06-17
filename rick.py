import random

# This is an easter egg made by Schlumpy

combos = ["grum", "flub", "choob", "flib", "shnub", "grup", "bop", "flark", "shnip", "frik", "frork", "frum", "glub",
          "gloob", "frumble", "pomple", "craks", "grooble", "shelm", "shleem", "grumbo", "dongle", "dangle", "fribble",
          "dibble", "dab", "dap", "frip", "shornk", "shrunk", "krenk", "kronk", "aloo", "alube", "broop", "brumble",
          "brak", "cruie", "zap", "shrup"]


def generate_name(syllables):
    wordstring = ""
    for i in range(syllables):
        rand = random.choice(combos)
        wordstring = wordstring + rand
    return wordstring


def name_creator(wordcount, syllables):
    names = ""
    for i in range(int(wordcount)):
        names = names + " " + generate_name(syllables)
    return names
