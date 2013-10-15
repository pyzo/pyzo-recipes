import shutil
import os
import sys


def install_qt_menu_nib():
        # For Qt to work on Mac, we need to put the qt_menu.nib directory
        # at the appropriate location..
        
        #path_src = '/opt/local/Library/Frameworks/QtGui.framework/Versions/4/Resources/qt_menu.nib'
        path_src = None
        # Get .nib dir in a smart way. Taken from cx_Freeze
        from PySide import QtCore
        lpath = QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.LibrariesPath)
        for subpath in ['QtGui.framework/Resources', 'Resources']:
            path = os.path.join(lpath, subpath, 'qt_menu.nib')
            if os.path.exists(path):
                path_src = path
                break
        # Copy the directory!
        if path_src:
            path_dst = sys.prefix + '/lib/Contents/Resources/qt_menu.nib'
            shutil.copytree(path_src, path_dst)
        else:
            raise RuntimeError('Could not find qt_menu.nib')

if __name__ == '__main__':
    install_qt_menu_nib()
