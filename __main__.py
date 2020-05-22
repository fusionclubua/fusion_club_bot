import sys
from . import app
if __name__ == "__main__":
    print("sys.path: {}".format(sys.path))
    app.main(sys.argv)