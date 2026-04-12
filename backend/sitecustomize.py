"""
sitecustomize.py
Automatically executed by Python on startup when placed in the project root.
Adds the KAL root directory (where setu_aa_client.py lives) to sys.path
so all AA modules are importable from anywhere in the project.
"""
import sys
import os

# This file lives at: KAL/backend/sitecustomize.py
# KAL root is one level up
kal_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if kal_root not in sys.path:
    sys.path.insert(0, kal_root)
