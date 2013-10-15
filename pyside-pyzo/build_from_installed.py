import os
import sys
import sysconfig
import shutil

# Allow importing Pyzolib from source
sys.path.append(os.path.expanduser('~/py'))

from pyzolib.path import Path
from pyzolib import dllutils

LIB_DIR = os.path.join(sys.prefix, 'lib')
PACKAGE_DIR = sysconfig.get_path('purelib')



def get_module_by_name(module_name):
    """ Get a module by its name.
    """
    #path = __import__(module_name).__file__
    import imp
    _, path, _ = imp.find_module(module_name)
    if path.endswith('__init__.py'):
        path = os.path.dirname(path)
    return Module(path)


class Module:
    """ The Module class is used to represent a module or package.
    It is used in the build process to keep track of all the modules and
    packages that we want to copy to the distro.
    """ 
    
    def __init__(self, path, ispkg=None):
        self.path = path
        self.includeMSVCR = True
        if ispkg is None:
            self.ispkg = os.path.isdir(self.path)
        else:
            self.ispkg = ispkg
    
    def name(self):
        return os.path.split(self.path)[1].rsplit('.',1)[0]
    
    def __repr__(self):
        moduleOrPackage = ['Module', 'Package'][self.ispkg]
        return "<%s '%s'>" % (moduleOrPackage, self.name())
    
    def install(self, dest=None):
        """ install the package to the target directory (where the new distro
        is build).
        
        This copies the source code of the packages, so the user has full 
        access (and control) over his code. Also any resource files are
        copied.
        
        Note that cx_Freeze may have created new .pyc files in some cases to 
        wrap DLL's. This is handled by using the copy_pycs method.
        
        """ 
        if dest is None:
            dest = PACKAGE_DIR
        
        if not self.ispkg:
            # Copy module (i.e. single file)
            fname = os.path.split(self.path)[1]
            destFile = os.path.join(dest, fname)
            if self.path != destFile:
                shutil.copy(self.path, destFile)
        else:
            # Copy package (multiple files and maybe resources)
            destDir = os.path.join(dest, self.name())
            if self.path != destDir:
                print('Installing %r' % self, end='')
                sys.stdout.flush()
                nfiles = copydir_smart(self.path, destDir)
                print('(%i files)'% nfiles)
    
    
    def install_dependencies(self):
        newfiles = set()
        count = 0
        
        if not self.ispkg:
            ext = os.path.splitext(self.path)[1].lower()
            if ext in ['.so', '.pyd', '.dll', '.dylib']: 
                dependencies = DependentFilesHelper(self.path)
                dependencies.get(self.path)
                count += dependencies.install()
                newfiles.update(dependencies._newFiles)
                print('Installed %i dependencies' % count)
        else:
            for dirpath, dirnames, filenames in os.walk(self.path):
                dependencies = DependentFilesHelper(dirpath)
                for fname in filenames:
                    fname = os.path.join(dirpath, fname)
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in ['.so', '.pyd', '.dll', '.dylib']: 
                        dependencies.get(fname)
                count += dependencies.install()
                newfiles.update(dependencies._newFiles)
            print('Installed %i dependencies' % count)
        
        # Recursively check for dependencies in the lib folder
        count = 0
        recDependencies = DependentFilesHelper(LIB_DIR)
        for filename in newfiles:
            recDependencies.get(filename)
        count += recDependencies.install()
        # Take 2
        newfiles = recDependencies._newFiles
        recDependencies = DependentFilesHelper(LIB_DIR)
        for filename in newfiles:
            recDependencies.get(filename)
        count += recDependencies.install()
        #
        print('Installed %i more dependencies' % count)


def copydir_smart(path1, path2):
    """ like shutil.copydirs, but ...
      * ignores __pycache__directories
      * ignores hg, svn and git directories
    """
    
    # Ensure destination directory does exist
    if not os.path.isdir(path2):
        os.makedirs(path2)
        
    # Itereate over elements
    count = 0
    for sub in os.listdir(path1):
        fullsub1 = os.path.join(path1, sub)
        fullsub2 = os.path.join(path2, sub)
        if sub in ['__pycache__', '.hg', '.svn', '.git']:
            continue
        elif os.path.isdir(fullsub1):
            count += copydir_smart(fullsub1, fullsub2)
        elif os.path.isfile(fullsub1):
            fullsub1 = os.path.abspath(fullsub1)
            fullsub1_ = os.path.realpath(fullsub1)
            if fullsub1 == fullsub1_:
                shutil.copy(fullsub1, fullsub2)
            elif os.path.dirname(fullsub1) == os.path.dirname(fullsub1_):
                # Preserve symlink
                fullsub3 = os.path.join(os.path.dirname(fullsub2), os.path.basename(fullsub1_))
                os.symlink(fullsub2, fullsub3)
            else:
                shutil.copy(fullsub1, fullsub2)
            count += 1
    
    # Return number of copies files
    return count


