from time import gmtime, strftime

class Logger:
    def __init__(self,filen):
        self.filename = filen
        self.fl = None
    
    def a(self):
        self.fl = open(self.filename,"a")

    def whac(self,string):
        self.fl = open(self.filename,"a")
        self.fl.write("\n#"+string+"\n")
        self.c()

    def w(self,string):
        stt = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
        self.fl.write(stt+" || "+string+"\n")

    def wac(self,string):
        self.fl = open(self.filename,"a")
        self.w(string)
        self.c()

    def c(self):
        #stt = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
        #self.fl.write(stt+" || closing log\n")
        self.fl.close()
