from math import *
from decimal import Decimal

import json, sys, os, editdistance
 
# calcuate longest common sequence length
def lcs_length(a, b):
    table = [[0] * (len(b) + 1) for _ in xrange(len(a) + 1)]
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            table[i][j] = (
                table[i - 1][j - 1] + 1 if ca == cb else
                max(table[i][j - 1], table[i - 1][j]))
    return table[-1][-1]

known_fname = str(sys.argv[4]).lower()
rank = int(sys.argv[3])
known = os.path.join(sys.argv[1], 'func_with_features.txt')
unknown = os.path.join(sys.argv[2], 'func_with_features.txt')

try: 
    with open(known) as k_f:
        known_lines = k_f.read().splitlines()

        for known_line in known_lines:
            if known_line:
                data = json.loads(known_line)
                name = data['name'].lower()
                
                # first, find target functions from known function file
                if known_fname in name: 
                    known_features = data['features']
                    similarity = {} # measure distance similarity 
                    lcs = {} # longest common sequence of function features
                    
                    # loop all features of target function
                    for i in range(0, len(known_features)): 

                        # for each feature of target function, create its similarity set from unknown function file
                        if known_features[i]: 
                            len_k = len(known_features[i])
                            if len_k < 5:
                            	continue
                            similarity_result = {}
                            lcs_result = {}
                            with open(unknown) as u_f:
                                unknown_lines = u_f.read().splitlines()

                                # loop all features of all unknown functions 
                                for unknown_line in unknown_lines:
                                    if unknown_line:
                                        data = json.loads(unknown_line)
                                        u_name = data['name']
                                        u_features = data['features']
                                        
                                        for j in range(0, len(u_features)):
                                            points = editdistance.eval(known_features[i], u_features[j])
                                            lcs_l = lcs_length(known_features[i], u_features[j])
                                            
                                            len_u = len(u_features[j])
                                            u_key = u_name + '__' + str(j) + '_' + str(len_u)
                                            
                                            similarity_result[u_key] = points
                                            lcs_result[u_key] = lcs_l

                            # get specific number of top functions by distance similarity
                            results = sorted(similarity_result.items(), key=lambda x: x[1])
                            length = len(results)
                            if rank > length:
                                rank = length
                            
                            result_array = []
                            for k in range(0, rank):
                                result_array.append(results[k])
                        
                            key = name + '__' + str(i) + '_' + str(len_k)
                            similarity[key] = result_array
                            
                            print 'Edit Distance Similarity for Function: ', key
                            for result_item in result_array:
                                print result_item
                            print '\n'

                            # get specific number of top functions by longest common sequence
                            results = sorted(lcs_result.items(), key=lambda x: x[1], reverse=True)
                            length = len(results)
                            if rank > length:
                                rank = length
                            
                            result_array = []
                            for k in range(0, rank):
                                result_array.append(results[k])
                        
                            key = name + '__' + str(i) + '_' + str(len_k)
                            lcs[key] = result_array
                            
                            print 'Longest Common Subsequence Length for Function: ', key
                            for result_item in result_array:
                                print result_item
                            print '\n'

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(fname, exc_type, exc_tb.tb_lineno, exc_obj)