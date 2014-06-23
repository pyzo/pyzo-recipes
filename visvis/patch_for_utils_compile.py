""" For Windows to use MSVC compiler.
Note that the visvis build must probably take place using an MSVS shell.
And the following commands should be issued:
  * setenv /x64 /release
"""

import visvis, os, sys
if sys.platform.startswith('win'):
    
    visvisdir = os.path.dirname(visvis.__file__)
    fn = os.path.join(visvisdir, 'utils', 'iso', '__init__.py')
    text = open(fn, 'rb').read().decode('utf-8')
    text = text.replace('pyximport.install()', 
                        'pyximport.install(compiler="native")')
    open(fn, 'wb').write(text.encode('utf-8'))
