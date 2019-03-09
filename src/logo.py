logo = """
    ____        ____  __  ____    ___ _       ______ 
   / __ \__  __/ __ \/ / / / /   /   | |     / / __ \\
  / /_/ / / / / /_/ / /_/ / /   / /| | | /| / / / / /
 / ____/ /_/ / ____/ __  / /___/ ___ | |/ |/ / /_/ / 
/_/    \__, /_/   /_/ /_/_____/_/  |_|__/|__/_____/  
      /____/                                         
"""

from conf import DI

def version():
    import subprocess
    cmd = "cd "+DI+" && git log -1 --pretty=format:\"%H\""
    p = subprocess.Popen(cmd,stdout=subprocess.PIPE,shell=True)
    return "current git hash: "+p.communicate()[0]

if __name__ == "__main__":
    print(logo)
    print(version())