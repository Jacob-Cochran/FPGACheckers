
# FPGA Checkers Application

### About
This project is the classic game 'Checkers' also called 'Draughts'. This project implements a slim, but clean GUI interface to play the classic two-player game. The purpose of the project is a proof-of-concept using FPGA-fabric to run the core business logic of checkers in hardware. We also take advantage of computer networking by running this FPGA-fabric as a basic server, which the client GUI communicates with, thereby decoupling the FPGA-interface from the users GUI. Therefore, the second proof of concept this project strives to demonstrate is running back-end business logic as a hardware module, rather than software.

This project is a Checkers Game implemented using the Tkinter GUI library (with PIL as a dependency). The Application works using a Client-Server Architecture implemented via Socket Communication. The projec 

The purpose of this project is to develop a lightweight GUI with very minimal business logic in its Model class. 

### Future Features
* This project is built on a relatively Modular MVC framework, which black-boxes business logic behind socket communication. This project could be changed into a Player-to-Player version using further computer networking quite easily. 

* Additionall, we considered implementing an AI-opponent using a shallow Min-max style searching algorithm. This could be done; however, it would require moderate changes to the controller architecture as moves are mostly handled as on-click events.
