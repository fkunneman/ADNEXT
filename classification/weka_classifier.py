
import weka.core.jvm as jvm
from weka.core.converters import Loader
from weka.classifiers import Classifier

class Classifier():

    def __init__(self):
        self.jvm.start(class_path=['/vol/customopt/machine-learning/src/weka/weka-3-6-8/weka.jar'])
        self.loader = Loader(classname="weka.core.converters.ArffLoader")
        
    def train(self,classifier,trainfile):
        if classifier == "ripper":
            self.cls = Classifier(classname="weka.classifiers.rules.JRip",options=["-P", "false","-E","false","O","5"])
        data = self.loader.load_file(trainfile)
        data.set_class_index(data.num_attributes() - 1)
        self.cls.build_classifier(data)
        return(self.cls.__str__())

    def test(self,testfile):
        predictions = []
        testdata = self.loader.load_file(testfile, incremental=True)
        testdata.set_class_index(data.num_attributes() - 1)
        while True:
            inst = self.loader.next_instance(testdata)
            if inst is None:
                break
            predictions.append([self.cls.predict_instance(inst)," ".join(self.cls.distribution_for_instance(inst))])
        return predictions

    def stop(self):
        self.jvm.stop()
