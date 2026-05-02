from cuid2 import Cuid

_generator = Cuid()

def generate_cuid():
    return _generator.generate()
