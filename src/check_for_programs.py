import os

def is_exe(filepath):
    return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

def which_program(program):
    filepath, filename = os.path.split(program)
    if filepath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

print which_program("FastTree")