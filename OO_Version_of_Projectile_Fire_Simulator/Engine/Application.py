from .Simulator_class import Simulator
import tkinter as tk


class App:
    def run(self):
        root = tk.Tk()
        root.title("Pro Fire Simulator — Tkinter (no external deps required)")
        sim = Simulator(root)

        #Variable Comnfiguration according to the user
        
        sim.AIR_DRAG=0.995  
        sim.WIND=0.0 
        sim.GRAVITY=700.0
        sim.WIDTH=1000   
        sim.HEIGHT=700
        sim.TARGET_FPS=60  
        sim.PROJECTILE_SPEED=1200.0 
        sim.MAX_PROJECTILES=1000  
        sim.MAX_PARTICLES=8000
        sim.AUTO_FIRE_RATE=100.0  
        sim.GROUND_Y=sim.HEIGHT-40


        root.mainloop()







