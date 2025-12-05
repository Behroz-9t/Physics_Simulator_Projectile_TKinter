class Projectile:
    __slots__ = ("x", "y", "vx", "vy", "alive", "age", "radius", "owner","_GRAVITY","_WIND","_AIR_DRAG") #added the gravity wind and airdrag in slots

    def __init__(self, x, y, vx, vy,AIR_DRAG=0.995,GRAVITY=700.0,WIND=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.age = 0.0
        self.alive = True
        self.radius = 5.0
        self.owner = None
        self.AIR_DRAG =AIR_DRAG
        self.GRAVITY=GRAVITY
        self.WIND=WIND


#implmented the getters and setters for the gravity, airdrag and wind to change/access them in the application.py

    @property  
    def GRAVITY(self):
        return self._GRAVITY
    @GRAVITY.setter
    def GRAVITY(self,valueG):

        if isinstance(valueG,(int,float)):
            self._GRAVITY = valueG
        else:
            raise ValueError("Gravity parameter can only be in float or integer")



    @property
    def AIR_DRAG(self):
        return self._AIR_DRAG
    @AIR_DRAG.setter
    def AIR_DRAG(self,valueA):

        if isinstance(valueA,(int,float)):
            self._AIR_DRAG = valueA
        else:
            raise ValueError("Air Drag parameter can only be in float or integer")
       



    @property
    def WIND(self):
        return self._WIND
    @WIND.setter
    def WIND(self,valueW):

        if isinstance(valueW,(int,float)):
            self._WIND = valueW
        else:
            raise ValueError("Wind parameter can only be in float or integer")
        



    def step(self, dt):
        # Apply wind and gravity; drag multiplicative
        self.vx += self.WIND * dt
        self.vy += self.GRAVITY * dt
        # simple drag
        self.vx *= 1.0 - (1.0 - self.AIR_DRAG) * dt * 60.0
        self.vy *= 1.0 - (1.0 - self.AIR_DRAG) * dt * 60.0
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt