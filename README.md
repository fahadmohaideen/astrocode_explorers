Table of Contents
Orbital 2025 Milestone 3	1
Table of Contents	2
Links and Resources	6
Current Builds	6
Code Base	6
Milestone 2	6
Milestone 3	6
Project Overview	7
Purpose & Motivation	7
Target Audience	7
User Stories	7
Features summary	8
Game Story	8
Installation & Setup	9
Prerequisites	9
How To Run	9
Game Overview	10
Gameplay breakdown	10
Feature Breakdown (Milestone-Based)	17
Milestone Progression	17
Milestone 1	17
Key Features	17
1. Block Coding Interface	17
2. Movement System	17
Progressive Learning Through Levels	17
Level 1 – Sequential Logic	17
Level 2 – Looping with For Loops	18
Level 3 – Conditionals with If Blocks	18
Shooting & Bullet Mechanics	18
Bullet Pooling	18
Health System	18
Nesting Functionality	18
Development Limitations	19
Milestone 2: Free Roam	19
Key features	19
FreeWorld Mode – New Game Paradigm	19
FreeWorld Structure & Mechanics	19
Game View ↔ Code Editor View	19
Camera & Map Rendering	20
Alien Spawning Logic	20
Alien Minimap & Visual Guidance	20
Gameplay Logic Enhancements	20
Conditional Logic (Phase 2)	20
Loop Logic (Phase 3)	21
Bug Fixes & Improvements	21
Nesting Bug Fix	21
Additional Features & Improvements	21
Milestone 3	21
1. Level Locking & Progress Saving System	21
2. Complete Overhaul of Level 1 (Sequencing Tutorial)	22
3. Refinement of Level 2 (Conditional Logic Challenge)	22
4. Advanced Gameplay Mechanics & Level 3 Overhaul	22
5. Implementation of Level 4 (Real-Time Capstone)	22
6. Enhanced User Feedback & UI Polish	22
7. Visual Polish & Immersion	23
8. Significant Bug Fixes & Code Refactoring	23
Code Architecture	23
High-Level Structure	23
main.py(Entry Point)	23
core/	23
ui/	23
entities/	24
levels/	24
Key Components & Responsibilities	24
base_level.py (The Blueprint)	24
player.py & alien.py (The Actors)	24
levelX.py (The Stages)	25
Command Execution System	25
Design Decisions & Rationale	26
Software engineering practices	26
Version Control & Workflow (Git)	26
Single Responsibility Principle (SRP)	28
Open-Closed Principle (OCP)	29
Liskov's Substitution Principle (LSP)	30
Interface Segregation Principle (ISP)	30
Dependency Inversion Principle (DIP)	30
Software Testing	31
Test Case Coverage	31
Test Suite Overview	31
Player Input & UI	31
S/N	31
Test Case	31
Classification	31
Expected Result	31
1	32
Command Block Interaction	32
Positive / Black-Box	32
Drag, Run, Reset block behavior works as expected	32
Level 1: Sequencing	32
S/N	32
Test Case	32
Classification	32
Expected Result	32
1	32
Player Movement Control	32
Negative / Black-Box	32
WASD keys do nothing	32
2	32
Command Execution	32
Positive / Black-Box	32
Player moves + shoots in order	32
3	32
Target Damage	32
Positive / White-Box	32
Target takes damage	32
Level 2: Conditional Logic	32
S/N	32
Test Case	32
Classification	32
Expected Result	32
1	32
Shooting mechanism for player	32
Positive / Black-Box	32
Player should shoot in the correct direction towards alien	32
2	32
Correct Hit	32
Positive / Black-Box	32
Deals damage to alien; player unharmed	32
Level 3: Iteration & Resource Management	32
S/N	32
Test Case	32
Classification	32
Expected Result	32
1	33
Shooting mechanism of alien bullets	33
Positive / Black-Box	33
Alien should shoot bullets in the correct direction towards the player, as well as in fixed intervals	33
2	33
Player taking damage	33
Negative / Black-Box	33
When hit by an alien bullet, the player should take damage	33
Level 4: Real-Time Application (In the future, by Splashdown)	33
S/N	33
Test Case	33
Classification	33
Expected Result	33
1	33
Player Movement	33
Positive / Black-Box	33
WASD movement; editor disabled	33
2	33
Alien AI	33
Positive / Black-Box	33
Chasing + shooting behavior present	33
3	33
Real-Time Combat	33
Positive / Black-Box	33
Player shoots; type-matching logic still applies	33
Integration Testing	33
UI/UX Improvements	34

Links and Resources

Current Builds





Code Base

Link to repository: AstroCode Explorers

Milestone 2

Poster: 
Video: 

Milestone 3

Poster: 
Video: 
Project File:  
https://drive.google.com/file/d/1Qixzo_0g0U-KkwHJ7ViYYygg1itgXo7z/view?usp=sharing








