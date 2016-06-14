# Please note the names of the factors and True and False start with capital letters

print ('''Please note that the name of the factors and values are case sensitive. 
    Here is the name of the factors and the values. 
    factors: Fraud,   IP,   CRP,   OC,   Travel,   FP
    Values: True, False
    Example: P(IP| Travel=True, OC=True) 
    ''')

import copy

while(True):
    # These are the factors and their probabilities
    Travel = [["Travel", "Travel"],
             [True, .05],
             [False, .95]]

    FP = [["Travel", "Fraud", "FP"],
         [True, True, True, .9],
         [True, True, False, .1],
         [True, False, True, .9],
         [True, False, False, .1],
         [False, True, True, .1],
         [False, True, False, .9],
         [False, False, True, .01],
         [False, False, False, .99]]

    Fraud = [["Travel", "Fraud"],
            [True, True, .01],
            [True, False, .99],
            [False, True, .002],
            [False, False, .998]]

    OC = [["OC", "OC"],
         [True, .6],
         [False, .4]]

    IP = [["OC", "Fraud", "IP"],
         [True, True, True, .02],
         [True, True, False, .98],
         [True, False, True, .01],
         [True, False, False, .99],
         [False, True, True, .011],
         [False, True, False, .989],
         [False, False, True, .001],
         [False, False, False, .999]]

    CRP = [["OC", "CRP"],
          [True, True, .1],
          [True, False, .9],
          [False, True, .001],
          [False, False, .999]]

    #Name of the factors and their dictionaries
    names = {"Travel":Travel, "FP":FP, "Fraud":Fraud, "OC":OC, "IP":IP, "CRP":CRP}

    #The factors and their dependant factors
    links = {"FP":[Travel, Fraud], "Fraud":[Travel], "IP":[Fraud, OC, Travel], "CRP":[OC]}

    def str2bool(v):
        return v in ("True")


    def restrict(factor, variable, value): # This function restrics the factor based on the value of a variable
        cnt = 0 
        new_factor = []
        for var in factor[0]:
            if var == variable:
                break
            cnt += 1
        first_row = copy.deepcopy(factor[0])
        if cnt != len(first_row)-1:
            del first_row[cnt]
        new_factor.append(first_row)
        for row in factor[1:]:
            if row[cnt] == value:
                del row[cnt]
                new_factor.append(row)
        return new_factor


    def multiply(factor1, factor2): # This function multiplies two given factors 

        if len(factor1[1]) < len(factor2[1]):
            A = copy.deepcopy(factor1)
            B = copy.deepcopy(factor2)
        else:
            A = copy.deepcopy(factor2)
            B = copy.deepcopy(factor1)
        p = {}
        factor = []
        p[A[1][0]] = A[1][1]
        p[A[2][0]] = A[2][1]
        variable = A[0][0]
        factor.append(B[0])
        cnt = 0 
        for var in B[0]:
            if var == variable:
                break
            cnt += 1
        for row in B[1:]:
            value = row[cnt]
            x = row[-1]*p[value]
            row[-1] = round(x, 15)
            factor.append(row)
        return factor

    def sumout(factor, variable): # This function sums out a varibale given the factor
        p = {}
        cnt = 0 
        new_factor = copy.deepcopy(factor)
        for var in factor[0]:
            if var == variable:
                break
            cnt += 1
        for row in new_factor:
            del row[cnt]
        for row in new_factor[1:]:
            tokens = str(row[0])
            for token in row[1:-1]:
                tokens = tokens + " " + str(token)
            if tokens not in p:
                p[tokens] = row[-1]
            else:
                p[tokens] += row[-1]
        final = []
        final.append(new_factor[0])
        for row in p:
            tokens = row.split(" ")
            temp = []
            for token in tokens:
                temp.append(str2bool(token))
            temp.append(round(p[row],15))
            final.append(temp)
        return final

    def pick(factors): # This function decides which two factors we choose to mulitply and then sum out
        for factor in factors:
            if len(factor[1]) == 2:
                a = factor
                break
        name = a[0][0]
        b = []
        for factor in factors:
            if len(factor[1]) > 2:
                if name in factor[0]:
                    if b == []:
                        b = factor
                    else:
                        if len(factor) < len(b):
                            b = factor
        return [a, b, name]


    def inference(Q, args): # This is the main function that uses all previous functions and calculates the probabilities of a given query
        try:
            Query = [key for key, value in names.iteritems() if value == Q][0]
            factors = [Q]
            evidences = []

            if len(args) > 0:
                for arg in args: # arg in a list of [factor, value]
                    factors.append(arg[0])
                    evidences.append(arg)


            for factor in factors:
                name = [key for key, value in names.iteritems() if value == factor][0]
                if name in links:
                    for f in links[name]:
                        if f not in factors:
                            factors.append(f)

            irrelevant = []
            for factor in factors:

                if Query not in factor[0]:
                    if Query in links:
                        if factor not in links[Query]:
                            irrelevant.append(factor)

            for factor in irrelevant:
                factors.remove(factor)


            irrelevant = []
            for factor in factors:
                name = [key for key, value in names.iteritems() if value == factor][0]
                if Query in links and name in links:
                    if factor not in links[Query] and Q not in links[name] and factor != Q:
                        irrelevant.append(factor)
            for factor in irrelevant:
                factors.remove(factor)

            added_factors = []
            for e in evidences:
                if e[0] in factors:
                    name = [key for key, value in names.iteritems() if value == e[0]][0]
                    if len(e[0][1]) == 2:
                        factors.remove(e[0])
                    else:
                        temp = restrict(e[0], name, e[1])
                        temp[0].remove(name)
                        added_factors.append(temp)
                        factors.remove(e[0])

                to_be_removed = []
                for factor in factors:
                    if len(factor[1]) > 2:
                        if name in factor[0][:-1]:
                            temp = restrict(factor, name, e[1])
                            added_factors.append(temp)
                            to_be_removed.append(factor)
                for factor in to_be_removed:
                    factors.remove(factor)
            for factor in added_factors:
                if factor not in factors:
                    factors.append(factor)


            if len(factors) == 1:
                for value in factors[0][1:]:
                    if value[0] == True:
                        t = value[1]
                print "P({}=True) = {} ".format(Query, t)
                print "P({}=False) = {} ".format(Query, 1-t)    


            else:
                factors_not_for_loop = []
                for factor in factors:
                    if len(factor[1]) == 2 and Query in factor[0]:
                        factors_not_for_loop.append(factor)

                for factor in factors_not_for_loop:
                    factors.remove(factor)

                while(len(factors) > 1):

                    selected = pick(factors)
                    multiplied = multiply(selected[0], selected[1])
                    sm = sumout(multiplied, selected[2])
                    factors.remove(selected[0])
                    factors.remove(selected[1])
                    factors.append(sm)

                for factor in factors_not_for_loop:
                    factors.append(factor)
                if len(factors) > 1:
                    factors = multiply(factors[0],factors[1])
                else:
                    factors = factors[0]

                for value in factors:
                    if value[0] == True:
                        t = value[1]
                    elif value[0] == False:
                        f = value[1]

                if f+t == 1: # If the values don't need normalization
                    print "P({}=True) = {} ".format(Query, t)
                    print "P({}=False) = {} ".format(Query, f)
                else: # Normalizing
                    z = t+f
                    print "\n"
                    print "P({}=True) = {} ".format(Query, t/z)
                    print "P({}=False) = {} ".format(Query, f/z)

        except:
            print "Sorry I can't calculate this probability! Please try another query"

    # Reading from keyboard
    string = raw_input('''Please enter your query:
    ''')

    string = string[2:-1].split("|")
    # print string[0]
    if len(string) > 1:
        if "," in string[1]:
            evids = []
            evs = string[1].split(",")
            for e in evs:
                args = e.split("=")
                evids.append([names[args[0].replace(" ", "")], str2bool(args[1].replace(" ", ""))])
            try:
                inference(names[string[0].replace(" ","")], evids)
            except:
                print "I think you have entered the query in a wrong format. Please pay attention to the instructions!"

        else:
            evids = []
            args = string[1].split("=")
            evids.append([names[args[0].replace(" ", "")], str2bool(args[1].replace(" ", ""))])
            try:
                inference(names[string[0].replace(" ","")], evids)
            except:
                print "I think you have entered the query in a wrong format. Please pay attention to the instructions!"

    else:
        try:
            inference(names[string[0].replace(" ","")], [])
        except:
            print "I think you have entered the query in a wrong format. Please follow the instructions!"