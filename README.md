# astrocode_explorers 
Level of Achievement: Apollo 11

Instructions to run PoC:

Firstly, install pygame by pip install pygame-ce
Then download our file from github, and run game1.py by python3 game1.py

Intro
In today’s digital world, computational thinking is a foundational skill, but formal coding education often begins too late, typically during secondary or tertiary levels. This can result in students feeling overwhelmed by syntax-heavy programming when introduced later in life.
AstroCode Explorers aims to bridge this gap by introducing children (ages 10 and up) to core programming concepts in a playful, visual, and gamified environment. Through drag-and-drop command blocks, kids can learn programming logic without typing, which lowers the barrier to entry and makes coding fun and accessible.



Visual Block Coding
Players build a queue of actions by selecting command blocks (e.g., move, shoot).
Directional Movement
The astronaut can be rotated and moved forward, left, right, or down.
Shooting Mechanic
Players can shoot at enemies using a visual laser gun when facing the right direction.
For-Loop Logic
Advanced levels introduce a looping mechanism where commands repeat.
Modular Level System
Each level is implemented as a separate class with its own logic and layout.







Game Description and Storyline

This game involves a stranded astronaut on an unknown planet trying to survive until he is able to gather the resources he needs to build a spaceship to get back to earth. However, the planet is ruled by aliens who are hostile to him, and thus he needs to protect himself from them while embarking on this mission to escape the unknown planet. Hence, he would need to farm resources and build tools and weapons with it, which is where automation will help him a lot in order to complete his mission in the fastest possible time. Using code blocks to create such automated programs is the main essence of this game.

Game Levels and Progression

Our game aims to progressively introduce programming concepts by gradually increasing the difficulty of the tasks, starting from the simplest one, which would be to destroy stationary entities like special plants, metal ores, minerals etc, after having to navigate through obstacles to find them. The next few levels would involve attacking aliens and farming more items, with the use of for loops, if-else statements and arrays to make navigation and attacking more efficient. After that, things get more challenging as now the astronaut needs to create factory-like machines in order to produce the resources he needs, as well as create defensive buildings to protect him from more powerful aliens. This is where higher level concepts like recursion, functions and Object Oriented Programming (OOP) comes into play. 

Overall, this game is supposed to feel like the users are actually playing the game, being able to move freely to farm and build defenses. The tasks in the game are closely aligned with the coding concepts to be learnt, like for example using functions and loops in machines which continuously takes in raw materials as inputs and outputs the objects needed by the player, and also using recursion to recursively search for certain types of items around the unknown planet. Hence, this is a game that allows players to visualise programming concepts and see how they work, by allowing users to try putting together code blocks and observe the corresponding mechanisms.


User Stories

As a child (primary user), I want to solve fun puzzles by arranging commands so I can see how coding logic controls the game character’s actions.
As a player, I want a game that challenges me to think outside the box and allows me to be creative to solve them through a wide variety of means and possibilities.
As a casual learner, I want a short tutorial and immediate feedback so I can quickly understand the puzzle mechanics and track my improvement.
As a player, I want a game with an engaging storyline which allows me to be the main character in this story for a more special experience
As a player, I want a game that is easy to follow along and gradually increases the difficulty instead of being too easy or too difficult all the time.

Features
Core Game Loop & States
[Current Progress]
Game States: The game transitions between a STATE_START (main menu), STATE_LEVELS (level selection screen), and specific STATE_LEVEL1, STATE_LEVEL2, STATE_LEVEL3 for gameplay.
Main Loop: A continuous game loop handles event processing, updates game logic, and draws elements for the current state.
Delta Time (dt): Uses dt (delta time) for frame-rate independent movement and updates, ensuring consistent speed across different machines.
Simple win screen: We have only one type of popup that displays when the player wins currently, and that just displays “Good Job”, and returns to the level selection screen when pressed
[Proposed]
Game Progression: Implement clear transitions between levels upon completion, potentially unlocking new commands or features.
Save/Load Game: Allow players to save their progress and load previously saved games.
Player & Alien Mechanics
[Current Progress]
Player (Robot) Character:
Movable within the battlefield.
Has a visible health bar (self.health).
Can fire bullets.
Position and orientation (angle) are updated based on commands.
Alien (Target) Character:
Static position as the target.
Has a visible health bar (self.health).
Can fire bullets at the player (specifically in Level 3).
Health decreases upon being hit by player bullets.
[Proposed]
Player Abilities: Introduce additional player abilities beyond basic movement and shooting, possibly tied to character upgrades.
Alien AI Behavior: Implement more complex AI for the alien, allowing it to move, evade, or use different attack patterns based on game state.


