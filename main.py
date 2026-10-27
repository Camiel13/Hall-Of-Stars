import os
import sys

# Ensure working directory points to bundled data (_MEIPASS / _internal) when packaged
if getattr(sys, "frozen", False):
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    os.chdir(base_dir)

from hallofstars import Game

app = Game()
app.run()
