from idaapi import *
from idautils import *
from idc import *
from sets import Set

module_set = Set()

# search specific module from all imported modules
def search_module(ea, module, module_output):
    index = 0
    f = open(module_output, "a")

    for function_ea in Functions(SegStart(ea), SegEnd(ea)):
        f_name = GetFunctionName(function_ea)
        if f_name in module_set:   
            index = index + 1
            f.write(str(hex(function_ea)) + "," + f_name + "\n")
            
    f.close()
    print "Total # of functions dumped from ", module, ": ", index

# callback function when iterate all functions in a module    
def imp_cb(ea, name, ord):
    if not name:
        print "%08x: ord#%d is NULL" % (ea, ord)
    else:
        module_set.add(name)
    
    # True -> Continue enumeration
    # False -> Stop enumeration
    return True

# get specific imported module and iterate all functions from it   
def dump_target_module(ea, module, module_output):
    nimps = get_import_module_qty()
    print "Found %d import(s)..." % nimps
    
    for i in xrange(0, nimps):
        name = get_import_module_name(i)
        if not name:
            print "Failed to get import module name for #%d" % i
            continue
        if module in name:
            print "Walking-> %s" % name
            enum_import_names(i, imp_cb)
            search_module(ea, module, module_output)

# get start address, end address, and name of all functions         
def dump_all_func(ea, all_func_output):
    index = 0
    f = open(all_func_output, 'a')
    for function_ea in Functions(SegStart(ea), SegEnd(ea)):
        index = index + 1
        f_name = GetFunctionName(function_ea)
        end = FindFuncEnd(function_ea)
        f.write(str(hex(function_ea)) + ',' + str(hex(end)) + ',' + f_name + '\n')
    f.close()  
    print 'Total # of functions: ', index

def main():  
    all_func_output = 'all_func_list.txt'
    module_output = 'module_func_list.txt'
    target_module = 'libSystem.B.dylib'

    for ea in Segments():
        segname = SegName(ea)
        if 'text' in  segname:
            dump_all_func(ea, all_func_output)
            
        if 'picsymbolstub' in segname:
            dump_target_module(ea, target_module, module_output)
            
            
if __name__ == '__main__':
    main()
        
        