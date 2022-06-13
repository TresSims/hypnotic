import hashlib


def calcHash(file):
    """
    Calculate an md5 hash of the on disk hip file to detect changes.
    """
    md5_hash = hashlib.md5()
    with open(file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)

    return md5_hash.hexdigest()


def validateInput(json, schema):
    """
    Validate the incoming control arguments with the Hypnotic app's schema.
    """
    try:
        result = self.controlSchema.load(controls)
    except ValidationError as e:
        logging.error(e)
        return None

    for key in result:
        # Don't allow for houdini special characters to be passed as parameters
        if type(result[key]) == str:
            result[key] = result[key].strip("`@$")

    return result
