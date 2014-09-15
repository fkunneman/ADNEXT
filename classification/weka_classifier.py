
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka import classifiers

class Classifier():

    def __init__(self):
        jvm.start(class_path=['/vol/customopt/machine-learning/src/weka/weka-3-6-8/weka.jar'])
        self.loader = Loader(classname="weka.core.converters.ArffLoader")
        
    def train(self,classifier,trainfile):
        if classifier == "ripper":
            self.cls = classifiers.Classifier(classname="weka.classifiers.rules.JRip",options=["-P", "false","-E","false","O","5"])
        data = self.loader.load_file(trainfile)
        data.set_class_index(data.num_attributes() - 1)
        self.cls.build_classifier(data)
        return(self.cls.__str__())

    def test(self,testfile):
        predictions = []
        testdata = self.loader.load_file(testfile, incremental=True)
        testdata.set_class_index(testdata.num_attributes() - 1)
        while True:
            inst = self.loader.next_instance(testdata)
            if inst is None:
                break
            predictions.append([self.cls.classify_instance(inst)," ".join([str(round(x,2)) for x in self.cls.distribution_for_instance(inst)])])
        return predictions

    def stop(self):
        jvm.stop()
