import PySide.QtCore
import PySide.QtDeclarative
import PySide.QtGui
import PySide.QtHelp
import PySide.QtMultimedia
import PySide.QtNetwork
import PySide.QtScript
import PySide.QtScriptTools
import PySide.QtSql
import PySide.QtSvg
import PySide.QtTest
import PySide.QtUiTools
import PySide.QtWebKit
import PySide.QtXml
import PySide.QtXmlPatterns
import PySide.QtOpenGL  # Was not testes on linux, why?
import pysideuic 

import sys
#if not sys.platform.startswith('linux'):
#    #import PySide.QtOpenGL
#    import PySide.phonon

# Test pyside executables
from subprocess import check_call, CalledProcessError
bin = sys.prefix + '/bin/'
check_call([bin+'pyside-uic', '--version'])
check_call([bin+'pyside-lupdate', '-version'])
try:
    check_call([bin+'pyside-rcc', '-version'])
except CalledProcessError as exc:
    assert exc.returncode == 1 

