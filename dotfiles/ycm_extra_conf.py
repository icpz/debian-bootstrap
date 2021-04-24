import os
import os.path
import fnmatch
import logging
import ycm_core
import re

DIR_OF_THIS_SCRIPT = os.path.abspath( os.path.dirname( __file__ ) )
DIR_OF_THIRD_PARTY = os.path.join( DIR_OF_THIS_SCRIPT, 'third_party' )

compilation_database_folder = ''
if os.path.exists( compilation_database_folder ):
    database = ycm_core.CompilationDatabase( compilation_database_folder )
else:
    database = None


BASE_FLAGS = [
        '-Wall',
        '-Wextra',
        '-Werror',
        '-Wno-long-long',
        '-Wno-variadic-macros',
        '-Wno-unused-variable',
        '-fexceptions',
        '-ferror-limit=10000',
        '-DNDEBUG',
        '-std=c++1z',
        '-fcoroutines-ts',
        '-xc++',
        '-I/usr/lib/',
        '-I/usr/include/',
        '-I/usr/local/include/',
        ]

SOURCE_EXTENSIONS = [
        '.cpp',
        '.cxx',
        '.cc',
        '.c',
        '.m',
        '.mm'
        ]

SOURCE_DIRECTORIES = [
        'src',
        'lib'
        ]

HEADER_EXTENSIONS = [
        '.h',
        '.hxx',
        '.hpp',
        '.hh'
        ]

header_file_extensions = HEADER_EXTENSIONS

HEADER_DIRECTORIES = [
        'include'
        ]

BUILD_DIRECTORY = 'build';

def IsHeaderFile(filename):
    extension = os.path.splitext(filename)[1]
    return extension in HEADER_EXTENSIONS

def FindNearest(path, target, build_folder=None):
    candidate = os.path.join(path, target)
    if(os.path.isfile(candidate) or os.path.isdir(candidate)):
        logging.info("Found nearest " + target + " at " + candidate)
        return candidate;

    parent = os.path.dirname(os.path.abspath(path));
    if(parent == path):
        raise RuntimeError("Could not find " + target);

    if(build_folder):
        candidate = os.path.join(parent, build_folder, target)
        if(os.path.isfile(candidate) or os.path.isdir(candidate)):
            logging.info("Found nearest " + target + " in build folder at " + candidate)
            return candidate;

    return FindNearest(parent, target, build_folder)

def FlagsForClangComplete(root):
    try:
        clang_complete_path = FindNearest(root, '.clang_complete')
        clang_complete_flags = open(clang_complete_path, 'r').read().splitlines()
        return clang_complete_flags
    except:
        return None

def FlagsForInclude(root):
    flags = []
    try:
        gitrepo_path = FindNearest(root, '.git')
        gitrepo_path = os.path.dirname(gitrepo_path)
        logging.info("Searching `include' under %s" % gitrepo_path)
        for droot, dirs, files in os.walk(gitrepo_path):
            if dirs.count('.git'):
                dirs.remove('.git')
            for dir_path in dirs:
                if (dir_path == 'include'):
                    realpath = os.path.join(droot, dir_path)
                    flags += ["-I" + realpath]

        if len(flags) == 0:
            include_path = FindNearest(root, 'include')
            flags += ["-I" + include_path]

    except:
        pass

    return flags

def FlagsForFile(filename):
    root = os.path.realpath(filename);
    final_flags = BASE_FLAGS
    clang_flags = FlagsForClangComplete(root)
    if clang_flags:
        final_flags = final_flags + clang_flags
    include_flags = FlagsForInclude(root)
    if include_flags:
        logging.info("Additional include flags: " + str(include_flags))
        final_flags = final_flags + include_flags
    return final_flags

def FindCorrespondingSourceFile( filename ):
  if IsHeaderFile( filename ):
    basename = os.path.splitext( filename )[ 0 ]
    for extension in SOURCE_EXTENSIONS:
      replacement_file = basename + extension
      if os.path.exists( replacement_file ):
        return replacement_file
  return filename

def Settings( **kwargs ):
    if kwargs[ 'language' ] != 'cfamily':
        return {}
    # If the file is a header, try to find the corresponding source file and
    # retrieve its flags from the compilation database if using one. This is
    # necessary since compilation databases don't have entries for header files.
    # In addition, use this source file as the translation unit. This makes it
    # possible to jump from a declaration in the header file to its definition
    # in the corresponding source file.
    filename = FindCorrespondingSourceFile(kwargs[ 'filename' ])

    if not database:
        return {
            'flags': FlagsForFile(kwargs['filename']),
#            'include_paths_relative_to_dir': DIR_OF_THIS_SCRIPT,
#            'override_filename': filename
        }

    compilation_info = database.GetCompilationInfoForFile( filename )
    if not compilation_info.compiler_flags_:
        return {}

    # Bear in mind that compilation_info.compiler_flags_ does NOT return a
    # python list, but a "list-like" StringVec object.
    final_flags = list( compilation_info.compiler_flags_ )

    return {
      'flags': final_flags,
#      'include_paths_relative_to_dir': compilation_info.compiler_working_dir_,
#      'override_filename': filename
    }

