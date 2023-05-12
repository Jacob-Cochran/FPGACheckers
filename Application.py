import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from enum import Enum
import socketCommunication


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


class GameState(Enum):
    blueWin = 0
    redWin = 1
    isPlaying = 2


class tile(Enum):
    n = 0
    b = 1
    r = 2
    bk = 3
    rk = 4


def arePositionsEqual(row1, col1, row2, col2):
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
        self.gameState = GameState.isPlaying
        self.playerAlreadyMoved = False  # False if hasn't moved yet, true if already moved but didnt take a piece,
        self.playerLastMove = None  # and tuple if moved and took a piece
        self.wasJump = False
        self.resetGrid()

    def getTurn(self):
        return self.whosTurn

    def getGrid(self):
        return self.grid

    def resetGrid(self):
        # self.grid = [
        #     [0, 1, 0, 1, 0, 1, 0, 1],
        #     [1, 0, 1, 0, 1, 0, 1, 0],
        #     [0, 1, 0, 1, 0, 1, 0, 1],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [2, 0, 2, 0, 2, 0, 2, 0],
        #     [0, 2, 0, 2, 0, 2, 0, 2],
        #     [2, 0, 2, 0, 2, 0, 2, 0]
        # ]
        self.grid = [
            [0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 3, 0],
            [0, 0, 0, 0, 0, 3, 0, 0],
            [0, 0, 0, 0, 1, 0, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

    def setGridPosition(self, row, col, new):
        self.grid[row][col] = new.value

    def endTurn(self):
        """
        Ends the turn for the current player and updates the player enum stored in the model.
        :return: None
        """
        self.playerLastMove = None
        self.playerAlreadyMoved = False
        self.wasJump = False
        if self.whosTurn == player.blue:
            self.whosTurn = player.red
        else:
            self.whosTurn = player.blue

    def gridAndMoveToString(self, startLocation, endLocation):
        outstring = ""
        outstring += str(startLocation) + "\n"
        outstring += str(endLocation) + "\n"
        for row in range(8):
            rowString = ""
            for col in range(8):
                rowString += str(self.grid[row][col]) + ","
            outstring += rowString
        return outstring[0:-1]

    def setGridFromOneDimensionArray(self, oneDimArray):
        total = []
        for row in range(8):
            newRow = []
            for col in range(8):
                newRow.append(oneDimArray[row * 8 + col])
            total.append(newRow)
        self.grid = total

    def takeMove(self, row1, col1, row2, col2):
        """
        Given a start and stop position changes the model's board state.
        Does not allow you to move another players piece. Only allows
        a player to move to a non-occupied tile (Does not handle captures).
        :return: Nothing, throws exceptions on invalid moves.
        """
        startPiece = getPieceFromGridPosition(self.grid, row1, col1)
        endPiece = getPieceFromGridPosition(self.grid, row2, col2)
        startLocation = row1 * 8 + col1
        endLocation = row2 * 8 + col2

        print("CALLING TAKE MOVE", startPiece, getPlayerFromPiece(startPiece))
        if getPlayerFromPiece(startPiece) != self.whosTurn:
            raise NotOwner("Player cannot move that piece!")

        # Since the player owns the piece call the model
        communicationResult = socketCommunication.sendAGrid(self.gridAndMoveToString(startLocation, endLocation))

        ## JUST FOR MOCKING ##
        # with open("mockGrid.txt", "r") as f:
        #     code = f.readline().strip()
        #     gridMock = ""
        #     for line in f.readlines():
        #         gridMock += line.strip().replace(", ", ",")
        # communicationResult = code + "\n" + gridMock
        ## END MOCKING ##

        print(communicationResult)
        resultSplit = communicationResult.split("\n")
        conditionCode = resultSplit[0]
        gridResult = resultSplit[1].split(",")
        gridResult = [int(i) for i in gridResult]

        print("Player Last Move:", self.playerLastMove, " | Current Move:", (row1, col1), "| Condition Code:", conditionCode)

        if conditionCode == "640":
            raise IllegalArgument("Invalid Move")
        elif self.playerAlreadyMoved:  # Checks if took a move last turn
            if self.wasJump:
                if self.playerLastMove is not None:
                    if self.playerLastMove == (row1, col1) and conditionCode[0:2] != "64":
                        # Verifies they are moving the same piece they just used to jump with
                        self.playerLastMove = (row2, col2)
                        self.setGridFromOneDimensionArray(gridResult)
                        # Player is at least allowed to move so set grid
                        self.playerAlreadyMoved = (row2, col2)
                    else:
                        raise IllegalArgument("Must move the piece just used to jump")
                else:
                    raise IllegalArgument("Last Move is None")
            else:
                # If they did not just take a piece then they cannot have a second turn
                raise IllegalArgument("Cannot move when did not previously take a piece")
        else:
            # First time moving for player
            self.playerAlreadyMoved = True
            self.playerLastMove = (row2, col2)
            self.setGridFromOneDimensionArray(gridResult)
        if conditionCode[0:2] != "64":
            self.wasJump = True
        if conditionCode[2] == "2":
            self.gameState = GameState.blueWin
        elif conditionCode[2] == "3":
            self.gameState = GameState.redWin
        # self.printBoard()

    def isLastJump(self):
        return self.wasJump

    def printBoard(self):
        outstring = ""
        for row in range(len(self.grid)):
            for col in range(len(self.grid)):
                piece = getPieceFromGridPosition(self.grid, row, col)
                outstring += format(piece) + " "
            outstring += "\n"
        print(outstring)


class View(ttk.Frame):
    def __init__(self, parent, bp, rp, bk, rk, w, b, b_sel, r_sel, bk_sel, rk_sel, startingGrid):
        super().__init__(parent)
        self.blue_piece = bp
        self.red_piece = rp
        self.blue_king = bk
        self.red_king = rk
        self.black = b
        self.white = w
        self.blue_sel = b_sel
        self.red_sel = r_sel
        self.blue_king_sel = bk_sel
        self.red_king_sel = rk_sel
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
                label = tk.Label(master=frame, width=75, height=75, image=self.white)
            else:
                label = tk.Label(master=frame, width=75, height=75, image=self.black)
        elif curPiece == tile.b:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_piece)
        elif curPiece == tile.bk:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_king)
        elif curPiece == tile.r:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_piece)
        elif curPiece == tile.rk:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_king)
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

    def getHighlightedOfPiece(self, frame, curPiece, row, col):
        """
        Given a current piece, returns the highlighted asset for said piece
        :return: A label, the highlighted version of a piece
        """
        if curPiece == tile.b:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_sel)
        elif curPiece == tile.r:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_sel)
        elif curPiece == tile.bk:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_king_sel)
        elif curPiece == tile.rk:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_king_sel)
        else:
            raise IllegalArgument("Invalid highlight location")
        label.bind("<Button-1>", lambda e: self.controller.clickedPlayerTile(row, col, curPiece))
        return label

    def getNonHighlightOfPiece(self, frame, curPiece, row, col):
        """
        Given a current piece, returns the NON-highlighted asset for said piece
        :return: A label, the NON-highlighted version of a piece
        """
        if curPiece == tile.b:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_piece)
        elif curPiece == tile.r:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_piece)
        elif curPiece == tile.bk:
            label = tk.Label(master=frame, width=75, height=75, image=self.blue_king)
        elif curPiece == tile.rk:
            label = tk.Label(master=frame, width=75, height=75, image=self.red_king)
        else:
            raise IllegalArgument("Invalid highlight location")
        label.bind("<Button-1>", lambda e: self.controller.clickedPlayerTile(row, col, curPiece))
        return label

    def highlightPieceLocation(self, grid, row, col):
        """
        Used by controller to set a piece in the view to be its highlighted asset.
        """
        frame = tk.Frame(
            master=self.parent,
            relief="raised",
            borderwidth=1
        )
        frame.grid(row=row, column=col, padx=0, pady=0)
        currentPiece = getPieceFromGridPosition(grid, row, col)
        label = self.getHighlightedOfPiece(frame, currentPiece, row, col)
        label.pack(padx=0, pady=0)

    def removeHighlightAtPieceLocation(self, grid, row, col):
        """
        Used by controller to set a piece in the view to be its NON-highlighted asset.
        """
        frame = tk.Frame(
            master=self.parent,
            relief="raised",
            borderwidth=1
        )
        frame.grid(row=row, column=col, padx=0, pady=0)
        currentPiece = getPieceFromGridPosition(grid, row, col)
        label = self.getNonHighlightOfPiece(frame, currentPiece, row, col)
        label.pack(padx=0, pady=0)


