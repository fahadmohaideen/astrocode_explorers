import pyglet
from pyglet.window import mouse

window = pyglet.window.Window(800, 600, caption="AstroCode Explorers")

background = pyglet.resource.image("assets/background.png")
astronaut_img = pyglet.resource.image("assets/astronaut.png")
astronaut = pyglet.sprite.Sprite(astronaut_img, x=100, y=100)
astronaut.scale = 0.2

enemy = pyglet.shapes.Rectangle(700, 100, 50, 50, color=(255, 0, 0))
enemy_alive = True

command_queue = []
command_index = 0
executing = False
labels = []

button_move = pyglet.text.Label("Move", x=20, y=550, font_size=14, color=(255, 255, 255, 255))
button_fire = pyglet.text.Label("Fire", x=90, y=550, font_size=14, color=(255, 255, 255, 255))
button_run = pyglet.text.Label("Run Code", x=160, y=550, font_size=14, color=(0, 255, 0, 255))

def add_command(cmd):
    command_queue.append(cmd)
    update_command_display()

def update_command_display():
    global labels
    labels = []
    for i, cmd in enumerate(command_queue):
        labels.append(pyglet.text.Label(f"{i+1}. {cmd}", x=20, y=500 - i*20, font_size=12, color=(255, 255, 0, 255)))

@window.event
def on_draw():
    window.clear()
    background.blit(0, 0)
    astronaut.draw()
    if enemy_alive:
        enemy.draw()
    button_move.draw()
    button_fire.draw()
    button_run.draw()
    for label in labels:
        label.draw()

@window.event
def on_mouse_press(x, y, button, modifiers):
    global executing, command_index
    if 20 <= x <= 70 and 550 <= y <= 570:
        add_command("move")
    elif 90 <= x <= 140 and 550 <= y <= 570:
        add_command("fire")
    elif 160 <= x <= 250 and 550 <= y <= 570:
        if command_queue:
            executing = True
            command_index = 0

def execute_command(dt):
    global command_index, executing, enemy_alive
    if executing and command_index < len(command_queue):
        cmd = command_queue[command_index]
        if cmd == "move":
            astronaut.x += 50
        elif cmd == "fire":
            if astronaut.x + astronaut.width >= enemy.x:
                enemy_alive = False
        command_index += 1
    elif executing:
        executing = False

pyglet.clock.schedule_interval(execute_command, 1.0)
pyglet.app.run()