class DependentFilesHelper:
    """ DependentFilesHelper(srcPath, dstPath=target/shared)
    To help install dependencies: libraries that extension modules
    depend on. The given path should be the directory to install the
    dependencies for. If path is a file, this file is checked for
    dependencies and the dependencies are immediately installed next
    to it. The second (optional) argument specifies the target dir.
    """
    
    def __init__(self, srcPath, dstDir=None):
        if dstDir is None:
            dstDir = LIB_DIR
        srcPath = Path(srcPath)
        self._dstDir = Path(dstDir)
        
         # Init set of files
        self._dependentFiles = set()
        # Init set of files to set search path for
        self._dependingFiles = set()
        # Init set of files that were copied
        self._newFiles = set()
        
        self._dependentFilesCache = {}
        self._linkerWarnings = {}
        self.binIncludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinIncludes()]
        self.binExcludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinExcludes()]
        self.binPathIncludes = []
        self.binPathExcludes = [os.path.normcase(n) \
                for n in self._GetDefaultBinPathExcludes()]
        
        # If given path is a file, get and install dependencies now
        if srcPath.isdir:
            self._srcDir = srcPath
        elif srcPath.isfile:
            self._srcDir = srcPath.dirname
    
    
    def process_recursively(self):
        checkedFiles = set()
        count = 0
        while True:
            # Update file set
            allFiles = set(self._srcDir.files())
            # Get files to check
            filesToCheck = allFiles.difference(checkedFiles)
            if not filesToCheck:
                break
            # Install current files
            for fname in sorted(filesToCheck):
                checkedFiles.add(fname)
                self.get(fname)                
            count += self.install()
        return count
    
    def get(self, path):
        """ get(path)
        Get the files that the given dynamic library or extension module
        depends on.
        """
        # Get files that the given lib depends on
        files = self._GetDependentFiles(path)
        # If any, add them to our set and modify the lib's RPATH
        if files:
            self._dependentFiles.update(files) 
            self._dependingFiles.add(path)
        # Done
        return files
    
    def install(self):
        """ install()
        Install the dependent files found until now, 
        and set the search path of the files that depend on them.
        """
        # Install dependencies
        count = 0
        for dep_src in sorted(self._dependentFiles):
            fname = os.path.basename(dep_src)
            dep_dst1 = self._srcDir / fname
            dep_dst2 = self._dstDir / fname
            self._newFiles.add(dep_dst2)
            if not (os.path.isfile(dep_dst1) or os.path.isfile(dep_dst2)):
                if not os.path.isfile(dep_src):
                    print('Skipping invalid dependency: %s' % fname)
                    continue  # Weird bug on Mac
                print('  Installing dependency: %s' % fname)
                shutil.copyfile(dep_src, dep_dst2)
                count += 1
        # Set path *after* installing the dependencies;
        # On Mac we need to be sure that the dependency is on the rpath. 
        for path in self._dependingFiles:
            self._set_search_path_if_we_can(path)
        # Return number of installed files
        return count
    
    def _set_search_path_if_we_can(self, path):
        """ Convenience function used in get()
        """
        # Get command or return 
        if not dllutils.get_command_to_set_search_path():
            return
        # Get relative path
        dependerDir = os.path.dirname(path)
        relDir = os.path.relpath(self._dstDir, dependerDir)
        # Set it!
        dllutils.set_search_path(path, relDir)
    
    
    ## Taken/inspired from cx_Freeze
    def _GetDependentFiles(self, path):
        """Return the file's dependencies using platform-specific tools (the
           imagehlp library on Windows, otool on Mac OS X and ldd on Linux);
           limit this list by the exclusion lists as needed"""
        dependentFiles = self._dependentFilesCache.get(path)
        if dependentFiles is None:
            if sys.platform == "win32":
                origPath = os.environ["PATH"]
                os.environ["PATH"] = origPath + os.pathsep + \
                        os.pathsep.join(sys.path)
                import cx_Freeze.util
                dependentFiles = cx_Freeze.util.GetDependentFiles(path)
                os.environ["PATH"] = origPath
            else:
                dependentFiles = []
                if sys.platform == "darwin":
                    command = 'otool -L "%s"' % path
                    splitString = " (compatibility"
                    dependentFileIndex = 0
                else:
                    command = 'ldd "%s"' % path
                    splitString = " => "
                    dependentFileIndex = 1
                for line in os.popen(command):
                    parts = line.expandtabs().strip().split(splitString)
                    if len(parts) != 2:
                        continue
                    dependentFile = parts[dependentFileIndex].strip()
                    if dependentFile in ("not found", "(file not found)"):
                        fileName = parts[0]
                        if fileName not in self._linkerWarnings:
                            self._linkerWarnings[fileName] = None
                            message = "WARNING: cannot find %s\n" % fileName
                            sys.stdout.write(message)
                        continue
                    if dependentFile.startswith("("):
                        continue
                    pos = dependentFile.find(" (")
                    if pos >= 0:
                        dependentFile = dependentFile[:pos].strip()
                    if dependentFile:
                        dependentFiles.append(dependentFile)
            dependentFiles = self._dependentFilesCache[path] = \
                    [f for f in dependentFiles if self._ShouldCopyFile(f)]
        return dependentFiles
    
    
    def _ShouldCopyFile(self, path):
        """Return true if the file should be copied to the target machine. This
           is done by checking the binPathIncludes, binPathExcludes,
           binIncludes and binExcludes configuration variables using first the
           full file name, then just the base file name, then the file name
           without any version numbers.
           
           Files are included unless specifically excluded but inclusions take
           precedence over exclusions."""

        # check for C runtime, if desired
        path = os.path.normcase(path)
        dirName, fileName = os.path.split(path)
        if fileName.startswith("msvcr") and fileName.endswith(".dll"):
            self.msvcRuntimeDir = dirName
            return self.includeMSVCR
        
        # check the full path
        if path in self.binIncludes:
            return True
        if path in self.binExcludes:
            return False

        # check the file name by itself (with any included version numbers)
        if fileName in self.binIncludes:
            return True
        if fileName in self.binExcludes:
            return False

        # check the file name by itself (version numbers removed)
        name = self._RemoveVersionNumbers(fileName)
        if name in self.binIncludes:
            return True
        if name in self.binExcludes:
            return False

        # check the path for inclusion/exclusion
        for path in self.binPathIncludes:
            if dirName.startswith(path):
                return True
        for path in self.binPathExcludes:
            if dirName.startswith(path):
                return False

        return True
    
    
    def _GetDefaultBinExcludes(self):
        """Return the file names of libraries that need not be included because
           they would normally be expected to be found on the target system or
           because they are part of a package which requires independent
           installation anyway."""
        if sys.platform == "win32":
            return ["comctl32.dll", "oci.dll", "cx_Logging.pyd"]
        else:
            return ["libclntsh.so", "libwtc9.so"]

    def _GetDefaultBinIncludes(self):
        """Return the file names of libraries which must be included for the
           frozen executable to work."""
        if sys.platform == "win32":
            pythonDll = "python%s%s.dll" % sys.version_info[:2]
            return [pythonDll, "gdiplus.dll", "mfc71.dll", "msvcp71.dll",
                    "msvcr71.dll"]
        else:
            return []
