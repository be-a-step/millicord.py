from millicord.idol import IdolManager
import os

IDOLS_DIR = os.path.join(os.path.dirname(__file__), 'idols')

manager = IdolManager()
manager.load_from_directory(IDOLS_DIR)
manager.loop()
