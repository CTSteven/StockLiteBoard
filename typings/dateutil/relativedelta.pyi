from datetime import timedelta

class relativedelta:
    def __init__(self, dt1, dt2=None): ...
    def __add__(self, other): ...
    def __sub__(self, other): ...
    def __radd__(self, other): ...
    def __rsub__(self, other): ...
    def __mul__(self, other): ...
    def __divmod__(self, other): ...
    def __rdivmod__(self, other): ...
    def __neg__(self): ...
    def normalized(self): ...