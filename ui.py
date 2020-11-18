from __future__ import unicode_literals

from engine import SudokuEngine, UnableToInsert

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import (
    BooleanProperty, ListProperty, NumericProperty, ObjectProperty
)
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

Window.size = (500, 500)


WHITE = [255, 255, 255, 1]
BLUE = [0.537, 0.769, 0.957, 1]
GRAY = [45, 81, 157, 0.9]
RED = [255, 0, 0, 1]


class BaseSudokuButton(Button):
    background_color = ListProperty(WHITE)
    color = ListProperty([0, 0, 0, 1])
    sudoku_engine = ObjectProperty()
    row = NumericProperty()
    column = NumericProperty()


class SudokuInputButton(FocusBehavior, BaseSudokuButton):
    def on_press(self):
        self.focus = True
        self.background_color = BLUE

    def on_focus(self, instance, value):
        if value is True:
            self.background_color = BLUE
        else:
            self.background_color = WHITE

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        # check if number should be inserted
        text = text or ''
        if text and text in '123456789':
            try:
                self.sudoku_engine.insert(
                    row=self.row, column=self.column, value=int(text)
                )
            except UnableToInsert:
                self.background_color = RED
                Clock.schedule_once(self.error_color, 0.4)
            else:
                self.text = text
                self.background_color = WHITE
            finally:
                self.focus = False

        # check if number should be removed
        code, name = keycode
        if name == "backspace":
            self.sudoku_engine.clear(row=self.row, column=self.column)
            self.text = ""
            self.focus = False

        # check if sudoku is solved
        if self.sudoku_engine.is_solved():
            self.parent.parent.solved = True

    def error_color(self, *args, **kwargs):
        anim = Animation(background_color=WHITE)
        anim.start(self)


class SudokuLockedButton(BaseSudokuButton):
    background_color = ListProperty(GRAY)


class SudokuBoard(BoxLayout):
    difficulty = NumericProperty()
    solved = BooleanProperty(False)
    ready = BooleanProperty(False)

    def create_cells(self):
        """Create cells with borders, numbers if provided with initial board"""
        for column in range(1, 10):
            box = BoxLayout(orientation='vertical')
            bottom, right, top, left = (16, 16, 16, 16)
            right = 0 if column in (3, 6) else 16
            for row in range(1, 10):
                bottom = 0 if row in (3, 6) else 16
                logical_row = row - 1
                logical_column = column - 1
                text = str(
                    self.sudoku_engine.get(
                        column=logical_column, row=logical_row
                    ) or ''
                )
                cell_class = SudokuLockedButton if text else SudokuInputButton
                button = cell_class(
                    id='{}{}'.format(column, row),
                    row=logical_row,
                    column=logical_column,
                    border=[bottom, right, top, left],
                    sudoku_engine=self.sudoku_engine,
                    text=text,
                )
                box.add_widget(button)
            self.add_widget(box)

    def on_solved(self, instance, solved):
        """Propagate solved to the parent, this takes care of cleanup or
        setup if sudoku puzzle is solved or not.
        """
        if solved:
            self.parent.parent.solved = True
            self.ready = False
        else:
            self.parent.parent.solved = False
            self.ready = True

    def on_ready(self, instance, ready):
        """Prepare widgets or remove them, depending on the state."""
        if ready:
            self.sudoku_engine = SudokuEngine.generate(
                difficulty=self.difficulty
            )
            self.parent.parent.solved = False
            self.create_cells()
        else:
            self.sudoku_engine = None
            self.clear_widgets()


class MenuScreen(Screen):
    pass


class GameScreen(Screen):
    difficulty = NumericProperty()
    solved = BooleanProperty(False)

    def on_pre_enter(self):
        """Makes sure that upon entering the state is reset and sudoku will be
        generated.
        """
        self.solved = False
        sudoku_board_widget = self.children[0].children[0]
        sudoku_board_widget.ready = True
        sudoku_board_widget.solved = False

    def on_solved(self, instance, solved):
        """Go to menu if sudoku puzzle is solved"""
        if solved:
            self.manager.current = "menu"


class SudokuScreenManager(ScreenManager):
    def game_screen(self, difficulty):
        """Pass difficulty and change screen"""
        self.get_screen("game").difficulty = difficulty
        self.current = "game"