Project Overview

Level of Achievement: Apollo 11
Purpose & Motivation
In an increasingly digital world, computational thinking is a critical foundational skill. However, formal coding education often begins at secondary or tertiary levels, potentially overwhelming students with complex syntax. AstroCode Explorers aims to bridge this gap by offering an early, playful, and visual introduction to core programming logic. By removing the barrier of complex syntax through an intuitive block-based interface, we make coding approachable and enjoyable, empowering young learners to grasp fundamental concepts like sequencing, repetition, and conditional logic. This project reflects a commitment to making STEM education engaging and preparing the next generation for a technologically driven future.
Target Audience
AstroCode Explorers aims to bridge this gap by introducing children (ages 10 and up) to core programming concepts in a playful, visual, and gamified environment. Set in a compelling narrative of a stranded astronaut on a hostile alien planet, players use a visual, drag-and-drop block-based interface to program their character's actions. Through drag-and-drop command blocks, kids can learn programming logic without typing, which lowers the barrier to entry and makes coding fun and accessible. The game progresses through a series of increasingly complex challenges, fostering logical reasoning, problem-solving, and the core principles of automation and algorithm design in a fun, accessible, and syntax-free environment. 
 	
User Stories
As a child, I would like to solve puzzles using block commands.


As a player, I want creativity, feedback, and progression.


As a learner, I want short tutorials and simple challenges.



Features summary
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




Game Story
You're a stranded astronaut on a hostile alien planet. However, there are hostile aliens looking to kill anyone or anything that is not their kind. Your objective is to defend yourself against alien attacks, as well as defeating them so that you can access your spaceship, which was stolen by the aliens. This is done progressively through conquering levels in which the aliens you encounter have increasing levels of abilities (e.g. shooting, chasing and cornering the player etc), after which you will have to go to the dungeon of the alien king to defeat him.
Throughout this game, you will have to use coding blocks in order to navigate the astronaut. These coding blocks include movement commands, such as move up, down, right, left, as well as if and loop blocks to more effectively control the movement logic. With the use of automation, resource gathering, and programming to build tools, defeat enemies, and escape, players would be able to visualise how programs work when executing chunks of code, and will thus gain a greater understanding of why and how code is used to control our computers and machines and would better appreciate the significance of programming in our current tech landscape.


Installation & Setup
Prerequisites
Before you can install and run AstroCode, ensure you have the following software installed:
Python 3: AstroCode is developed using Python 3. You can download the latest version from the official Python website: https://www.python.org/downloads/
Recommendation: When installing Python, make sure to check the "Add Python to PATH" option during the installation process, as this simplifies command-line usage.
pip: Python's package installer. pip is usually installed automatically with Python 3. You can verify its installation by running pip --version in your terminal or command prompt.
How To Run

First, you need to obtain the AstroCode project files.
https://github.com/fahadmohaideen/astrocode_explorers (Our github repo link)

 AstroCode ZIP Folder: https://drive.google.com/file/d/1Qixzo_0g0U-KkwHJ7ViYYygg1itgXo7z/view?usp=sharing
Clone from Git Repository: 
Run the following commands:
git clone https://github.com/fahadmohaideen/astrocode_explorers.git
cd astrocode_explorers
pip: Usually comes with Python. Verify via pip --version.
Add Python to PATH during installation.

OR
Download the zip folder
Extract contents
Navigate to main.py and double click to run (Ensure dependencies are installed before)

Setting up Virtual Environment:
Create a virtual environment: python -m venv venv
Activate the virtual environment : .\venv\Scripts\activate (on windows) or source venv/bin/activate (Mac/Linux)

You'll know the virtual environment is active when you see (venv) preceding your command prompt.
Running the game itself:
Ensure your virtual environment is active.
Install dependencies (Pygame in this case): pip install pygame
Navigate to the root of your project directory (where main.py is located).
Execute the game: python main.py

The AstroCode game window should now appear, allowing you to start your cosmic coding adventure!

Game Overview
Gameplay breakdown

Welcome to AstroCode! A Player's Guide

Welcome, astronaut! AstroCode is a game where you solve challenges by thinking like a programmer. Instead of just reacting, you'll build simple programs to control your character. Let's get started on your mission.

Step 1: The Main Menu
When you launch the game, you'll be at the main menu. You have two main options:
Start Game: This will take you to the Level Selector to begin your adventure.
Quit: This will close the game.

Click "Start Game" to proceed.


Step 2: The Level Selector
This is your mission hub. You will see a list of all the levels in the game.
Progression: When you first start, only Level 1 will be available. You must complete a level to unlock the next one. This is to make sure you learn the skills in the right order!
Locked Levels: Levels you haven't reached yet will be grayed out and marked as "(Locked)".


Click on "Level 1" to begin your training.

Step 3: Level 1 - Learning to Walk & Shoot (Sequencing)

