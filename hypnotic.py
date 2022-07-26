import logging

import hou
from marshmallow import Schema, ValidationError, fields

from .util import calcHash


class Hypnotic:
    def __init__(self, hipFile, schema=None):
        self.hipFile = hipFile
        self.hipFileHash = None
        self.controls = None
        self.out = None

        self._loadHip(self.hipFile)

        if schema:
            self.controlSchema = schema
        else:
            self._generateSchema()

    def _generateSchema(self):
        """
        Scan the control node to generate a validation schema for incoming data.
        """
        if self.controls:
            parms = self.controls.parms()
        else:
            logging.error("No control node in object. Is the hip file initialized?")
            return

        schemaDict = {}
        for parm in parms:
            value = parm.eval()
            if isinstance(value, str):
                schemaDict[parm.name()] = fields.String(required=False)
            elif isinstance(value, int):
                schemaDict[parm.name()] = fields.Integer(required=False)
            elif isinstance(value, float):
                schemaDict[parm.name()] = fields.Float(required=False)
            else:
                logging.info(f"Skipping parameter {parm.name()} of unrecognized type")

        self.controlSchema = Schema.from_dict(schemaDict)

    def _loadHip(self, file=None, hash=None):
        """
        Reload the hip file definition, or switch to a new one.
        Veify changes with hash if provided.
        """

        logging.info("Reloading the hip file")
        # Calculate the new files hash
        if file:
            newHash = calcHash(file)
        else:
            newHash = calcHash(self.hipFile)

        # if a hash has been provided to verify the new file, make sure they match
        if hash:
            if hash != newHash:
                logging.error("New file hash does not match provided one")
                return

        # If we are loading a new file and not reloading one in the same place update
        # our file name
        if file:
            self.hipFile = file

        # Actually load the file and save the hash to the object
        hou.hipFile.load(self.hipFile)
        self.controls = hou.node("/obj/CONTROLS")
        self.out = hou.node("/out/OUT")
        self.out_gl = hou.node("/out/OUT_GL")
        self.out_uv = hou.node("/out/OUT_UV")
        self.hipFileHash = newHash

    def _detectChanges(self):
        """
        Detects changes in the hip file during runtime.
        """
        md5_hash = calcHash(self.hipFile)

        return not md5_hash == self.hipFileHash

    def _reloadIfChanged(self):
        """
        Re-imports the hip file if it has been changed externally since it was loaded.
        """
        if self._detectChanges():
            self._loadHip()

    def _validateControls(self, controls):
        """
        Ensure passed parameters will fit in the control node
        """

        try:
            self.controlSchema.load(controls)
            return True
        except ValidationError as err:
            logging.error(f"Controls did not pass Hypnotic validation.\n{err.messages}")
            return False

    def _writeControls(self, controls):
        """
        Write the parameters from a json request into the control node.
        """
        self._reloadIfChanged()
        controlsAreValid = self._validateControls(controls)
        if controlsAreValid:
            self.controls.setParms(controls)
        else:
            logging.error("Could not write controls. Reason: Invalid controls")

    def exportPrintFile(self, controls):
        """
        Export an obj file from the provided parameters.
        """
        self._writeControls(controls)

        outPath = f"$HIP/out/print/{self.hipFile.split('/')[-1].split('.')[0]}/out.obj"
        self.out.setParms({"sopoutput": outPath})

        self.out.render()

    def exportPreviewFile(self, controls):
        """
        Export a .glb file from the provided parameters.
        """
        self._writeControls(controls)

        outPath = f"$HIP/out/gl/{self.hipFile.split('/')[-1].split('.')[0]}/out.glb"
        self.out.setParms({"file": outPath})

        self.out_gl.render()
