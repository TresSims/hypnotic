import hou
import logging
from .util import calcHash


class Hypnotic:
    def __init__(self, hipFile, schema=None):
        self.hipFile = hipFile
        self.hipFileHash = None

        hash = self._loadHip(self.hipFile)

        if schema:
            self.controlSchema = schema
        else:
            self._generateSchema()

    def _generateSchema(self):
        """
        Scan the control node to generate a validation schema for incoming data.
        Not implemented.
        """
        parms = self.controls.parms()
        schemaDict = {}
        logging.error("not implemented")

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

    def _writeControls(self, controls):
        """
        Write the parameters from a json request into the control node.
        """
        self._reloadIfChanged()
        validatedControls = self._validateControls(controls)
        self.controls.setParms(validatedControls)

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
