from sets import Set
import json, os, sys, itertools, re


# convert hex address to int value
def addr_to_int(addr):
    return int(addr, 16)


# search a function by given an address
def binarySearch(addr, start_array, end_array, name_array):
    first = 0
    last = len(end_array) - 1
    fname = ''
    found = False

    if last < 0:
        return fname

    while first <= last and not found:
        midpoint = (first + last) / 2
        if addr <= end_array[midpoint] and addr >= start_array[midpoint]:
            fname = name_array[midpoint]
            found = True
        else:
            if addr < start_array[midpoint]:
                last = midpoint - 1
            if addr > end_array[midpoint]:
                first = midpoint + 1
    return fname


# combine the backtrace function calls to a long string without ","
def combineString(stringTrace):
    strings = stringTrace.split(',')
    string = ''
    if strings:
        for i in range(1, len(strings)):
            string = string + strings[i]
    
    return string


# check the relationship between current trace line and previous trace line   
def checkStackTrace(pstr, cstr):
    if pstr == cstr:
        return 'EQ' # in same function
    else:
        if pstr in cstr:
            return 'ENTER' # enter a sub function

        if cstr in pstr:
            return 'LEAVE' # leave current function

        return 'END' # different function
      

# split function features
def split_array(string_array):
    if string_array == '':
        return ''

    key = 'END'
    result = []
    tmp = []
    for string in string_array:
        if string != 'END':
            tmp.append(string)
            continue
        result.append(tmp)
        tmp = []
    return result


# remove duplicate features for each functions
def remove_duplicates(features):
    features.sort()
    result = list(features for features,_ in itertools.groupby(features))
    return result


# init a tmp stack to handle the first trace line
def init_stack(string_array):
    size = len(string_array)
    result = []
    for i in range(0, size-1):
        result.append(string_array[size-1-i]) # first function is library call, skip it.

    return result


# get the number of same functions between current and previous backtrace lines
def pop_offset(current, previous):
    num = 0
    clen = len(current)
    plen = len(previous)

    if clen >= plen:
        length = plen
    else:
        length = clen

    for i in range(0, length):
        if current[clen-1-i] == previous[plen-1-i]:
            num = num + 1
        else:
            break

    return num