The Goal: Your mission is simple: destroy the single red target on the screen.
The Challenge: You'll immediately notice you cannot move with the W, A, S, D keys. This is intentional! Your goal is to give the astronaut a list of instructions to follow.

How to Complete the Level:
Understand Your Interface: The screen is split into two main areas:
Command Palette (Left): This is your toolbox. It contains all the command blocks you can use, like Move Up, Move Down, and Shoot.
Code Area (Right): This is where you build your program.
       

Build Your Program:
Click and drag a command block from the palette on the left into the code area on the right.
To get to the target, you'll need to move down. Drag the Move Down block into the code area.
One Move Down isn't enough. Drag another Move Down block and place it right below the first one. Your character will now execute two moves in a row.
Finally, you need to shoot. Drag the Shoot block and place it at the end of your list.


Run Your Program:
Click the green "Run" button at the bottom.
Watch as your astronaut follows your instructions perfectly: they move down, move down again, and then fire a laser straight to the right, destroying the target.

Congratulations! You've just learned the most fundamental concept in programming: sequencing. The order of your commands is critical to success.

Step 4: Level 2 - Thinking with if  Statements (Conditional Logic)

The Goal: Defeat the three hostile aliens.
The Challenge: This level is a puzzle. You'll notice two things:
All three aliens look identical! You can't tell them apart just by looking.
When you shoot at them, your bullets do no damage! This is because each alien is immune to the wrong type of weapon.

How to Complete the Level:
Introduce the if Block: now have a new command: if. Think of this block as your ship's scanner. It lets you ask a question before you act.
      
Scan and Shoot:
Drag an if block into the code area. It will say something like if Alien Type A is near.... This is your scanner checking for a specific alien type.
Now, look at your Shoot block. It has a new option on it that lets you cycle through different bullet types: "Alien Type A", "Alien Type B", and "Alien Type C".
The solution is to match the scan with the shot. Build a program like this:
if Alien Type A is near
shoot (with "Alien Type A" bullet selected)


Do this for all three alien types! Build a list of three if statements.

BE CAREFUL! The Penalty: If you hit an alien with the wrong bullet type (e.g., shooting a "Type B" alien with a "Type A" bullet), your own ship will take heavy damage! Guessing is dangerous. You must use the if scanner to be sure.

Lesson Learned: You've just used conditional logic. You taught your astronaut how to make decisions based on the information available, a core skill for any programmer.

Step 5: Level 3 - Working Efficiently with for loops (Iteration)

The Goal: Defeat the three aliens.
The Challenge: This is a test of efficiency. The aliens are tougher, they shoot back, and they have energy shields that turn on and off. But the biggest challenge is a new rule: You only have 5 Run Attempts!

How to Complete the Level:
The Problem with Single Shots: The aliens are strong. One shot isn't enough to destroy them. If you build a program with just one shoot command, you'll have to click "Run" many times, quickly using up your limited attempts.
Introduce the for loop block: You have a new tool: the for loop. This block tells your astronaut to repeat an action multiple times.
Build an Efficient Program:
Instead of dragging three separate shoot blocks, build your program like this:
for loop (3 times)
Shoot
             
This program tells your astronaut: "When I say go, shoot three times in a row." This powerful combo will be enough to break through the shields and destroy an alien, and it only uses one of your precious run attempts!

Timing is Key: Watch the aliens' shields. Run your powerful loop program when an alien's shield is down to make sure your shots count.
           w

Lesson Learned: You've mastered iteration. You're no longer giving one command at a time; you're creating efficient loops to solve bigger problems, a massive step forward in your coding journey.

Step 6: The Final Exam - Real-Time Action!

The Goal: Survive and defeat the three hostile aliens.
The Challenge: This is your final test. The code editor is gone. WASD movement is enabled. The aliens are actively chasing and shooting at you.

How to Complete the Level:
Apply Your Knowledge: You must now manually do everything you taught your astronaut before.
Identify and Attack: The aliens are now visibly different colors (red, green, blue). You need to remember their weaknesses from what you learned.
Dodge and Weave: Use the WASD keys to move your character, dodge incoming projectiles, and position yourself for a clear shot.
Shoot Correctly: Aim at an alien and fire. Remember, only the matching bullet type will do damage!

You've Done It! You've completed your training. You started by learning how to give simple, ordered instructions, then learned to make decisions with if and work efficiently with for. Now, you've applied all of that knowledge in a real-time challenge.
Good luck, AstroCode pilot.


Feature Breakdown (Milestone-Based)
Milestone Progression
M1: Game states, basic mechanics, drag-and-drop UI, bullet logic


M2: Free movement, integrated levels, improved conditionals, battlefield integration


M3: AI, debugging tools, step-through command execution, level-specific objectives


