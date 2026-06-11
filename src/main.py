import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app import App

if __name__ == "__main__":
    app = App()
    app.run()