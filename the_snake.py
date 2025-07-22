from random import choice, randint

<<<<<<< HEAD
import pygame
=======
import pygame as pg
>>>>>>> 5902195 (commit after first reviev)

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
GRID_CENTER = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2
)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DEFAULT_GAME_SPEED = 4
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
WRONG_APPLE_COLOR = (120, 120, 0)
ROCK_COLOR = (128, 128, 128)
SNAKE_BODY_COLOR = (0, 255, 0)
SNAKE_HEAD_COLOR = (0, 100, 0)
GAME_OVER_TEXT_COLOR = (255, 0, 0)
BUTTON_BACKGROUND_COLOR = (200, 200, 200)
BUTTON_TEXT_COLOR = (0, 0, 0)
BUTTON_INFLATE_SIZE = (20, 10)

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, body_color, position=None) -> None:
        self.position: tuple[int, int] = position or GRID_CENTER
        self.body_color: tuple[int, int, int] = body_color

    def draw(self) -> None:
        """Отображает объект на экране,"""
        """должен быть реализован в дочерних классах"""
        raise NotImplementedError(
            'Метод draw() должен быть переопределён '
            'в дочернем классе для отрисовки объекта.'
        )

    def draw_cell(self) -> None:
        """Отрисовывает одну ячейку игрового поля"""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class EdibleObject(GameObject):
    """Класс игровых объектов, которое змейка съедает."""

    def __init__(self, body_color, position) -> None:
        super().__init__(body_color, position)

    def draw(self):
        """отрисовывает 'съедаемые' объекты"""
        self.draw_cell()


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self, body_color, head_color, ) -> None:
        super().__init__(body_color)
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] = None
        self.head_color = head_color

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Двигает змейку по полю."""
        head_position_x, head_position_y = self.get_head_position()
        direction_x, direction_y = self.direction
        head_position = (
            (head_position_x + direction_x * GRID_SIZE)
            % SCREEN_WIDTH,
            (head_position_y + direction_y * GRID_SIZE)
            % SCREEN_HEIGHT,
        )
        self.positions.insert(0, head_position)
        while len(self.positions) > self.length:
            self.positions.pop()

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает игру и возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

    def draw(self) -> None:
        """Отображает змейку на экране."""
        for self.position in self.positions[1:]:
            self.draw_cell()

        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.head_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)


class Game:
    """Основной класс игры."""

    def __init__(self) -> None:
        self.snake = Snake(SNAKE_BODY_COLOR, SNAKE_HEAD_COLOR)
        self.occupied_positions = self.snake.positions[:]
        self.apple = EdibleObject(
            APPLE_COLOR, randomize_position(self.occupied_positions)
        )
        self.wrong_apple = EdibleObject(
            WRONG_APPLE_COLOR, randomize_position(self.occupied_positions)
        )
        self.rock = EdibleObject(
            ROCK_COLOR, randomize_position(self.occupied_positions)
        )
        self.game_speed: int = DEFAULT_GAME_SPEED
        self.items: list[GameObject] = [
            self.apple,
            self.wrong_apple,
            self.rock
        ]

    def check_snake_colission(self) -> None:
        """Проверяет столкновение змейки с её телом."""
        if self.snake.get_head_position() in self.snake.positions[1:]:
            self.game_over()

    def randomize_all_items(self) -> None:
        """Размещает, одновременно, все игровые объекты случайным образом"""
        self.occupied_positions = self.snake.positions[:]
        self.apple.position = randomize_position(self.occupied_positions)
        self.wrong_apple.position = randomize_position(self.occupied_positions)
        self.rock.position = randomize_position(self.occupied_positions)

    def object_status(self, item: GameObject) -> None:
        """Проверяет, есть ли пересечение между объектом и змейкой."""
        if self.snake.get_head_position() == item.position:
            if item.body_color == ROCK_COLOR:
                self.game_over()
            elif item.body_color == WRONG_APPLE_COLOR:
                if self.snake.length == 1:
                    self.game_over()
                    return
                self.snake.length -= 1
            elif item.body_color == APPLE_COLOR:
                self.snake.length += 1
                self.increase_speed()
            self.randomize_all_items()

    def game_over(self) -> None:
        """Выводит экран с сообщением о конце игры и кнопками Restart, Exit."""
        self.game_speed = DEFAULT_GAME_SPEED
        running = True
        font = pg.font.SysFont(None, 48)
        small_font = pg.font.SysFont(None, 36)

        game_over_text = font.render('Game Over', True, GAME_OVER_TEXT_COLOR)
        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )

        restart_text = small_font.render('Restart', True, BUTTON_TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(GRID_CENTER))

        exit_text = small_font.render('Exit', True, BUTTON_TEXT_COLOR)
        exit_rect = exit_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        )

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit()

                elif (event.type == pg.MOUSEBUTTONDOWN
                      and event.button == 1):
                    if restart_rect.collidepoint(event.pos):
                        self.snake.reset()
                        return
                    elif exit_rect.collidepoint(event.pos):
                        pg.quit()
                        exit()

            screen.fill((BOARD_BACKGROUND_COLOR))
            screen.blit(game_over_text, game_over_rect)

            pg.draw.rect(screen, (BUTTON_BACKGROUND_COLOR),
                         restart_rect.inflate(BUTTON_INFLATE_SIZE))
            pg.draw.rect(screen, (BUTTON_BACKGROUND_COLOR),
                         exit_rect.inflate(BUTTON_INFLATE_SIZE))

            screen.blit(restart_text, restart_rect)
            screen.blit(exit_text, exit_rect)

            pg.display.update()

    def increase_speed(self) -> None:
        """
        Увеличивает скорость игры после
        каждого пятого роста длины змейки.
        """
        if self.snake.length % 5 == 0:
            self.game_speed += 1


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш и меняет направление змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def randomize_position(occupied_positions) -> tuple[int, int]:
    """
    Генерирует случайную позицию для объекта,
    избегая уже занятых координат.
    """
    while True:
        position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        if position not in occupied_positions:
            occupied_positions.append(position)
            return position


def main() -> None:
    """Основной цикл игры."""
    pg.init()
    pg.font.init()
    game = Game()
    while True:
        clock.tick(game.game_speed)
        handle_keys(game.snake)
        pg.display.set_caption(
            f'Snake | Length: {game.snake.length}'
            f'| Speed: {game.game_speed - 3}'
        )
        game.snake.update_direction()
        game.snake.move()
        game.check_snake_colission()
        game.object_status(game.apple)
        game.object_status(game.wrong_apple)
        game.object_status(game.rock)
        screen.fill(BOARD_BACKGROUND_COLOR)
        game.snake.draw()
        game.wrong_apple.draw()
        game.rock.draw()
        game.apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
