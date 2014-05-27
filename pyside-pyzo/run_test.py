import PySide.QtCore
# import PySide.QtDeclarative  Broken on Windows
import PySide.QtGui
# import PySide.QtHelp  Broken on Windows
import PySide.QtMultimedia
import PySide.QtNetwork
import PySide.QtScript
import PySide.QtScriptTools
# import PySide.QtSql  Broken on Windows
import PySide.QtSvg
import PySide.QtTest
import PySide.QtUiTools
import PySide.QtWebKit
import PySide.QtXml
import PySide.QtXmlPatterns
import PySide.QtOpenGL
import pysideuic 

import sys
#if not sys.platform.startswith('linux'):
#    #import PySide.QtOpenGL
#    import PySide.phonon

# Test pyside executables
if not sys.platform.startswith('win'):
    from subprocess import check_call, CalledProcessError
    bin = sys.prefix + '/bin/'
    check_call([bin+'pyside-uic', '--version'])
    check_call([bin+'pyside-lupdate', '-version'])
    try:
        check_call([bin+'pyside-rcc', '-version'])
    except CalledProcessError as exc:
        assert exc.returncode == 1 

