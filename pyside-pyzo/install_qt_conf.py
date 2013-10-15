import sys, os
for subdir in ('', 'bin'):
    with open(os.path.join(sys.prefix, subdir, 'qt.conf'), 'wb') as file:
        file.write("[Paths]\nPlugins = '.'\n".encode('utf-8'))
