import json, sys, os

file = os.path.join(sys.argv[1], 'func_with_features.txt')
save_file = os.path.join(sys.argv[1], 'features_summary.txt')

with open(file) as f:
    lines = f.read().splitlines()

    count = 0
    num_name = {k : [] for k in range(1000)}

    for line in lines:
        if line:
            count = count + 1
            data = json.loads(line)
            name = data['name']
            features = data['features']

            num_events = 0

            for feature in features:
                tmp = len(feature)
                if tmp > num_events:
                    num_events = tmp
            
            num_name[num_events].append(name)

    print 'Total: ', count

    sf = open(save_file, 'a')
    for i in range(0, 999):
        length = len(num_name[i])
        if length:
            
            info = str(i) + ': ' + str(length) + ', {' + str(num_name[i]) + '}\n\n'
            sf.write(info) 
    sf.close()           