def main():
    folder = sys.argv[1]

    # input
    all_func_list = os.path.join(folder, 'all_func_list.txt')
    module_func_file = os.path.join(folder, 'module_func_list.txt')
    trace_file = os.path.join(folder, 'stack_backtrace.txt')

    # output
    trace_to_func = os.path.join(folder, 'trace_to_func.txt')
    func_with_features = os.path.join(folder, 'func_with_features.txt')
    func_with_features_split = os.path.join(folder, 'func_with_features_split.txt')

    all_func_start = []
    all_func_end = []
    all_func_name = []
    module_dict = {}


    # read all functions and create array lists to store start address, end address, and function name 
    with open(all_func_list) as a_f:
        all_func_lines = a_f.read().splitlines()
        
    for all_func_line in all_func_lines:
        func_line_split = re.split(r'[,\t]+', all_func_line)
        all_func_start.append(addr_to_int(func_line_split[0]))
        all_func_end.append(addr_to_int(func_line_split[1]))
        all_func_name.append(func_line_split[2])

    print '# of all functions: ', len(all_func_name)


    # read all module functions and create a dictionary: <name, address>
    with open(module_func_file) as m_f:
        module_lines = m_f.read().splitlines()

    for module_line in module_lines:
        module_line_split = re.split(r'[,\t]+', module_line)
        module_dict_key = module_line_split[0]
        module_dict_value = module_line_split[1]
        module_dict[module_dict_key] = module_dict_value

    print '# of library functions: ', len(module_dict)


    # read tracefile and convert adresses to function names
    with open(trace_file) as t_f:
        trace_lines = t_f.read().splitlines()

    tf = open(trace_to_func, 'a')
    for trace_line in trace_lines:
        if trace_line:
            trace_addrs = trace_line.split(',')
            lib_addr = trace_addrs[0]
            lib_name = module_dict[lib_addr]
            tf.write(lib_name + ',')

            for index in range(1, len(trace_addrs)):
                bt_addr = trace_addrs[index]
                if bt_addr:
                    bt_name = binarySearch(addr_to_int(bt_addr), all_func_start, all_func_end, all_func_name)

                    if bt_name:
                        tf.write(bt_name + ',')
                    else:
                        tf.write('NULL' + ',')
            tf.write('\n')
    tf.close()


    # generate function features
    with open(trace_to_func, 'r') as trace_to_func_f:
        if trace_to_func_f:
            
            # create a function feature dictionary to store: <func_name, func_features>
            func_trace = {}

            # init function feature dictionary
            for i in range(0, len(all_func_name)):
                func_trace_key = all_func_name[i]
                func_trace[func_trace_key] = []

            fname_trace_lines = trace_to_func_f.read().splitlines()
            
            # init tmp stack and handle the first trace line
            fnames = fname_trace_lines[0].split(',')
            tmp_stack = init_stack(fnames)
            for i in range(1, len(fnames)):
                fname = fnames[i]
                if fname and fname != 'NULL':
                    func_trace[fname].append(fnames[0])

            # handle the rest of trace lines, starting at the second line
            for j in range(1, len(fname_trace_lines)):
                previous = combineString(fname_trace_lines[j-1])
                current = combineString(fname_trace_lines[j])
                status = checkStackTrace(previous, current)

                p_fnames = fname_trace_lines[j-1].split(',')
                fnames = fname_trace_lines[j].split(',')
                
                p_fnames_len =  len(p_fnames)
                fnames_len =  len(fnames)
                
                if status == 'ENTER':
                    len_diff = fnames_len - p_fnames_len
                    for depth in range(0, len_diff):
                        tmp_stack.append(fnames[1+depth])

                elif status == 'LEAVE':
                    # pop the func name from tmp_stack and add END to that func
                    len_diff = p_fnames_len - fnames_len
                    for depth in range(0, len_diff):
                        tmp_name = tmp_stack.pop()
                        if tmp_name and tmp_name != 'NULL':
                            func_trace[tmp_name].append('END')

                elif status == 'END':
                    # pop the func name from tmp_stack and add END to that func
                    pop_diff = pop_offset(fnames, p_fnames)
                    plen_diff = p_fnames_len - 1 - pop_diff

                    for depth in range(0, plen_diff):
                        tmp_name = tmp_stack.pop()
                        if tmp_name and tmp_name != 'NULL':
                            func_trace[tmp_name].append('END')

                    # add new func names to tmp_stack
                    len_diff = fnames_len - 1 - pop_diff
                    for depth in range(0, len_diff):
                        tmp_stack.append(fnames[len_diff-depth])

                # add lib call name as features to corresponding functions
                for k in range(1, len(fnames)):
                    fname = fnames[k]
                    if fname and fname != 'NULL':
                        func_trace[fname].append(fnames[0])
            
            # add 'END' after all trace lines are handled
            for item in tmp_stack:
                if item and item != 'NULL':
                    func_trace[item].append('END')                  

            # write the features to file
            ft = open(func_with_features, 'a')
            fts = open(func_with_features_split, 'a')
            count = 0;
            for key in func_trace:
                features = split_array(func_trace[key])

                if features:
                    count = count + 1
                    features_no_duplicates = remove_duplicates(features)
                    data = {
                        'name' : key,
                        #'features' : features,
                        'features' : features_no_duplicates,
                    }
                    json_data = json.dumps(data)
                    json_data_split = json.dumps(data, indent=4, separators=(',', ' : '))
                    ft.write(json_data + '\n\n')
                    fts.write(json_data_split + '\n\n')
            ft.close()
            fts.close() 
            print 'Func features are generated! Func #: ', count


if __name__ == '__main__':
    main()
        