Milestone 1
Key Features
Establish the foundational structure and mechanics of AstroCode, a 2D educational game that introduces children to programming through drag-and-drop command blocks, inspired by LEGO-style block logic.
Core Features Implemented
1. Block Coding Interface
Players assemble sequences using colored command blocks:
 Move Up, Move Down, Move Left, Move Right, and Shoot.
Designed to resemble building with virtual LEGOs, emphasizing sequencing and logic flow.


2. Movement System
Each directional command moves the astronaut a fixed distance.
Players experiment with block quantity to navigate the map correctly.

 Progressive Learning Through Levels
  Level 1 – Sequential Logic
Introduces basic movement and the shooting command.
Objective: Navigate to a red alien target and shoot until its health reaches 0.
Reinforces understanding of command order and movement precision.


 Level 2 – Looping with For Loops
Introduces a for block that can nest commands inside.
Players reuse movement and shooting logic to reduce code block length.
Teaches iteration and efficiency in logic construction.


 Level 3 – Conditionals with If Blocks
Introduces if statements and bullet-shape matching logic.
Players must select the correct bullet type to counter the alien’s shape:


Match logic:
{"circle": "square", "square": "triangle", "triangle": "circle"}
Incorrect shapes result in damage to the astronaut, enforcing decision-making and conditional logic.
 Shooting & Bullet Mechanics
Shoot commands trigger Player.shoot_bullet(), which adds bullets to an internal array.
Bullets move each frame (update()), get drawn (draw_bullets()), and are deactivated upon impact.
Bullets that hit targets are moved to a bullet pool for reuse.


 Bullet Pooling
Bullets that hit targets are added to bullet_pool.
If the pool is non-empty, bullets are reused instead of creating new ones.
A 10% chance exists to permanently remove used bullets, optimizing memory and improving performance.
 Health System
Green health bars shown above both player and aliens.
Updates in real time based on health changes, helping players gauge their success visually.
 Nesting Functionality
Conditional (if) and loop (for) blocks support nested command blocks.
Layout and block positioning were partially functional; overlapping issues noted and deferred for Milestone 2.
 Development Limitations
No modular file system yet; all classes in one script.
Nesting block alignment and rendering still under development.
Collision detection and bullet-typing logic partially functional for Level 3.

Milestone 2: Free Roam
Key features
Milestone 2 focused on implementing a new FreeWorld mode, enhancing player agency, refining coding logic execution, and introducing new control mechanics and gameplay elements to improve immersion and educational value.
 FreeWorld Mode – New Game Paradigm
Phase-based gameplay: Starts with command-driven movement, transitions to free WASD movement.
Keyboard Movement: Once Phase 1 is cleared (shooting a stationary target), players can freely control the astronaut using WASD or arrow keys.
Coding Relevance: Movement is removed from code logic after Phase 1—players now focus on coding interactions, not navigation.
Goal: Blend traditional shooter mechanics with block-based programming to improve player engagement.


FreeWorld Structure & Mechanics
Game View ↔ Code Editor View
Click the astronaut to toggle from game screen to code editor view.
Editor overlays include:


Left box: Available command blocks
Right box: Main command area
Dimmed background for clarity (like a pause/settings screen)


Players edit logic, then click 'Run' or 'X' to execute and return to gameplay.


 Camera & Map Rendering
The camera now follows the astronaut, allowing exploration beyond the screen bounds.
Infinite terrain rendering using background tiles based on player position.


 Alien Spawning Logic
Three aliens spawn randomly, one per quadrant of the map.
Ensures spatial distribution and exploration instead of camping at a single location.


Alien Minimap & Visual Guidance
A top-right minimap shows positions of astronaut and aliens as colored dots:


Type A = red, Type B = green, Type C = purple


Direction vectors drawn when aliens are off-screen, guiding player navigation.


Gameplay Logic Enhancements
 Conditional Logic (Phase 2)
Replaces shape-based conditionals with alien-type matching:


e.g., If Alien Type A → Shoot Type A (red laser)


Introduces colored lasers instead of shaped bullets.
Highlights abstraction and logic binding by type.


 Loop Logic (Phase 3)
Reintroduces for loop with a custom integer box:


Click to set repeat count (up to 2 digits)


Allows freedom to experiment with iteration logic beyond pre-set values.

Bug Fixes & Improvements
Nesting Bug Fix
Fixed issue where nested blocks (inside if or for) would overlap incorrectly.
Cause: Blocks were drawn at fixed vertical spacing based on their initial height.
Fix: Dynamically recalculated Y-offset based on the expanded height of preceding blocks.


Additional Features & Improvements
Improved UX: Game now feels more interactive with movement and visual cues.
Preparations for Milestone 3:
Bullet firing and command execution in FreeWorld were planned but not fully functional in MS2; to be completed in MS3.

