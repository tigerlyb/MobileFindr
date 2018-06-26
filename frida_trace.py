import frida, sys, os

folder = sys.argv[1]
pid = int(sys.argv[2])
bp_list_file = os.path.join(folder, 'module_func_list.txt')
bp_list = []


def on_message(message, data):
    if message['type'] == 'send':
        #print(message['payload'])
        f = open('stack_backtrace_all.txt', 'a')
        f.write(message['payload'] + '\n')
        f.close()
    elif message['type'] == 'error':
        print('on_message error: ' + message['stack'])


session = frida.get_usb_device().attach(pid)

with open (bp_list_file) as f:
    lines = f.read().splitlines()

    for line in lines:
        address = line.split(',')[0]
        bp_list.append(address)

print ('Tracing %d library functions...' % len(bp_list)) 

for bp in bp_list:
    
    script = session.create_script("""

    var address = new NativePointer('%s');
    Interceptor.attach(address, {
        onEnter: function(args) {
            thread_id = this.threadId;

            send(thread_id + ',' + address + ',' + Thread.backtrace(this.context, Backtracer.ACCURATE));
            send('');
        }
    });

    """ % int(bp, 16))

    script.on('message', on_message)
    script.load()

sys.stdin.read()
