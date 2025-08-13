import sys
print(f"Python version: {sys.version}")
print("Basic test completed successfully!")

try:
    import pandas as pd
    print("Pandas imported successfully")
except ImportError:
    print("Pandas not available")

try:
    import numpy as np
    print("Numpy imported successfully")
except ImportError:
    print("Numpy not available")

try:
    import requests
    print("Requests imported successfully")
except ImportError:
    print("Requests not available")

print("Test completed!")