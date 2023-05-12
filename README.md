
# FPGA Checkers Application

### Purpose
This project is the classic game 'Checkers' also called 'Draughts'. This project implements a slim, but clean GUI interface to play the classic two-player game. The purpose of the project is a proof-of-concept using FPGA-fabric to run the core business logic of checkers in hardware. We also take advantage of computer networking by running this FPGA-fabric as a basic server, which the client GUI communicates with, thereby decoupling the FPGA-interface from the users. This demonstrates our second proof of concept, which is running back-end business logic as a hardware module instead of software.

### About

This project is a Checkers Game implemented using the Tkinter GUI library (with PIL as a dependency). The Application works using a Client-Server Architecture implemented via Socket Communication. There are two separate components to this package: (1) A Server which runs on a PynQ FPGA, and (2) A lightweight GUI that runs on the clients local machine.

 Markup : 1. Server: The code-base intended for the Server, running on a PynQ FPGA using a custom hardware overlay.
  1. Server.py: This is the core-script for the server. It instantiates a custom IP Overlay using a hardware bitstream, representing the move validation and state- checking logic of checkers. The Server file also runs the TCP Socket Server. It first creates a new TCP Socket Host, and listens indefinitely for incoming packets. It then interprets these packets as a chess move, as well as the current checker-board. The server then validates the move with a condition code, and returns the new board state.
3. 

### Future Features
* This project is built on a relatively Modular MVC framework, which black-boxes business logic behind socket communication. This project could be changed into a Player-to-Player version using further computer networking quite easily. 

* Additionall, we considered implementing an AI-opponent using a shallow Min-max style searching algorithm. This could be done; however, it would require moderate changes to the controller architecture as moves are mostly handled as on-click events.