class Controller:
    def __init__(self, root, model, view):
        self.root = root
        self.model = model
        self.view = view
        self.lastClicked = None

    def verifyGameNotOver(self):
        """
        Raises an error if the game is over, otherwise does nothing. Used to prevent moves after the game
        :return: None
        """
        if self.model.gameState != GameState.isPlaying:
            raise IllegalArgument("Cannot move when the game has ended!")

    def swapTurns(self):
        self.verifyGameNotOver()
        print("Swapping turns")
        if self.lastClicked is not None:
            newGrid = self.model.getGrid()
            lastRow = self.lastClicked[0]
            lastCol = self.lastClicked[1]
            self.view.removeHighlightAtPieceLocation(newGrid, lastRow, lastCol)
            self.lastClicked = None
        self.model.endTurn()
        currentTurn = self.model.getTurn()
        if currentTurn == player.blue:
            self.root.title("FPGA CHECKERS:  Blue's Move")
        elif currentTurn == player.red:
            self.root.title("FPGA CHECKERS:  Red's Move")


    def pressedEnter(self, event):
        self.verifyGameNotOver()
        if event.keysym == "Return":
            self.swapTurns()

    def clickedPlayerTile(self, row, col, curPiece):
        """
        Can never move from a non-player tile to a player tile, so this function just sets lastClicked
        iff the current player is the one who is clicking
        :param row: row of piece clicked
        :param col: column of piece clicked
        :param curPiece: piece clicked
        :return: Nothing, simply sets lastClicked attribute
        """
        self.verifyGameNotOver()
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
                newGrid = self.model.getGrid()
                lastRow = self.lastClicked[0]
                lastCol = self.lastClicked[1]
                self.view.removeHighlightAtPieceLocation(newGrid, lastRow, lastCol)
                self.lastClicked = None
                raise NotEmpty("Can't move to occupied tile!")
        newGrid = self.model.getGrid()
        if self.lastClicked is not None:
            lastRow = self.lastClicked[0]
            lastCol = self.lastClicked[1]
            self.view.removeHighlightAtPieceLocation(newGrid, lastRow, lastCol)
        self.view.highlightPieceLocation(newGrid, row, col)
        self.lastClicked = [row, col]

    def clickedNonPlayerTile(self, row, col, curPiece):
        """
        Attempts to make a move if the last tile clicked was a player tile of the correct player
        :param row: row of piece clicked
        :param col: column of piece clicked
        :param curPiece: piece clicked
        :return: Nothing, but resets lastClicked and attempts to modify view and model based on move
        """
        self.verifyGameNotOver()
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
        print("\n" * 2)

        # After validating a move check the win-conditions
        if self.model.gameState == GameState.redWin:
            self.root.title("FPGA CHECKERS:  Red Wins!")
        elif self.model.gameState == GameState.blueWin:
            self.root.title("FPGA CHECKERS:  Blue Wins!")

        # Finally, if the move was not a jump then automatically end the users turn
        if not self.model.isLastJump():
            self.swapTurns()
        else:
            self.lastClicked = [row, col]
            newGrid = self.model.getGrid()
            self.view.highlightPieceLocation(newGrid, row, col)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("650x650")
        self.title("FPGA CHECKERS:  Blue's Move")

        whiteIMG = Image.open("assets/white.png").resize((75, 75))
        blackIMG = Image.open("assets/black.png").resize((75, 75))
        blueIMG = Image.open("assets/blue.png").resize((75, 75))
        redIMG = Image.open("assets/red.png").resize((75, 75))
        blue_kingIMG = Image.open("assets/blue_king.png").resize((75, 75))
        red_kingIMG = Image.open("assets/red_king.png").resize((75, 75))
        blueSelIMG = Image.open("assets/blue_select.png").resize((75, 75))
        redSelIMG = Image.open("assets/red_select.png").resize((75, 75))
        blue_kingSelIMG = Image.open("assets/blue_king_select.png").resize((75, 75))
        red_kingSelIMG = Image.open("assets/red_king_select.png").resize((75, 75))

        white = ImageTk.PhotoImage(whiteIMG)
        black = ImageTk.PhotoImage(blackIMG)
        blue = ImageTk.PhotoImage(blueIMG)
        red = ImageTk.PhotoImage(redIMG)
        blue_king = ImageTk.PhotoImage(blue_kingIMG)
        red_king = ImageTk.PhotoImage(red_kingIMG)
        blueSelect = ImageTk.PhotoImage(blueSelIMG)
        redSelect = ImageTk.PhotoImage(redSelIMG)
        blueKingSelect = ImageTk.PhotoImage(blue_kingSelIMG)
        redKingSelect = ImageTk.PhotoImage(red_kingSelIMG)

        model = Model()

        view = View(self, blue, red, blue_king, red_king, white, black, blueSelect, redSelect, blueKingSelect, redKingSelect, model.getGrid())

        controller = Controller(self, model, view)
        view.setController(controller)

        event_sequence = '<KeyPress>'
        self.bind(event_sequence, controller.pressedEnter)
        self.bind("<KeyRelease>", lambda e: controller.pressedEnter)


if __name__ == '__main__':
    app = App()
    app.mainloop()
