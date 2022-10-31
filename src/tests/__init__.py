# Prepares environment for testing

import os, sys

TESTS_PATH   = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(TESTS_PATH, os.pardir))

# Adds project dir to python path so source code can be imported
sys.path.append(PROJECT_PATH)
