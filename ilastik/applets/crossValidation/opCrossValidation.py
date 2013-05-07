from crossValidation import make_folds, train_and_predict
from lazyflow.graph import Operator, InputSlot, OutputSlot
from ilastik.utility import OperatorSubView, MultiLaneOperatorABC

import logging
logger = logging.getLogger(__name__)

class OpCrossValidation(Operator, MultiLaneOperatorABC):
    name = "OpCrossValidation"
    category = "Top-level"

    PatchFeatures = InputSlot(level=1)
    PatchLabels = InputSlot(level=1)
    NFolds = InputSlot(stype='int')

    Classifiers = OutputSlot(level=1)
    Predictions = OutputSlot(level=1)

    def __init__(self, *args, **kwargs):
        super(OpCrossValidation, self).__init__(*args, **kwargs)

    def setupOutputs(self):
        super(OpCrossValidation, self).setupOutputs()

        self.Classifiers.resize(self.NFolds.value)
        self.Predictions.resize(len(self.PatchFeatures))

    def execute(self, slot, subindex, roi, result):
        pass

    def propagateDirty(self, slot, subindex, roi):
        pass

    def addLane(self, laneIndex):
        numLanes = len(self.PatchFeatures)
        assert numLanes == laneIndex, "Image lanes must be appended."
        for slot in self.inputs.values():
            if slot.level > 0 and len(slot) == laneIndex:
                slot.resize(numLanes + 1)

    def removeLane(self, laneIndex, finalLength):
        for slot in self.inputs.values():
            if slot.level > 0 and len(slot) == finalLength + 1:
                slot.removeSlot(laneIndex, finalLength)

    def getLane(self, laneIndex):
        return OperatorSubView(self, laneIndex)
