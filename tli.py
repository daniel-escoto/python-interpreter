#! /usr/bin/env python3

import fileinput
import sys

# used to store a parsed TL expressions which are
# constant numbers, constant strings, variable names, and binary expressions
class Expr :
    def __init__(self,op1,operator,op2=None):
        self.op1 = op1
        self.operator = operator
        self.op2 = op2

    def __str__(self):
        if self.op2 == None:
            return self.operator + " " + self.op1
        else:
            return self.op1 + " " + self.operator + " " +  self.op2

    # evaluate this expression given the environment of the symTable
    def eval(self, symTable, lineNumber):
        if self.operator == "var":
            try:
                return symTable[self.op1]
            except KeyError:
                print("Undefined varible", self.op1, "at line", lineNumber)
                sys.exit()

        elif self.operator == "label":
            return symTable[self.op1]

        elif self.operator == "num":
            try:
                return (float)(self.op1)
            except KeyError:
                print("Undefined varible", self.op1, "at line", lineNumber)
                sys.exit()

        elif self.operator == "constStr":
            return self.op1

        elif self.operator == "+":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) + float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "-":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) - float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "*":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) * float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "/":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) / float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "<":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) < float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == ">":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) > float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "<=":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) <= float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == ">=":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) >= float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "==":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) == float(self.op2.eval(symTable, lineNumber)) )

        elif self.operator == "!=":
            return (float) ( float(self.op1.eval(symTable, lineNumber)) != float(self.op2.eval(symTable, lineNumber)) )

        # Used to detect syntax errors when an unknown operator is used.
        else:
            print("Syntax error on line {}.".format(lineNumber+1))
            sys.exit()
            return 0

# used to store a parsed TL statement
class Stmt :
    def __init__(self,keyword,exprs):
        self.keyword = keyword
        self.exprs = exprs

    def __str__(self):
        others = ""
        for exp in self.exprs:
            others = others + " " + str(exp)
        return self.keyword + others

    
# Given a string(line) and line number, this method produces a statement object
def parseStmt(line, lineNum):
    splitLine = line.split(' ')
    keyword = splitLine[0]
    if keyword == "input":
        s = Stmt('input', Expr(splitLine[1], "var"))
        return s

    elif keyword == "let":
        subString = splitLine[3:]
        s = Stmt( 'let', [ splitLine[1], stringToExpr(subString) ] )
        return s

    elif keyword == "if":
        subString = splitLine[1:4]
        s = Stmt( "if", [ stringToExpr(subString), Expr(splitLine[-1], "label") ] )
        return s

    elif keyword == "print":
        subString = line[6:]
        expressions = subString.split(" , ")

        listOfExpressions = []
        for exp in expressions:
            if (exp.startswith('"') and exp.endswith('"')):
                exp = exp[1:] # remove first quotation mark
                exp = exp[:-1] # remove second quotation mark
                listOfExpressions.append(Expr(exp, "constStr"))
            else:
                listOfExpressions.append(  stringToExpr(exp) )

        s = Stmt("print", listOfExpressions)
        return s

    # Detects a label in the string, then removes it from the statement to parse.
    elif keyword[-1] == ':':
        s = parseStmt(line.split(' ', 1)[1], lineNum)
        return s

    # This detects a syntax error when none of the above cases are reached.
    else:
        print("Syntax error on line {}.".format(lineNum))
        sys.exit()

# converts str to expr
def stringToExpr(words):
    if type(words) == str:
        return Expr(words, 'var')
    else:
        if len(words) == 1:
            if words[0].isdigit():
                return Expr(words[0], 'num')
            else:
                return Expr(words[0], 'var')
        else:
            firstTerm = words[0]
            secondTerm = words[2]
            if firstTerm.isdigit():
                firstExpr = Expr(words[0], 'num')
            else:
                firstExpr = Expr(words[0], 'var')

            if secondTerm.isdigit():
                secondExpr = Expr(words[2], 'num')
            else:
                secondExpr = Expr(words[2], 'var') 

            return Expr(firstExpr, words[1], secondExpr)

# This method prepares the Stringlist into a form that parseStmt can recieve.
def prepareParse(StringList, LabelAndVarDict, StatementList):
    # for loop accesses every string
    for i in range(len(StringList)):
        currentLineNumber = i+1
        firstWord = StringList[i].replace('\t', ' ')
        firstWord = firstWord.split(' ', 1)[0]
        remainingString = StringList[i].split(None, 1)[1:][0]
        if firstWord.endswith(':') or firstWord.endswith(':\t'):
            LabelAndVarDict[firstWord] = currentLineNumber
            StatementList.append(parseStmt(remainingString, currentLineNumber))
        else:
            StatementList.append(parseStmt(StringList[i], currentLineNumber))

# This method runs statements.
def runStatements(LabelAndVarDict, StatementList, ShortenedStmtList):
    for statement in ShortenedStmtList:
        if statement.keyword == "input":
            chosenVariable = statement.exprs.op1

            # Detects illegal or missing inputs
            try:
                userInput = float(input())
            except ValueError:
                print("Illegal or missing input")
                sys.exit()


            userInput = float(input())
            LabelAndVarDict[chosenVariable] = userInput

        elif statement.keyword == "let":
            chosenVariable = Expr(statement.exprs[0], "var")
            solvedExpression = statement.exprs[1].eval(LabelAndVarDict, StatementList.index(statement))
            LabelAndVarDict[chosenVariable.op1] = solvedExpression
            

        elif statement.keyword == "if":
            tempList = StatementList.copy()
            passingExpressionOutcome = statement.exprs[0].eval(LabelAndVarDict, StatementList.index(statement))
            labelName = statement.exprs[1].op1 + ":"
            labelLocation = LabelAndVarDict[labelName]
            if passingExpressionOutcome == 1.0:
                runStatements(LabelAndVarDict, StatementList, tempList[labelLocation-1:])
                break

        elif statement.keyword == "print":
            # stringToPrint is used to print multiple statements on the same line.
            stringToPrint = ""
            for expr in statement.exprs:

                # i.e. print "hello world"
                if expr.operator == "constStr":
                    stringToPrint = stringToPrint + (expr.op1) + " "
                else:
                    # i.e. print x + y
                    if " " in expr.op1:
                        temp = stringToExpr(expr.op1).op1
                        temp = temp.split(" ")
                        tempExpr = Expr(stringToExpr(temp[0]), temp[1], stringToExpr(temp[2]))
                        stringToPrint =  stringToPrint + str(tempExpr.eval(LabelAndVarDict, StatementList.index(statement))) + " "
                    else:
                        # i.e. print x
                        try:
                            stringToPrint = stringToPrint + str(LabelAndVarDict[expr.op1]) + " "
                        except KeyError:
                            print("Undefined variable", expr.op1, "at line", StatementList.index(statement)+1)
                            sys.exit()
            print(stringToPrint)        


# Begin Run

# Recieve input file, convert to list of strings without \n1
fileName = sys.argv[1]
lineList = [line.strip() for line in open(fileName)]

env = {} # variables and labels
linedStmts = [] # lineNumber:Stmt

prepareParse(lineList, env, linedStmts)
runStatements(env, linedStmts, linedStmts)

# End Run