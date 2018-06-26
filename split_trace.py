import os, sys

folder = sys.argv[1]
trace_file_all = os.path.join(folder, 'stack_backtrace_all.txt')
tf_folder = os.path.join(folder, 'stack_backtrace')

# create the folder if not exist
if not os.path.exists(tf_folder):
    try:
        os.makedirs(tf_folder)
    except OSError as exc:
        print 'OSError: ', exc

with open(trace_file_all) as f:
    trace_lines = f.read().splitlines()

    # split trace lines based on the thread ID, write as separate trace files
    for trace_line in trace_lines:
        if trace_line:
            data = trace_line.split(',')
            thread_id = data[0] # thread ID is the first element of each trace line
            tf_name = str(thread_id) + '_stack_backtrace.txt'
            tf_file = os.path.join(tf_folder, tf_name)

            tf = open(tf_file, 'a')
            for i in range(1, len(data)):
                tf.write(data[i] + ',')
            tf.write('\n')
            tf.close()

# combine all thread trace files into a single trace file
trace_file_combine = os.path.join(folder, 'stack_backtrace.txt')
with open(trace_file_combine, 'a') as out_file:
    for trace_file in os.listdir(tf_folder):
        in_file_path = os.path.join(tf_folder, trace_file)
        with open(in_file_path) as in_file:
            out_file.write(in_file.read())