# NLP Final Project
# myCNF.py
# Converts Context Free Grammar to Chomsky Normal Form

import sys

ruleMap = {}

# Returns a list of terminals and their indices in the given rule
def findTerm(rule):
    terminals = []
    indices = []
    j = 0
    for item in rule:
        if item[0] == "'":
            terminals.append(item)
            indices.append(j)
        j += 1
    
    return terminals, indices

# Returns a string representation of the given rule
def stringify(rule):
    string = rule[0] + ' ->'
    for item in rule[1:]:
        string += ' ' + item
    string += '\n'
    
    return string

# Adds a rule to the dictionary of rules
def addRule(rule):
    
    global ruleMap
    
    if rule[0] not in ruleMap:
        ruleMap[rule[0]] = []
    ruleMap[rule[0]].append(rule[1:])

# Replaces the terminals in the given rule with new nonterminals, adds new rules to the output, and returns altered rule
def replaceTerm(rule, terminals, indices, i):
    
    string = ''
    
    for j in range(len(indices)):
        newNode = 'X' + str(i)
        rule[indices[j]] = newNode
        string += stringify([newNode] + [terminals[j]])
    
    return string, rule

# Replaces first two elements in given rule with a new nonterminal, adds new rule to the output, and returns altered rule
def replaceLong(rule, i):
    
    newNode = 'X' + str(i)
    string = stringify([newNode] + rule[1:3])
    rule = [rule[0]] + [newNode] + rule[3:]
    
    return string, rule

# Converts long/multiple productions to CNF form and adds string to output
def convertLM(filename):
    
    output = ''
    reserves = []
    i = 1
    top = ''
    tops = ''
    first = True
    
    with open(filename) as f:
        while True:
            line = f.readline()
            if line == '':
                break
            line = line.strip()
            
            # Don't process commented/empty lines
            if line != '' and line[0] != '#':
                line = line.split('->')
                lhs = line[0].strip()
                
                # Store initial symbol
                if first:
                    top = lhs
                    first = False
                    
                rhs = line[1:][0].strip().split('|')
                
                for item in rhs:
                    rule = [lhs] + item.split()
                    skip = False
                    
                    # Reserve unit productions for the end
                    if len(rule) == 2 and rule[1][0] != "'":
                        reserves.append(rule)
                        skip = True
                    
                    # If not a terminal
                    elif len(rule) > 2:
                        
                        # Find multiple rules
                        terminals, indices = findTerm(rule)
                        if len(terminals) > 0:
                            string, rule = replaceTerm(rule, \
                                terminals, indices, i)
                            if rule[0] == top:
                                tops += string
                            else:
                                output += string
                            i += 1
                            
                        # Convert long productions
                        while len(rule) > 3:
                            string, rule = replaceLong(rule, i)
                            if rule[0] == top:
                                tops += string
                            else:
                                output += string
                            i += 1
                    
                    addRule(rule)
                    
                    if not skip:
                        if rule[0] == top:
                            tops += stringify(rule)
                        else:
                            output += stringify(rule)
                        
    return top, tops, output, reserves

# Conerts unit productions to CNF form and adds to output string
def convertUnit(reserves, top):
    
    global ruleMap
    output = ''
    tops = ''
    
    # Convert unit productions 
    while len(reserves) > 0:
        rule = reserves.pop()
        if rule[1] in ruleMap:
            for item in ruleMap[rule[1]]:
                newRule = [rule[0]] + item
                
                # If not a unit production anymore, then output
                if len(newRule) > 2 or newRule[1][0] == "'":
                    if newRule[0] == top:
                        tops += stringify(newRule)
                    else:
                        output += stringify(newRule)
                
                # If still a unit production, then recycle
                else:
                    reserves.append(newRule)
                    
                addRule(newRule)
        
    return tops, output

# Reads in CFG file, converts to Chomsky Normal Form, and outputs to a file
def main():
        
    if len(sys.argv) < 3:
        sys.stdout.write('Comverter takes two arguments: \
            [input_grammar_file] [out_file]\n')
        sys.exit()
    
    top, tops, output, reserves = convertLM(sys.argv[1])
    results = convertUnit(reserves, top)
    tops += results[0]
    output += results[1]
    
    with open(sys.argv[2], 'w') as f:
        f.write(tops)
        f.write(output)

main()