#             soName = distutils.sysconfig.get_config_var("INSTSONAME")
#             if soName is None:
#                 return []
#             pythonSharedLib = self._RemoveVersionNumbers(soName)
#             return [pythonSharedLib]

    def _GetDefaultBinPathExcludes(self):
        """Return the paths of directories which contain files that should not
           be included, generally because they contain standard system
           libraries."""
        if sys.platform == "win32":
            import cx_Freeze.util
            systemDir = cx_Freeze.util.GetSystemDir()
            windowsDir = cx_Freeze.util.GetWindowsDir()
            return [windowsDir, systemDir, os.path.join(windowsDir, "WinSxS")]
        elif sys.platform == "darwin":
            return ["/lib", "/usr/lib", "/System/Library/Frameworks"]
        else:
            return ["/lib", "/lib32", "/lib64", "/usr/lib", "/usr/lib32",
                    "/usr/lib64"]
    
    
    def _RemoveVersionNumbers(self, libName):
        tweaked = False
        parts = libName.split(".")
        while parts:
            if not parts[-1].isdigit():
                break
            parts.pop(-1)
            tweaked = True
        if tweaked:
            libName = ".".join(parts)
        return libName


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Get input args
        modulename = sys.argv[1]
        if len(sys.argv) > 2:
            dest = sys.argv[2]
        else:
            dest = None
        
        # Get module
        if os.path.isfile(modulename):
            mod = Module(modulename)
        else:
            mod = get_module_by_name(modulename)
        
        # Install
        mod.install(dest)
        mod.install_dependencies()
    else:
        print('build_from_installed can import pyzolib')
    
    