""" Shared utilities for all modules. """

def print_header(header):
    text = "*"*80 + '\n'
    text += "*"*80 + '\n'
    text += "**" + " "*76+"**"+"\n"
    text += "**" +header.center(76)+"**"+"\n"
    text += "**" + " "*76+"**"+"\n"
    text += "*"*80 + '\n\n'
    print text

