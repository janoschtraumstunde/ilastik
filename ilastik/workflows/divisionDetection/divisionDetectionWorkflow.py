from lazyflow.graph import Graph, Operator, OperatorWrapper

from ilastik.workflow import Workflow

from ilastik.applets.projectMetadata import ProjectMetadataApplet
from ilastik.applets.dataSelection import DataSelectionApplet
from ilastik.applets.objectExtraction import ObjectExtractionApplet

from ilastik.applets.objectClassification import ObjectClassificationApplet

from lazyflow.graph import Operator, InputSlot, OutputSlot
from lazyflow.stype import Opaque
from lazyflow.operators.ioOperators.opInputDataReader import OpInputDataReader
from lazyflow.operators import OpAttributeSelector
from ilastik.applets.divisionFeatureExtraction.divisionFeatureExtractionApplet import DivisionFeatureExtractionApplet
from ilastik.applets.thresholdTwoLevels.thresholdTwoLevelsApplet import ThresholdTwoLevelsApplet

class DivisionDetectionWorkflow(Workflow):
    name = "Division Detection Workflow"

    def __init__( self, headless, *args, **kwargs ):
        graph = kwargs['graph'] if 'graph' in kwargs else Graph()
        if 'graph' in kwargs: del kwargs['graph']
        super(DivisionDetectionWorkflow, self).__init__(headless=headless, graph=graph, *args, **kwargs)

        ######################
        # Interactive workflow
        ######################

        ## Create applets
        self.rawDataSelectionApplet = DataSelectionApplet(self,
                                                       "Input: Raw",
                                                       "Input Raw",
                                                       batchDataGui=False,
                                                       force5d=True)
        
        self.dataSelectionApplet = DataSelectionApplet(self,
                                                       "Input: Segmentation",
                                                       "Input Segmentation",
                                                       batchDataGui=False,
                                                       force5d=True)
        
#        self.thresholdTwoLevelsApplet = ThresholdTwoLevelsApplet(self, 
#                                                                 "Threshold & Size Filter", 
#                                                                 "ThresholdTwoLevels" )
        
#        self.objectExtractionApplet = ObjectExtractionApplet(workflow=self)
        self.objectExtractionApplet = DivisionFeatureExtractionApplet(workflow=self)
        self.objectClassificationApplet = ObjectClassificationApplet(workflow=self,
                                                                     name="Division Detection",
                                                                     projectFileGroupName="DivisionDetection")

        self._applets = []
        self._applets.append(self.rawDataSelectionApplet)
        self._applets.append(self.dataSelectionApplet)
#        self._applets.append(self.thresholdTwoLevelsApplet)
        self._applets.append(self.objectExtractionApplet)
        self._applets.append(self.objectClassificationApplet)

    @property
    def applets(self):
        return self._applets

    @property
    def imageNameListSlot(self):
        return self.dataSelectionApplet.topLevelOperator.ImageName

    def connectLane( self, laneIndex ):
        ## Access applet operators
        opRawData = self.rawDataSelectionApplet.topLevelOperator.getLane(laneIndex)
        opData = self.dataSelectionApplet.topLevelOperator.getLane(laneIndex)
#        opTwoLevelThreshold = self.thresholdTwoLevelsApplet.topLevelOperator.getLane(laneIndex)
        opObjExtraction = self.objectExtractionApplet.topLevelOperator.getLane(laneIndex)
        opObjClassification = self.objectClassificationApplet.topLevelOperator.getLane(laneIndex)

        # connect data -> extraction
        opObjExtraction.RawImage.connect(opRawData.Image)        
#        opTwoLevelThreshold.InputImage.connect(opData.Image)        
#        opObjExtraction.BinaryImage.connect(opTwoLevelThreshold.Output)
        opObjExtraction.BinaryImage.connect(opData.Image)

        # connect data -> classification
        opObjClassification.BinaryImages.connect(opData.Image)
        opObjClassification.RawImages.connect(opRawData.Image)
        opObjClassification.LabelsAllowedFlags.connect(opData.AllowLabels)

        # connect extraction -> classification
        opObjClassification.SegmentationImages.connect(opObjExtraction.LabelImage)
        opObjClassification.ObjectFeatures.connect(opObjExtraction.RegionFeatures)