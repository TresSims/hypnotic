import hou
import logging
import hashlib


class Hypnotic:

    def __init__(self, hipFile, scema):
        self.hipFile = hipFile
        self.hipFileHash = None

        hash = self._loadHip(self.hipFile)

        self.controls = hou.node("/obj/CONTROLS")
        self.out = hou.node("/out/OUT")
        self.out_gl = hou.node("/out/OUT_GL")
        self.out_uv = hou.node("/out/OUT_UV")

        self.controlSchema = schema

    def _generateSchema(self):
        parms = self.controls.parms()
        schemaDict = {}

    def _loadHip(self, file=None, hash=None):
        """
        Open a hip file 
        """

        # Calculate the new files hash
        md5_hash = hashlib.md5()
        with open(self.hipFile, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)

        # if a hash has been provided to verify the new file, make sure they match
        if hash:
            if hash != md_hash.hexdigest():
                logging.error("New file hash does not match provided one")
                return

        # If we are loading a new file and not reloading one in the same place update
        # our file name
        if file:
            self.hipFile = file

        # Actually load the file and save the hash to the object
        hou.hipFile.load(self.hipFile)
        self.hipFileHash = md5_hash.hexdigest()

    def _detectChanges(self):
        """
        This function detects changes in the hip file that might require a re-import
        """
        md5_hash = hashlib.md5()
        with open(self.hipFile, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                md5_hash.update(byte_block)

        return False if md5_hash == self.hipFileHash else True

    def _reloadIfChanged(self):
        if self._detectChanges():
            self._loadHip()

    def writeControls(self, controls):
        """
        Write the parameters from json into the control node
        """
        self._reloadIfChanged()
        controls.setParms(controls)

    def exportPlainFile(self):
        self._reloadIfChanged()
        out.render()

    def exportPreviewFile(self):
        self._reloadIfChanged()
        out_gl.render()

    def exportUVFile(self):
        self._reloadIfChanged()
        out_uv.render()
