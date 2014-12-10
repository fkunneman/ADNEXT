
import frog

class Frogger:

    def __init__(self,t):
        self.frogger = frog.Frog(frog.FrogOptions(threads=t),"/vol/customopt/uvt-ru/etc/frog/frog-twitter.cfg")

    def return_entities(self,sentences):
        for sentence in sentences:
            tags = self.frogger.process(sentence)
            print(tags)