[Current Progress]
Command Palette: A dedicated area displays available commands for drag-and-drop.
Main Code Area: Players can drag and drop commands into a sequence to program the robot's actions.
Command Types:
Move Forward: Moves the player a fixed distance in the direction it's facing.
Turn Left: Rotates the player 90 degrees counter-clockwise.
Turn Right: Rotates the player 90 degrees clockwise.
Reverse: Moves the player a fixed distance backward along its current axis.
Shoot: Fires a bullet from the player's gun.
For Loop: Allows nesting commands to repeat a sequence a specified number of times (editable iterations).
If Statement: Allows nesting commands to execute conditionally based on a game state (e.g., alien bullet shape).
Nested Commands: For Loop and If Statement commands support nesting other commands within them, enabling more complex programs.
Command Execution: Commands are executed sequentially from a queue with a small delay for visual feedback.
Conditional Logic: If Statement can check the shape of the closest approaching alien bullet to determine if nested commands should run.
Shoot Target Selection (Level 3): In Level 3, the Shoot command allows cycling through different bullet shapes (circle, square, triangle) for strategic targeting.
[Proposed]
More Variables for Conditionals: Expand the If Statement to check other game variables (e.g., player health, alien health, distance to target).
Customizable Command Parameters: Allow players to input specific values for movement distance, turn angles, or loop iterations directly (beyond just cycling).
Debugging Tools: Implement features like step-through execution, breakpoints, or visual indicators of the currently executing command.

Bullet & Collision System
[Current Progress]
Bullet Firing: Player and alien can fire bullets.
Three Bullet Shapes: As seen from classes Circle, Square and Triangle , our bullets currently only have 3 shapes
Bullet Movement: Bullets travel at a constant speed in a straight line.
Player-Bullet Collision: Player bullets damage the alien.
Alien-Bullet Collision: Alien bullets damage the player (in Level 3).
Bullet-to-Bullet Collision: Bullets from the player and alien can collide mid-air and destroy each other. A specific counter-logic is implemented where certain player bullet shapes can "counter" alien bullet shapes, dealing damage to the alien if the counter is successful, or damaging the player if not.
[Proposed]
Bullet Visual Effects: Add particle effects or animations for bullet impacts and destruction.
Different Bullet Properties: Introduce bullets with varying speeds, sizes, or shapes (potentially star shaped, hexagon shaped, ellipse etc).
Levels
[Current Progress]
Three Playable Levels: Level1, Level2, and Level3 are implemented.
Level Reset: Each level can be reset to its initial state, including player/alien positions and health.
Level Completion: Levels are completed when the alien's health reaches zero. In Level 3, the level also completes if the player's health reaches zero (defeat condition).
[Proposed]
Unique Level Objectives: Introduce varied objectives beyond just defeating the alien (e.g., reach a specific point, collect items).
Level Design: Introduce different "battlefield" layouts or environmental elements that influence gameplay.

                                          
User Interface
[Current Progress]
Start Screen: Features "Start Game," "Select Level," and "Quit" options.
Level Selection Screen: Allows choosing between implemented levels.
Buttons: Interactive buttons for various actions (Run, Reset, Start, Quit, Level Selection).
Code Area Visuals: Commands are drawn as distinct blocks, with nested commands visually indented.
Pop Ups: Simple popups indicate "Good Job!" (level completion) or "You were defeated!" (player health zero).
[Proposed]
Improved Drag-and-Drop: Visual feedback during dragging, clearer insertion points.
Error Indicators: Visual cues for invalid command sequences or syntax errors.
In-game Tutorial: Guided introduction to the command programming system.



What This PoC Demonstrates
The foundational interaction logic of our game


A visual command system where players construct a queue of instructions


Core programming concepts: movement, direction, shooting, and for-loops


Collision detection and visual success feedback


A modular, scalable structure for level design



 Known Limitations
Only two levels are implemented so far (Level 1 and Level 2)


No save system or user accounts yet


Commands cannot be removed or reordered once placed


For-loop only supports a hardcoded repeat value (x3)


No sound or accessibility features yet


Limited UI polish (e.g., minimal animations or tutorials)
