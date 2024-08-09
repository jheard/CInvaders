from copy import copy
import tkinter as tk
from tkinter import ttk
from math import sqrt
from random import randint

class Thing():
    def __init__(self, canvas: tk.Canvas, x: float, y: float, 
                 radius: float, id: 'int|None' = None) -> None:
        self.x = x
        self.y = y
        self.id = id
        self.radius = radius
        self.radiusSq = self.radius * self.radius
        self.canvas = canvas

    def collides(self, other: 'Thing') -> bool:
        if self.radiusSq >= (self.x - other.x) ** 2 + (self.y - other.y) ** 2:
            return True
        return False

class Invader(Thing):
    def __init__(self, canvas: tk.Canvas, x: float, y: float, 
                 img: tk.PhotoImage) -> None:
        super().__init__(canvas, x, y, img.height() / 2)
        self.id = canvas.create_image(x,y,image=img,tags="invader")

class Player(Thing):
    def __init__(self, canvas: tk.Canvas, x: float, y: float, 
                 radius: float) -> None:
        super().__init__(canvas, x, y, radius)
        self.step = 4
        self.move = [0,0]
        self.img = tk.PhotoImage("player",file="hacker.png")
        self.id = self.canvas.create_image(x,y,image=self.img,tags="player")
        self.score = 0
    
    def collides(self, other: Thing) -> bool:
        if super().collides(other):
            self.score += 1
            return True
        return False
    
    def moving(self, event) -> None:
        match(event.keysym):
            case "Right":
                self.move[0] = self.step
            case "Left":
                self.move[0] = -self.step
            case "Up":
                self.move[1] = -self.step
            case "Down":
                self.move[1] = self.step
    
    def stop_moving(self,event) -> None:
        match(event.keysym):
            case "Right" | "Left":
                self.move[0] = 0
            case "Up" | "Down":
                self.move[1] = 0
    
    def toward(self,event) -> None:
        dx = event.x - self.x
        dy = event.y - self.y
        mag = sqrt(dx * dx + dy * dy)
        if mag < self.radius / 2:
            self.move = [0,0]
            return
        dx /= mag
        dy /= mag
        self.move[0] = self.step * dx
        self.move[1] = self.step * dy

    def update(self) -> None:
        self.x += self.move[0]
        self.y += self.move[1]
        self.canvas.move(self.id,*self.move)        

class CInvaders(tk.Tk):
    def __init__(self, interval: int = 50) -> None:
        super().__init__()
        self.title("CInvaders")
        self.resizable(False,False)
        self.interval: int = interval
        self.frame = tk.Frame(self,width=400,height=600)
        self.frame.grid()
        self.damage: tk.DoubleVar = tk.DoubleVar()
        self.damage.set(0)
        self.progress = ttk.Progressbar(self.frame,length=378,
                                        variable=self.damage)
        self.progress.grid(column=0,row=0)
        self.canvas = tk.Canvas(self.frame,height=450)
        self.canvas.grid(column=0,row=1)
        self.bg = tk.PhotoImage("bg",file="bg.png")
        self.canvas.create_image(189,225,image=self.bg)
        self.player = Player(self.canvas,75,75,32)
        self.invader_img = tk.PhotoImage("invader",file="invader.png")
        self.spawn_timer = 2500
        self.ppi: float = 0.2
        self.invaders: list[Invader] = []
        self.bind("<KeyPress>",self.player.moving,add=True)
        self.bind("<KeyRelease>",self.player.stop_moving,add=True)
        self.bind("<Motion>",self.player.toward)
        self.after(self.interval,self.updater)
        self.spawnerID = self.after(500, self.spawner)
        self.running = True
        self.resetEvent: str|None= None

    def updater(self) -> None:
        if self.damage.get() >= 100:
            self.canvas.create_text(180,200,text=f"Burnt Out!\nScore: {self.player.score}",
                                    tags="lose",fill="red", font=("Comic Sans MS", 24))
            self.resetEvent = self.bind("<ButtonPress>",self.reset)
            self.after_cancel(self.spawnerID)
            self.running = False
            return
        self.player.update()
        for inv in copy(self.invaders):
            if self.player.collides(inv):
                self.canvas.delete(inv.id)
                self.invaders.remove(inv)
        if len(self.invaders):
            self.damage.set(self.damage.get() + self.ppi * len(self.invaders))
        else:
            self.damage.set(self.damage.get() * 0.998)
        self.after(self.interval, self.updater)
    
    def reset(self, event) -> None:
        self.damage.set(0)
        self.player.score = 0
        for inv in self.invaders:
            self.canvas.delete(inv.id)
        self.invaders.clear()
        self.running = True
        self.canvas.delete("lose")
        self.unbind("<ButtonPress>")
        self.after_idle(self.spawner)
        self.after_idle(self.updater)
    
    def spawner(self) -> None:
        x = randint(0,self.canvas.winfo_width())
        y = randint(0,self.canvas.winfo_height())
        self.invaders.append(Invader(self.canvas,x,y,self.invader_img))
        if self.running:
            self.spawnerID = self.after(self.spawn_timer + randint(0,self.spawn_timer),self.spawner)

cinvaders = CInvaders()
cinvaders.mainloop()
