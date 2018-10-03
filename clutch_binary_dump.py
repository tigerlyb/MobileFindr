'''
Author: Jiakuan Li
'''

import mmap, subprocess

global configuration
configuration = list()

def get_install_app():
    output = subprocess.Popen('Clutch -i', shell=True, stdout=subprocess.PIPE).stdout.read()

    print output

    output = [s.strip() for s in output.splitlines()]
    output.pop(0)

    print "Total Apps:" + str(len(output))
    return len(output)

def get_dump_path(id):
    command = 'Clutch -n -i | grep \'' + str(id) + ':\''
    name = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    name = name[0:1]

    command = 'Clutch -n -b ' + str(id)
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = proc.stderr.read()
    if len(err) is not 0:
        f = open('Report', 'a+')
        f.write('Dump Fail, app id: ' + str(id))
        f.close()
        return
    output = proc.stdout.read()
    output = [s.strip() for s in output.splitlines()]

    armv7 = list()
    packages = list()

    for item in output[0:len(output) - 2]:
        if "Dumping" in item:
            package_name = item[item.find('<') + 1:item.rfind('>')]

            if 'armv7' in item:
                package_armv7 = True
            else:
                package_armv7 = False

            armv7.append(package_armv7)
            packages.append(package_name)

    path = output[-2]
    path = path[path.find('/'):]

    print "Finish Dumping, AppID =  " + str(id)
    # print "Total packages in this App: " + str(len(packages))
    configuration.append({'clutch_path':path, 'packages':packages, 'armv7':armv7, 'app_name':name})


def process_files(path, package, armv7, name):
    command = 'find ' + path + ' -name \"' + package + '\"'
    clutch_path = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    clutch_path = clutch_path.strip('\n')

    print "Disabling ASLR for: " + package
    disable_ASLR(clutch_path, armv7)

    if verify_PIE(clutch_path):
        print "Disable ASLR Success"
        replace_file(package, clutch_path, name)
    else:
        print "Disable ASLR Fail"
        f = open('Report', 'a+')
        f.write('Disable ASLR Fail for ' + package + '\n')


def disable_ASLR(filename, armv7):
    f = open(filename, 'a+')
    m = mmap.mmap(f.fileno(), 0)

    if armv7:
        m[0x401a] = '\x01'
    else:
        m[0x18] = '\x01'

    m.close()
    f.close()

def sign_app(app_path):
    command = 'ldid -s ' + app_path
    error = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE).stderr.read()

    if len(error) is not 0:
        f = open('Report', 'a+')
        f.write("Sining " + app_path + " fail")
        f.close()

def replace_file(package, clutch_path, name):
    command = 'find /User/Containers/Bundle/Application -name ' + '\"' + package + "\""
    app_path = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    app_path = app_path.strip('\n')

    command = 'cp ' + clutch_path + " " + app_path
    output = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE).stderr.read()
    output = output.strip('\n')
    if len(output) is not 0:
        f = open('Report', 'a+')
        f.write("Replace File Error " + package + '\n')
        f.close()
        return

    command = 'cp ' + clutch_path + ' ' + name
    output = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE).stderr.read()
    output = output.strip('\n')
    if len(output) is not 0:
        f = open('Report', 'a+')
        f.write('Copy clutch binary fail' + '\n')
        f.close()
        return

    sign_app(app_path)

    f = open('path_list', 'a+')
    f.write(package + '\n')
    f.write(app_path + '\n')
    f.write('\n')

    f.close()

    symbolic_destination = app_path[0:app_path.rfind('/')]
    symbolic_name = name + '/' + package + "_symbolic"

    create_symbolic(symbolic_destination, symbolic_name)

def verify_PIE(app_path):
    command = 'otool -Vh ' + '\'' + app_path + '\''
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    if 'PIE' in output:
        return False
    return True

def create_folder(name):
    stderr = subprocess.Popen('mkdir '+ name, shell=True, stderr=subprocess.PIPE).stderr.read()
    if len(stderr) is not 0:
        f = open('Report', 'a+')
        f.write(stderr + '\n')
        f.close()

def create_symbolic(destination, name):
    command = 'ln -s ' + destination + " " + name
    stderr = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE).stderr.read()
    if len(stderr) is not 0:
        f = open('Report', 'a+')
        f.write(stderr + '\n')
        f.close()

def reboot():
    subprocess.Popen('reboot', shell=True)

if __name__=='__main__':
    appcount = get_install_app()

    appid = raw_input("Please enter App ID: (enter 'all' for all app) ")
    if 'all' in appid:
        for i in range(1, appcount + 1):
            get_dump_path(i)
        # print appid
    else:
        while int(appid) > appcount:
            appid = raw_input("App ID does not exists, please enter App ID: (enter 'all' for all app): ")

        get_dump_path(int(appid))
        # print appid

    # print configuration

    for conf in configuration:
        print '==============================================='
        create_folder('\'' + conf['app_name'] + '\'')
        # create_symbolic(conf['clutch_path'], conf['app_name']+'/clutch_path')
        for package in conf['packages']:
            process_files(conf['clutch_path'], package, conf['armv7'][conf['packages'].index(package)], conf['app_name'])

    reboot_prompt = raw_input('Do you want to reboot? (y/n)')
    if 'y' in reboot_prompt:
        reboot()

