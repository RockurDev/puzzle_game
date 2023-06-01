import os
import random
import sys
from typing import Generic, Iterable, TypeVar
from PyQt6.QtCore import QSize, QTime, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget,
    QComboBox
)

# Define a type variable T for the Board class
T = TypeVar("T")

# Define a class to represent the game board
class Board(Generic[T]):
    def __init__(self, blank_item: T, values_in_correct_order: list[T]) -> None:
        # `values_in_correct_order` is a list with items
        # of the same time, for example, QPixmap.
        # Create a list of values on the board with the blank item at the end
        self.values = values_in_correct_order.copy()
        self.values.append(blank_item)
        # Create a shuffled list of positions for the values on the board
        self.positions = list(range(16))
        random.shuffle(self.positions)

    def render(self) -> Iterable[T]:
        # return QPixmap object from shuffled positions list
        # Yield the value at each position in the shuffled positions list
        for pos in self.positions:
            yield self.values[pos]

    def check_win(self) -> bool:
        return self.positions == list(range(16))

    def _swap_tiles(self, first_pos: int, second_pos: int) -> None:
        # Swap the positions of two tiles on the board
        first_tile = self.positions[first_pos]
        second_tile = self.positions[second_pos]
        self.positions[first_pos] = second_tile
        self.positions[second_pos] = first_tile

    @staticmethod
    def _tile_is_near(first_pos: int, second_pos: int) -> bool:
        # Check if two tiles are next to each other on the board
        first_row, first_column = divmod(first_pos, 4)
        second_row, second_column = divmod(second_pos, 4)

        if first_column == second_column and (
            # lower or upper
            first_row == second_row - 1
            or first_row == second_row + 1
        ):
            return True

        if first_row == second_row and (
            # to the left or to the right
            first_column == second_column - 1
            or first_column == second_column + 1
        ):
            return True

        return False

    def move_tile(self, pos: int) -> bool:
        # Move a tile on the board to the empty space if it is next to it
        blank_item_pos = self.positions.index(15)
        if self._tile_is_near(blank_item_pos, pos):
            self._swap_tiles(blank_item_pos, pos)
            return True
        return False


# Define a class for the main game window
class MainWindow(QMainWindow):
    def __init__(self):  # The first image should be the blank one.
        super().__init__()

        # Set the window title, size, and layout
        self.setWindowTitle("Puzzle Game")
        self.setGeometry(100, 100, 500, 500)
        self.setFixedSize(470, 550)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)

        # Create a list of buttons for the tiles on the board
        self.tiles: list[QPushButton] = []
        for row in range(4):
            for column in range(4):
                btn = QPushButton()
                btn.setFixedSize(100, 110)
                self.tiles.append(btn)
                grid_layout.addWidget(btn, row, column)

        # Create a restart button and labels for moves and time
        restart_button = QPushButton("Restart")
        restart_button.clicked.connect(self.restart_game)
        grid_layout.addWidget(restart_button, 4, 0)

        self.moves_label = QLabel("Moves: 0")
        grid_layout.addWidget(self.moves_label, 4, 1)

        self.time_label = QLabel(self)
        self.time_label.setFont(QFont("Courier New"))
        self.time_label.setText("00:00:00")
        self.time_label.setGeometry(10, 10, 180, 30)
        grid_layout.addWidget(self.time_label, 4, 2)
        self.timer = QTimer()

        # Create a combo menu for selecting the image for the game
        self.combo_menu = QComboBox()
        self.combo_menu.addItems(['AirBallon', 'Amsterdam', 'Flower', 'Moscow', 'MulledWine', 'Panda', 'Toucan', 'Witcher'])
        grid_layout.addWidget(self.combo_menu, 4, 3)

    def init_timer(self):
        # Initialize a timer that updates the time label every second
        time = QTime(0, 0, 0)

        def update_time():
            nonlocal time
            time = time.addSecs(1)
            self.time_label.setText(time.toString("hh:mm:ss"))

        self.timer.timeout.connect(update_time)
        self.timer.start(1000)

    # Set the icons of the tiles to the current state of the board
    def render_icons(self):
        # self.tiles is just QPushButton list
        # self.board.render() return position from shuffled positions list
        for image_widget, tile in zip(self.board.render(), self.tiles):
            # Every tile get its own QIcon with right image_widget
            tile.setIcon(QIcon(image_widget))

    def set_picture(self):
        # Set the images for the game based on the current selection in the combo menu
        picture = self.combo_menu.currentText()
        folder = "./Source/Images/" + picture

        images = [
            os.path.join(folder, f) for f in os.listdir(folder) if f.startswith("ImageP")
        ]
        images.sort(key=lambda x: int(x.split('ImageP')[1].split(".")[0]))

        # Create a list of QPixmap images for the tiles on the board
        self.image_widgets = [QPixmap(image) for image in images]

    def init_tiles(self):
        # Initialize the tiles on the board with the current images and connect them to the move_tile method
        self.set_picture()

        # image_widgets is list with sorted QPixmap images
        self.board = Board(self.image_widgets[0], self.image_widgets[1:])
        self.render_icons()

        for i, tile in enumerate(self.tiles):
            tile.setIconSize(QSize(110, 110))
            tile.clicked.connect(lambda _, i=i: self.move_tile(i))
            tile.setEnabled(True)

    def update_moves_label(self):
        # Update the moves label with the current number of moves
        self.moves_label.setText(f"Moves: {self.moves}")

    def restart_game(self):
        # Reset the timer, initialize the tiles, and set the moves counter to zero
        self.init_timer()
        self.init_tiles()
        self.moves = 0
        self.update_moves_label()

    def move_tile(self, index: int):
        # Move a tile on the board when it is clicked and update the moves counter and win state
        moved = self.board.move_tile(index)
        if not moved:
            return

        self.render_icons()

        self.moves += 1
        self.update_moves_label()

        if not self.board.check_win():
            return

        self.moves_label.setText(f"You won in {self.moves} moves!")
        for tile in self.tiles:
            tile.setEnabled(False)


# Define the main function to create and run the game window
def main():
    # The style sheet is loaded
    with open('./Source/Style/styles.qss', 'r') as f:
        style = f.read()
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    game = MainWindow()
    game.show()
    return app.exec()

# Run the main function when this script is called
if __name__ == "__main__":
    raise SystemExit(main())