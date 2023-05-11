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
)

T = TypeVar("T")


class Board(Generic[T]):
    def __init__(self, values_in_correct_order: list[T], blank_item: T) -> None:
        # `values_in_correct_order` is a list with items
        # of the same time, for example, QPixmap.
        self.values = values_in_correct_order.copy()
        self.values.append(blank_item)
        self.positions = list(range(16))
        random.shuffle(self.positions)

    def render(self) -> Iterable[T]:
        for pos in self.positions:
            yield self.values[pos]

    def check_win(self) -> bool:
        return self.positions == list(range(16))

    def _swap_tiles(self, first_pos: int, second_pos: int) -> None:
        first_tile = self.positions[first_pos]
        second_tile = self.positions[second_pos]
        self.positions[first_pos] = second_tile
        self.positions[second_pos] = first_tile

    @staticmethod
    def _tile_is_near(first_pos: int, second_pos: int) -> bool:
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
        blank_item_pos = self.positions.index(15)
        if self._tile_is_near(blank_item_pos, pos):
            self._swap_tiles(blank_item_pos, pos)
            return True
        return False


class MainWindow(QMainWindow):
    def __init__(self, images: list[str]):  # The first image should be the blank one.
        super().__init__()

        self.setWindowTitle("Puzzle Game")
        self.setGeometry(100, 100, 500, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)

        self.tiles: list[QPushButton] = []
        for row in range(4):
            for column in range(4):
                btn = QPushButton()
                btn.setFixedSize(100, 110)
                self.tiles.append(btn)
                grid_layout.addWidget(btn, row, column)

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

        self.image_widgets = [QPixmap(image) for image in images]

    def init_timer(self):
        time = QTime(0, 0, 0)

        def update_time():
            nonlocal time
            time = time.addSecs(1)
            self.time_label.setText(time.toString("hh:mm:ss"))

        self.timer.timeout.connect(update_time)
        self.timer.start(1000)

    def render_icons(self):
        for image_widget, tile in zip(self.board.render(), self.tiles):
            tile.setIcon(QIcon(image_widget))

    def init_tiles(self):
        self.board = Board(self.image_widgets[0:15], self.image_widgets[15])
        self.render_icons()

        for i, tile in enumerate(self.tiles):
            tile.setIconSize(QSize(100, 100))
            tile.clicked.connect(lambda _, i=i: self.move_tile(i))
            tile.setEnabled(True)

    def update_moves_label(self):
        self.moves_label.setText(f"Moves: {self.moves}")

    def restart_game(self):
        self.init_timer()
        self.init_tiles()
        self.moves = 0
        self.update_moves_label()

    def move_tile(self, index: int):
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


def main():
    folder = "./Source"
    images = [
        os.path.join(folder, f) for f in os.listdir(folder) if f.startswith("ImageP")
    ]

    app = QApplication(sys.argv)
    game = MainWindow(images)
    game.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
