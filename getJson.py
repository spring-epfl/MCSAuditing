import json
import sys

def get():
    try:
        with open("pipelineJson.json") as config_file:
            return json.load(config_file)
    except:
        sys.stderr.write("No pipelineJson file found. Please adjust the settings.")
        exit(-1)