Milestone 3
In Milestone 3 we have decided to break down FreeWorld into separate levels (Levels 1–4) that progressively increase in difficulty and are unlocked by completing the previous levels.
The primary goal of Milestone 3 was to evolve AstroCode from a collection of concepts into a cohesive, structured learning experience. This was achieved by overhauling existing levels, introducing robust new mechanics, implementing a progression system, and significantly polishing the user experience.
1. Level Locking & Progress Saving System
Summary: A comprehensive system was created to save and load player progress. A new file, save_data.json, is generated in the project root directory, which stores the highest level the player has unlocked.
Application: Enforces a structured learning path. Levels must be completed in sequence. The LevelSelector UI displays locked levels as grayed-out, disabled buttons.
2. Complete Overhaul of Level 1 (Sequencing Tutorial)
Summary: Level 1 was transformed into a fully-featured tutorial with terrain, player assets, and enforced command-only control.
Changes:
Disabled WASD movement; forced use of command blocks.
shoot_bullet() modified to fire only horizontally.
Purpose: Teaches procedural thinking and basic sequencing.
3. Refinement of Level 2 (Conditional Logic Challenge)
Summary: Level 2 now features "mystery aliens" with randomized types. Players must use if blocks to identify and respond.
Changes:
Minimap and direction indicators use neutral colors.
Enforces use of conditional logic blocks as scanning tools.
4. Advanced Gameplay Mechanics & Level 3 Overhaul
Health Penalty System:
Summary: Wrong bullet type deducts 1/3 of player health.
Effect: Discourages trial-and-error; reinforces logic.
Run-Click Limit:
Summary: Player is limited to five Run attempts per level.
Effect: Teaches efficiency and use of loop blocks.
Enemy Shields & Combat AI:
Summary: Level 3 aliens now toggle shields and fire back.
Effect: Introduces timing, positioning, and tactical coding challenges.
5. Implementation of Level 4 (Real-Time Capstone)
Summary: WASD control enabled; code editor removed.
Effect: Final test of player knowledge—reactive, real-time combat with learned logic.
6. Enhanced User Feedback & UI Polish
Summary: Improved UI with:
Mission briefings
Aligned "Mission Complete" and "Mission Failed" overlays
Effect: Boosts clarity, professionalism, and player feedback.
7. Visual Polish & Immersion
Summary: Bullet sprites in Bullet class now rotate to face travel direction.
Effect: Enhances realism and visual fluidity during combat.
8. Significant Bug Fixes & Code Refactoring
Summary: Numerous critical bugs fixed.
Key Fixes:
Corrected alien shooting logic
Resolved inheritance conflicts using load_assets()
Fixed damage logic across all levels
Resolved crash bugs: TypeError, NameError, AttributeError
Effect: Stable, fully functional application from start to finish


Code Architecture
High-Level Structure

The AstroCode application is built on a modular, state-driven architecture designed for clarity and scalability. The entire project is organized into distinct packages, each with a specific domain of responsibility:
main.py(Entry Point)
Initializes game state and global UI.
Handles state transitions.
Runs the core loop (events, updates, drawing).
core/
constants.py: Screen sizes, states, FPS, colors, game parameters.
utils.py: Starfield animation logic.
Progress_manager.py: Tracks level progress
ui/
button.py: Reusable button component.
level_selector.py: Manages level selection screen.


entities/
player.py, alien.py: Shared logic via inheritance.
bullet.py, bullet_shapes.py: Bullet logic, shapes.
commands.py: Core logic for move, turn, shoot, loops, and conditionals.


levels/
base_level.py: Abstract class defining common game level structure.
level1.py to level4.py: Introduce movement, loops, conditionals, and while-loops progressively.


Key Components & Responsibilities

main.py (The Conductor)
Responsibility: Manages the primary game loop and the overall game state (STATE_START, STATE_LEVELS, STATE_LEVEL1, etc.).
Function: Initializes Pygame, loads all level instances, handles top-level event processing (such as quitting or switching levels), and directs update and draw calls to the appropriate active object. It also connects to the progress manager for saving and loading player data.


 base_level.py (The Blueprint)
Responsibility: Provides a universal template for all game levels.
Function: Implements shared systems—command palette, drag-and-drop code editor, game camera, minimap, directional indicators, and command execution. This ensures consistent structure across levels and simplifies level creation.


 player.py & alien.py (The Actors)
Responsibility: Define the behaviors of the player and enemy entities.
Function:
Player class: Handles health, shooting, and death animation.
Alien class: Includes AI for movement/shooting, shields, and in Level 4, chasing behavior.
 This setup simplifies management of different entity types and supports future scalability.
levelX.py (The Stages)
Responsibility: Defines unique rules, logic, and objectives for each level, supporting a progressive learning curve.
Function:
Level 1: Teaches sequencing using move and shoot blocks. The astronaut must hit a fixed target. WASD is disabled.
Level 2: Introduces conditional logic (if). Players scan visually identical aliens to determine types. Includes health penalty for incorrect shots.
Level 3: Introduces iteration with for loops. Players must solve puzzles under a run-click limit while also facing shielded aliens.
Level 4: Serves as a capstone. Enables real-time WASD movement and removes the code editor. Players apply logic reactively while dodging and countering active alien attacks.

