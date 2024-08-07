import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the count of mines is equal to the number of cells, all cells are mines
        if len(self.cells) == self.count:
            return self.cells
        else: 
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # if no mines, all cells are safe
        if self.count == 0:
            return self.cells
        else: 
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # remove the mine from the cell list and discount it from the count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        else:
            return 

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # remove the mine from the cell list
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            return 


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
    
    def valid_neighbors(self, cell):
        """
        Auxiliar: returns all neighbors cells that have not been seen yet. 
        """
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # ignore the cell itself 
                if (i, j) == cell:
                    continue
                
                # add all neighbors 
                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) not in self.moves_made:
                        neighbors.add((i, j))

        return neighbors
    
    def mark_and_update_knowledge(self):
        """
        Auxiliar: marks all known cell as safe or mine
        """
        for sentence in self.knowledge:
            # marks as safes
            safe_cells = sentence.known_safes().copy() | self.safes
            if safe_cells:
                for safe_cell in safe_cells:
                    self.mark_safe(safe_cell)

            # marks as mines
            mine_cells = sentence.known_mines().copy()
            if mine_cells:
                for mine_cell in mine_cells:
                    self.mark_mine(mine_cell)

    def remove_knows_mark_append(self, cells, count):
        """
        Auxiliar: removes known cells, marks and appends to knowledge
        """
        # checks for known safe cells
        cells = cells - self.safes

        # checks for known mines in cells
        count_mines = len(cells & self.mines)
        if count_mines:
            count -= count_mines
        cells = cells - self.mines

        if cells:
            sentence = Sentence(cells, count)

            if sentence not in self.knowledge:
                self.knowledge.append(sentence)
                self.mark_and_update_knowledge()

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the cell as a move that has been made
        self.moves_made.add(cell)
    
        # mark the cell as safe
        self.mark_safe(cell)       

        # add a new sentence to the AI's knowledge base
        # based on the value of `cell` and `count`
        neighbors = self.valid_neighbors(cell)

        self.remove_knows_mark_append(neighbors, count)

        # add any new sentences to the AI's knowledge base
        # if they can be inferred from existing knowledge
        for i in range(len(self.knowledge)):
            for j in range(len(self.knowledge)):
                if i == j:
                    continue

                sentence_i = self.knowledge[i]
                sentence_j = self.knowledge[j]

                # if sentence is a subset of other, append the difference
                if sentence_i.cells <= sentence_j.cells and len(sentence_i.cells) > 0:
                    new_cells = sentence_j.cells - sentence_i.cells
                    if new_cells:
                        new_count = sentence_j.count - sentence_i.count

                        sentence = Sentence(new_cells, new_count)
                        if sentence not in self.knowledge:
                            self.knowledge.append(sentence)

        # update knowledge marking cells
        self.mark_and_update_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        left_moves = set()
        for i in range(self.width):
            for j in range(self.height):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    left_moves.add((i, j))
        if left_moves:
            return left_moves.pop()