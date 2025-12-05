from .Projectile_class import Projectile

class Particle(Projectile):
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "col","_alive") #added _alive to the slots

    def __init__(self, x, y, vx, vy, life, size, col):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.col = col
        super().__init__(x,y,vx,vy)   #--> super for attributes accessing and calling parent init
        

    def step(self, dt):
        self.vy += self.GRAVITY * dt * 0.1  # very light gravity on particles
        self.vx += self.WIND * dt * 0.3  # particles affected a bit by wind
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    @property  #--> implemented the property for alive so that it can be true or false in projectile class
    def alive(self):
        return self.life > 0
       

    @alive.setter
    def alive(self, value):
   
        self._alive = value

    
        
    