Command Execution System
The command execution system is the primary interface for Levels 1–3. It is implemented in
 base_level.py using a Python generator (yield).
How it Works:
 When the player clicks “Run”, the execute_commands() function is called.
 Instead of executing all commands at once (which would freeze the game), it returns a generator object.The main game loop in main.py then calls next() on this generator once per frame.This non-blocking approach allows commands to execute sequentially over time, while the rest of the game continues to run smoothly.


Transition in Level 4:
 This system is disabled in Level 4. Instead, the update loop in level4.py directly calls self.handle_player_movement(dt, keys), transitioning the game’s core mechanic from turn-based programming to real-time control.This change tests the player’s ability to apply learned strategies under pressure.


Design Decisions & Rationale
State Machine Pattern:
 A state machine was chosen in main.py  to handle game flow transitions
 (e.g., STATE_START → STATE_LEVELS).This approach simplifies navigation, avoids messy if/elif/else chains,and makes the game logic more maintainable and extensible.


Inheritance for Levels:
 A class inheritance structure (Level → Level2 → Level3 → Level4) was used to enforce the DRY (Don't Repeat Yourself) principle.Shared logic such as player movement and asset loading is written once in the parent class and inherited by all levels, reducing duplication and improving maintainability.


Shift to Hybrid Gameplay in Level 4:
 Level 4 removes the code editor and enables direct WASD control. This deliberate design creates a capstone experience, requiring the player to execute the strategies they previously built via block code (e.g., identifying alien types and selecting the correct weapon). It transforms the game from a learning tool into a real-time application of skills, providing a satisfying final test to conclude the player’s programming journey.

Software engineering practices
Version Control & Workflow (Git)
The project is managed using Git for version control, hosted on a cloud-based repository. We adopted the Git Feature Branch Workflow, which is ideal for our development scale and collaborative nature.

Workflow: New features (e.g., "Level 4 implementation," "health penalty system") and bug fixes (e.g., "fix minimap color bug") are developed in their own dedicated branches.
Code Review: Before any new code is merged into the main branch, a Pull Request is created. This allows for peer review, ensuring that new code is not only functional but also adheres to our coding standards and architectural principles.
Stability: This workflow ensures that the main branch always contains a stable, tested, and working version of the game, isolating experimental or in-progress features and minimizing the risk of integration errors.

Code Refactoring & Modularization
A significant effort during development was the transition from a monolithic script to a fully modular architecture. Initially, the entire game's logic, though organized into classes, was contained within a single file exceeding 1600 lines of code. This presented several critical challenges:
Difficult Navigation: Finding specific functions or classes was inefficient.
High Risk of Conflicts: With all code in one file, the chance of merge conflicts during collaboration was extremely high.
Poor Maintainability: A bug in one feature could potentially impact the entire codebase, making it difficult to debug and safely modify.

To address this, we undertook a major refactoring effort based on the principle of Separation of Concerns. We assigned each class its own file (module) and organized them into logical folders (packages) to create the current, clean code architecture:
core/: Contains foundational modules like constants.py and progress_manager.py that are used globally.
entities/: Contains all game object classes, such as player.py, alien.py, and bullet.py.
levels/: Contains the logic for each stage, including the crucial base_level.py.
ui/: Contains all classes related to the user interface, like button.py and level_selector.py.
This modular structure is now a cornerstone of the project, providing improved readability, easier maintenance, and a clear, logical separation that allows for efficient development and debugging.





Single Responsibility Principle (SRP)
The Single Responsibility Principle states that every module or class should have responsibility over a single part of the functionality provided by the software, and that responsibility should be entirely encapsulated by the class. A class should only have one reason to change.
In AstroCode, this principle is the bedrock of the entire architecture, evident from the project's file structure down to the individual classes:

Module-Level Responsibility: The project is divided into distinct packages, each with a single concern. The entities/ package is solely responsible for defining game objects, the ui/ package is responsible for user interface elements, and the core/progress_manager.py module is responsible only for saving and loading player data. This separation ensures that a change to the UI's appearance (e.g., in button.py) has no direct impact on the game's core logic (e.g., in player.py).

Class-Level Responsibility: We have kept this principle in mind when designing our game objects. Rather than a single, monolithic Game class, we have separated concerns into distinct classes:
The  class (entities/player.py) is responsible for managing the player's state, such as health, position, and bullets. It encapsulates all logic directly related to the player entity.

The  class (entities/alien.py) is responsible for all enemy logic, including its health, AI behavior (shooting timers, movement), and shield mechanics.

The  class (ui/level_selector.py) is concerned only with the presentation and logic of the level selection menu, including drawing locked/unlocked buttons and handling user clicks.

Through utilizing this principle, our code remains highly extensible and easy to debug. If a bug occurs with alien shields, we know the problem must be contained within alien.py, significantly reducing the scope of debugging.

Open-Closed Principle (OCP)
The Open-Closed Principle aims to make a code entity (class, module, function) open for extension, but closed for modification. This means it should be possible to add new functionality without changing existing, working code.

AstroCode's level structure is a prime example of this principle in action:
Level System: The game's levels are built on an inheritance hierarchy (Level -> Level2 -> Level3 -> Level4). The main.py game loop is designed to work with any object that inherits from the base Level class.
To add a Level5 to the game, we would simply create a new level5.py file, define a class Level5(Level4):, and implement its unique logic. We could then add it to the state machine in main.py. This requires zero modifications to the existing, tested code in level1.py, level2.py, level3.py, or level4.py.

This design contrasts sharply with using a large switch statement or if/elif chain in the main loop to handle level logic, which would require modification every time a new level is added, increasing the risk of introducing regressions.

By structuring our code this way, we can easily add new content and features in the future with a high degree of confidence that we will not break existing functionality.




Liskov's Substitution Principle (LSP)
This principle states that objects of a superclass should be replaceable with objects of its subclasses without breaking the application. In essence, a subclass must honor the "contract" of its parent class.This principle is fundamental to how our main game loop interacts with the various level classes.
Polymorphic Level Handling: In main.py, the core game loop does not care if it is running Level1, Level2, Level3, or Level4. It only knows it has a current_level object that is a subtype of Level. The loop confidently calls methods like current_level.update(dt, keys) and current_level.draw_game(...) because it is guaranteed by the inheritance structure that every level class will have these methods with the correct signatures.

Seamless Substitution: Even though the internal logic of Level4.update() (real-time action) is vastly different from Level2.update() (puzzle logic), they both fulfill the contract of the base Level class. This allows us to substitute any level into the main loop, and the program remains correct and functional, which is the essence of LSP. We are also able to use super().__init__() call to inherit and initialise the attribute of the parent base Level class, if we want to use the shared functionality of the base class.

Interface Segregation Principle (ISP)
This principle states that no client should be forced to depend on methods it does not use. It favors creating many smaller, specific interfaces over a single large, general-purpose one.
Focused Class APIs (Application Programming Interfaces): Our classes are designed to have small, focused sets of public methods. For example, the Button class has a very specific "interface": draw(), is_clicked(), and check_hover(). A developer using this class is not burdened with irrelevant methods related to other parts of the UI.

Separation of Concerns in Player Logic: In AstroCode, this is achieved through method separation. The logic for taking damage is contained within the Player and Alien classes and is not mixed with unrelated concerns like drawing or progress saving. A hypothetical NPC entity(if any) that cannot take damage would simply not have a take_damage method, adhering to the principle of not implementing unnecessary functionality.
This leads to a decoupled system where classes interact through minimal, well-defined APIs, making the code easier to understand and refactor.

Dependency Inversion Principle (DIP)
This principle states that high-level modules should not depend on low-level modules; both should depend on abstractions. Furthermore, abstractions should not depend on details; details should depend on abstractions.
The Level Abstraction: The main.py module is our highest-level module, responsible for orchestrating the game. It does not directly depend on the concrete, low-level implementations in level1.py, level2.py, etc. Instead, it depends on the abstraction of a Level, which is defined by the parent class in base_level.py.

How it Works: main.py knows that any Level object will have methods like update() and handle_events(). The specific, detailed implementations of these methods reside in the low-level modules (level1.py, level2.py). Therefore, both the high-level module (main.py) and the low-level modules (levelX.py) depend on the Level class "contract" or abstraction. This inverts the typical dependency flow and decouples our main game loop from the specifics of any single level.

This design makes our system incredibly flexible. We could create a completely new set of levels without ever touching the core logic in main.py, as long as they adhere to the Level abstraction.
Software Testing
Test Case Coverage
Our team used several core principles of test case design to ensure our test suite is both comprehensive and exhaustive:
Positive vs Negative Test Cases: We tested both valid user behavior and invalid interactions (e.g. player dragging code blocks outside of command area).


Black-Box Testing: Most tests simulate user interactions without looking at internal logic.


White-Box Testing: Used during development to verify internal state (e.g., ensuring bullets move in the correct direction).


Test Suite Overview
Designed to validate core game functions after any change. Structured by gameplay feature:
 Player Input & UI
S/N
Test Case
Classification
Expected Result
1
Command Block Interaction
Positive / Black-Box
Drag, Run, Reset block behavior works as expected

 Level 1: Sequencing
S/N
Test Case
Classification
Expected Result
1
Player Movement Control
Negative / Black-Box
WASD keys do nothing
2
Command Execution
Positive / Black-Box
Player moves + shoots in order
3
Target Damage
Positive / White-Box
Target takes damage

 Level 2: Conditional Logic
S/N
Test Case
Classification
Expected Result
1
Shooting mechanism for player
Positive / Black-Box
Player should shoot in the correct direction towards alien
2
Correct Hit
Positive / Black-Box
Deals damage to alien; player unharmed

Level 3: Iteration & Resource Management
S/N
Test Case
Classification
Expected Result
1
Shooting mechanism of alien bullets
Positive / Black-Box
Alien should shoot bullets in the correct direction towards the player, as well as in fixed intervals
2
Player taking damage
Negative / Black-Box
When hit by an alien bullet, the player should take damage 

Level 4: Real-Time Application (In the future, by Splashdown)
S/N
Test Case
Classification
Expected Result
1
Player Movement
Positive / Black-Box
WASD movement; editor disabled
2
Alien AI
Positive / Black-Box
Chasing + shooting behavior present
3
Real-Time Combat
Positive / Black-Box
Player shoots; type-matching logic still applies

Integration Testing
Validates inter-module interaction, especially inheritance from the base Level class.
Feature
Expected
Actual
Fixed
Level Inheritance
Distinct alien sprites in Level 3
Inherited mystery aliens from Level 2
(By Splashdown)
Command Execution System
Game runs while commands execute
Game froze during execution
(By Splashdown)
Bullet Damage
All bullets deal damage in Level 1
Damage wrongly checked bullet_type
(By Splashdown)



UI/UX Improvements 
Understanding that our target audience is children, a primary focus of our development was to create a User Interface (UI) and User Experience (UX) that is intuitive, forgiving, and visually clear. We iteratively refined the UI to remove ambiguity and reduce potential frustration, ensuring that the focus remains on learning and fun.

1. Redesigned Mission Briefings: From Pop-up to Overlay
The Problem: Our initial design used a large, static pop-up box in the middle of the screen to explain each level's objective. For a child, this was visually intrusive, blocked the game world, and felt like a disruptive wall of text. It was an interruption, not a guide.
The Improvement: We completely redesigned the briefings to be a single, timed line of text that appears cleanly at the top of the screen.
Timed Disappearance: The text automatically fades away after 8 seconds. This respects a child's attention span and allows them to get into the gameplay quickly without needing to manually close a window.
Clear, Concise Language: The instructions were rewritten to be simple and direct (e.g., "Use 'if' to scan alien type, then 'shoot' with the matching bullet!").

Benefit for Children: This new system provides just-in-time instruction without interrupting play. It gives a clear, simple goal at the start of the level and then gets out of the way, which is essential for keeping younger players engaged and not overwhelmed.

2. Immediate & Clear Action Feedback
The Problem: In Level 2, hitting an alien with the wrong bullet type would reduce the player's health, but there was no immediate visual cue to explain why they were being penalized. This could lead to confusion and frustration, as the child might not understand the connection between their action and the negative consequence.
The Improvement: We implemented the "INCORRECT HIT" text pop-up.
Instant Feedback: This white, bold text appears directly above the player's character for 1.5 seconds at the exact moment the incorrect collision happens.
Contextual Link: It creates a direct, undeniable link between the action (firing the wrong bullet) and the consequence (losing health).

Benefit for Children: This provides cause-and-effect learning. Children learn best through clear and immediate feedback. The pop-up instantly tells them "what you just did was wrong," which is a far more effective teaching tool than simply watching a health bar go down without explanation.


3. Explicit Resource Counters and Limits
The Problem: The core challenge of Level 3 is the limit on "Run" attempts. In early versions, this limit was not displayed on screen. A child playing the level would fail without ever knowing the rule they were breaking, leading to a feeling of unfairness.
The Improvement: We added a clear, persistent UI element at the top of the screen that explicitly states: "Run Attempts Remaining: 5".
Visual Clarity: The counter is always visible and updates in real-time.
Defines the Puzzle: It immediately frames the level as a resource management puzzle, rather than a simple combat challenge.

Benefit for Children: This makes the rules of the game explicit and fair. It empowers the child by giving them all the information they need to succeed. Instead of being confused about why they failed, they can strategize and understand that they need to find a more "powerful" command (the for loop) to solve the puzzle within the given limits.

4. Puzzle Integrity and a Frustration-Free Experience
The Problem: In Level 2, early versions had loopholes where a clever child could solve the puzzle without using the if command by looking at the colored dots on the minimap or the off-screen indicators. While this shows intelligence, it allows them to bypass the intended educational objective.
The Improvement: We intentionally neutralized all visual clues in Level 2.
The minimap dots and directional indicators are now a neutral color.
The alien sprites are identical.

Benefit for Children: This creates a focused learning environment. By removing distracting or misleading information, we guide the child directly to the intended solution: using the if block as a scanner. This prevents them from getting stuck on incorrect strategies and ensures they engage with the core concept the level is designed to teach, leading to a more rewarding "aha!" moment when they solve it correctly.

