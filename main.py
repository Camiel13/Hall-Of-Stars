import os
import sys

# Ensure working directory is set to the application directory when packaged
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(os.path.abspath(sys.executable)))

from hallofstars import Game

app = Game()
app.run()