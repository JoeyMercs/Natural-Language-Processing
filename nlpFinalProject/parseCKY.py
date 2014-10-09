# Joseph Mercedes
# parseCKY.py
# Parses a sentence and outputs all the associated trees using the CKY Algorithm and a CFG in CNF

import nltk
import sys
import re

# Class for Context Free Grammars in Chomsky Normal Form
class CNFGrammar:

    # Reads a CFG and creates all lexical/phrasal tree productions
    def __init__(self, path):

        self.lexical = {}  # unary branching grammar productions
        self.phrasal = {}  # binary branching grammar productions
        self.start = None  # start symbol

        with open(path) as grammarFile:
            grammarText = grammarFile.read()

        grammarText = grammarText.strip()
        grammarLines = grammarText.split("\n")

        production = r"""^(\w+)\s*->\s*(\w+\s+\w+|'\S+'|"\S+")$"""
        quoted = r"""^"\S+"|'\S+'$"""
        PRODUCTION = re.compile(production)
        QUOTED = re.compile(quoted)

        for line in grammarLines:
            prod_match = PRODUCTION.match(line)
            if prod_match:
                lhs, rhs = prod_match.group(1), prod_match.group(2)
                if not self.start:
                    self.start = lhs
                quot_match = QUOTED.match(rhs)
                if quot_match:
                    prod_type = "lexical"
                else:
                    prod_type = "phrasal"
                    rhs = rhs.split()
                rule_map = getattr(self, prod_type)
                if lhs not in rule_map:
                    rule_map[lhs] = []
                rule_map[lhs].append(rhs)

    # Returns a list of non-terminal symbols by searching lexical/phrasal productions
    def lhsRhs(self, rhs, structure_type):

        nonterminals = []
        productions = getattr(self, structure_type)
        for lhs in productions:
            if rhs in productions[lhs]:
                nonterminals.append(lhs)
        return nonterminals

# Node class for nodes places into the parse chart
class Node:

    def __init__(self, symbol, left=None, right=None, terminal=None):
        
        self.symbol = symbol
        self.left = left
        self.right = right
        self.terminal = terminal

    def __str__(self):
        
        return """({0} -> {1} {2})""".format(self.symbol, str(self.left), str(self.right))

# Parsing Algorithm Class
class CKYParser:
    
    def __init__(self, path):

        self.grammar = CNFGrammar(path)

    def parse(self, sentence):

        N = len(sentence)

        # (N+1)x(N+1) matrix
        self.chart = [(N+1)*[None] for row_label in xrange(N+1)]
        for j in xrange(1, N+1):
            token = sentence[j-1]
            self.chart[j-1][j] = map(lambda preterm: Node(preterm, terminal=token), self.grammar.lhsRhs(token, "lexical"))
            for i in reversed(xrange(0, j-1)):
                for k in xrange(i+1, j):
                    lcandidates = self.chart[i][k]  # candidate left branches
                    rcandidates = self.chart[k][j]  # candidate right branches
                    # Examine all node pairs from two split cells, check if node pair is on RHS of any production, and add node to appropriate cell
                    if lcandidates and rcandidates:
                        for lnode in lcandidates:
                            lsymbol = lnode.symbol
                            for rnode in rcandidates:
                                rsymbol = rnode.symbol
                                msymbols = self.grammar.lhsRhs([lsymbol, rsymbol], "phrasal")
                                if msymbols and self.chart[i][j] is None:
                                    self.chart[i][j] = []
                                for msymbol in msymbols:
                                    self.chart[i][j].append(Node(msymbol, lnode, rnode))

    # Return a string representation of a parse given the root node of a parse
    def parseToString(self, node):
        
        if node.left and node.right:
            inside = "{0} {1}".format(self.parseToString(node.left), self.parseToString(node.right))
        else:
            inside = "{0}".format(node.terminal)
        return "({0} {1})".format(node.symbol, inside)

    # Return a list of string representations of all parses given a sentence
    def getParses(self, sentence):
        
        self.parse(sentence)
        N = len(sentence)
        parseRoots = self.chart[0][N]
        result = []
        if parseRoots: # guard against None
            for root in parseRoots:
                if root.symbol == self.grammar.start:
                    result.append(self.parseToString(root))
        return result




# Returns parses as a strings
def printParses(parses):
    
    output = ''
    
    for parse in parses:
        parse = parse.split()
        output += printTree(parse)
        output += '\n\n'
    
    return output

# Returns indented tree representation of given parse
def printTree(parse):
    
    string = parse[0]
    openParen = 1
    depth = 1
    index = 1
    
    while openParen > 0 and index < len(parse):
        if not re.match(r"'", parse[index]):
            string += '\n' + '  ' * depth + parse[index]
            openParen += 1
            depth = openParen
        else:
            string += ' ' + re.sub("'", "", parse[index])
            openParen -= closeParen(parse[index])
            depth = openParen
            
        index += 1
                
    return string
    
# Returns number of close parentheses attached to a token
def closeParen(string):
    
    num = 0
    index = -1
    
    while string[index] == ')':
        num += 1
        index -= 1

    return num

# Main loop to output parse tree
def main():
    
	try:
		sentPath = sys.argv[1]
	except IndexError:
		exit("Please give a path to a file of sentences.")

	try:
		gramPath = sys.argv[2]
	except IndexError:
		exit("Please give a path to a file with a grammar.")

	with open(sentPath) as sentence_file:
		sentData = sentence_file.read()

	sentences = sentData.strip().split("\n")
	sentences = [nltk.wordpunct_tokenize(sentence) for sentence in sentences]

	parser = CKYParser(gramPath)

        delim = 50 * "-"
        
	for sentence in sentences:
		sentence = ["'{0}'".format(token) for token in sentence]
		parses = parser.getParses(sentence)
		sys.stdout.write(printParses(parses))
		print len(parses)
                print delim

if __name__ == "__main__":
    main()
