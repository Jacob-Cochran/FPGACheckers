import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from enum import Enum


class NotOwner(Exception):
    pass


class NotEmpty(Exception):
    pass


class IllegalArgument(Exception):
    pass


class player(Enum):
    blue = 0
    red = 1
    neither = 2


class tile(Enum):
    n = 0
    b = 1
    r = 2
    bk = 3
    rk = 4


def arePositionsEqual(row1, col1 , row2, col2):
    return (row1 == row2) and (col1 == col2)


def getPlayerFromPiece(thePiece):
    if thePiece in [tile.r, tile.rk]:
        return player.red
    elif thePiece in [tile.b, tile.bk]:
        return player.blue
    else:
        return player.neither


def getPieceFromGridPosition(grid, row, col):
    t = grid[row][col]
    if t == 0:
        return tile.n
    elif t == 1:
        return tile.b
    elif t == 2:
        return tile.r
    elif t == 3:
        return tile.bk
    elif t == 4:
        return tile.rk


class Model():
    def __init__(self):
        self.grid = []
        self.whosTurn = player.blue
        self.resetGrid()

    def getTurn(self):
        return self.whosTurn

    def getGrid(self):
        return self.grid

    def resetGrid(self):
        self.grid = [
            [0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [2, 0, 2, 0, 2, 0, 2, 0],
            [0, 2, 0, 2, 0, 2, 0, 2],
            [2, 0, 2, 0, 2, 0, 2, 0]
        ]

    def setGridPosition(self, row, col, new):
        self.grid[row][col] = new.value

    def endTurn(self):
        """
        Ends the turn for the current player and updates the player enum stored in the model.
        :return: None
        """
        if self.whosTurn == player.blue:
            self.whosTurn = player.red
        else:
            self.whosTurn = player.blue

    def takeMove(self, row1, col1, row2, col2):
        """
        Given a start and stop position changes the model's board state.
        Does not allow you to move another players piece. Only allows
        a player to move to a non-occupied tile (Does not handle captures).
        :return: Nothing, throws exceptions on invalid moves.
        """
        ## TODO: THIS DOES NOT ACCOUNT FOR JUMPS AT ALL!!!!
        startPiece = getPieceFromGridPosition(self.grid, row1, col1)
        endPiece = getPieceFromGridPosition(self.grid, row2, col2)
        print("CALLING TAKE MOVE", startPiece, getPlayerFromPiece(startPiece))
        if getPlayerFromPiece(startPiece) != self.whosTurn:
            raise NotOwner("Player cannot move that piece!")
        elif endPiece != tile.n:  ## TODO: Remove this after OVERLAY BECAUSE IT STEALS HIS THUNDER
            raise NotEmpty("Cannot move piece to a non-empty tile")
        else:
            self.setGridPosition(row1, col1, tile.n)
            self.setGridPosition(row2, col2, startPiece)


    def printBoard(self):
        outstring = ""
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                piece = getPieceFromGridPosition(self.grid, row, col)
                outstring += format(piece) + " "
            outstring += "\n"
        print(outstring)


class View(ttk.Frame):
    def __init__(self, parent, bp, rp, bk, rk, w, b, startingGrid):
        super().__init__(parent)
        self.blue_piece = bp
        self.red_piece = rp
        self.blue_king = bk
        self.red_king = rk
        self.black = b
        self.white = w
        self.parent = parent
        self.controller = None
        self.drawFromGrid(startingGrid)

    def setController(self, controller):
        self.controller = controller


    def getLabelFromPieceAndLocation(self, frame, curPiece, row, col):
        """
        Given a piece enum, returns a new label object that will be put into the grid
        :param frame: The frame which will be the parent of new label
        :param curPiece: A piece enum
        :return: New label object or exception
        """
        if curPiece == tile.n:
            if (row + col) % 2 == 0:
                label = tk.Label(master=frame, width=100, height=100, image=self.white)
            else:
                label = tk.Label(master=frame, width=100, height=100, image=self.black)
        elif curPiece == tile.b:
            label = tk.Label(master=frame, width=100, height=100, image=self.blue_piece)
        elif curPiece == tile.bk:
            label = tk.Label(master=frame, width=100, height=100, image=self.blue_king)
        elif curPiece == tile.r:
            label = tk.Label(master=frame, width=100, height=100, image=self.red_piece)
        elif curPiece == tile.rk:
            label = tk.Label(master=frame, width=100, height=100, image=self.red_king)
        else:
            raise IllegalArgument("Invalid arguments specified!")
        if curPiece != tile.n:
            label.bind("<Button-1>", lambda e: self.controller.clickedPlayerTile(row, col, curPiece))
        else:
            label.bind("<Button-1>", lambda e: self.controller.clickedNonPlayerTile(row, col, curPiece))
        return label

    def drawFromGrid(self, grid):
        for row in range(len(grid)):
            for col in range(len(grid)):
                frame = tk.Frame(
                    master=self.parent,
                    relief="raised",
                    borderwidth=1
                )
                frame.grid(row=row, column=col, padx=0, pady=0)
                currentPiece = getPieceFromGridPosition(grid, row, col)
                label = self.getLabelFromPieceAndLocation(frame, currentPiece, row, col)
                label.pack(padx=0, pady=0)


class Controller:
    def __init__(self, root, model, view):
        self.root = root
        self.model = model
        self.view = view
        self.lastClicked = None ## TODO: RESET THIS WHEN MODEL CHANGES PLAYERS

    def pressedEnter(self, event):
        if event.keysym == "Return":
            print("Swapping turns")
            self.model.endTurn()
        #self.root.title("{}: {}".format(str(event.type), event.keysym))
        # self.model.setTurn()

    def clickedPlayerTile(self, row, col, curPiece):
        """
        Can never move from a non-player tile to a player tile, so this function just sets lastClicked
        iff the current player is the one who is clicking
        :param row: row of piece clicked
        :param col: column of piece clicked
        :param curPiece: piece clicked
        :return: Nothing, simply sets lastClicked attribute
        """
        print("PLAYER_TILE: ", row, col, " CLICKED")
        pieceAt = getPieceFromGridPosition(self.model.getGrid(), row, col)
        playerAt = getPlayerFromPiece(pieceAt)
        currentTurn = self.model.getTurn()

        if self.lastClicked is None and currentTurn == playerAt:
            self.lastClicked = [row, col]
        elif currentTurn != playerAt:
            if self.lastClicked is None:
                raise NotOwner("Can't move other players piece!")
            else:
                self.lastClicked = None
                raise NotEmpty("Can't move to occupied tile!")
        self.lastClicked = [row, col]


    def clickedNonPlayerTile(self, row, col, curPiece):
        """
        Attempts to make a move if the last tile clicked was a player tile of the correct player
         :param row: row of piece clicked
        :param col: column of piece clicked
        :param curPiece: piece clicked
        :return: Nothing, but resets lastClicked and attempts to modify view and model based on move
        """
        if self.lastClicked is not None:
            lastRow, lastCol = self.lastClicked[0], self.lastClicked[1]
            if not arePositionsEqual(lastRow, lastCol, row, col):
                try:
                    self.model.takeMove(lastRow, lastCol, row, col)
                    self.lastClicked = None
                    newGrid = self.model.getGrid()
                    self.view.drawFromGrid(newGrid)
                except NotOwner:
                    print("Can't move other players piece!")
                except NotEmpty:
                    print("Can't move to not empty tile!")
        print("\n"*2)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("850x850")
        self.title("FPGA CHECKERS")
        white = ImageTk.PhotoImage(file="assets/white.png")
        black = ImageTk.PhotoImage(file="assets/black.png")
        blue = ImageTk.PhotoImage(file="assets/blue.png")
        red = ImageTk.PhotoImage(file="assets/red.png")
        blue_king = ImageTk.PhotoImage(file="assets/blue_king.png")
        red_king = ImageTk.PhotoImage(file="assets/red_king.png")

        model = Model()

        view = View(self, blue, red, blue_king, red_king, white, black, model.getGrid())

        controller = Controller(self, model, view)
        view.setController(controller)

        event_sequence = '<KeyPress>'
        self.bind(event_sequence, controller.pressedEnter)
        self.bind("<KeyRelease>", lambda e: controller.pressedEnter)

        # view.drawFromGrid(model.getGrid()) <-- This is how to update the view based on the grid


if __name__ == '__main__':
    app = App()
    app.mainloop()
