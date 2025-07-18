from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self) -> None:
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.body_color: tuple[int, int, int] = None

    def randomize_position(self) -> None:
        """Устанавливает случайную позицию для объекта."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self) -> None:
        """Отображает объект на экране."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока, которое змейка съедает."""

    def __init__(self) -> None:
        super().__init__()
        self.randomize_position()
        self.body_color = APPLE_COLOR


class Snake(GameObject):
    """Класс змейки."""

    def __init__(self) -> None:
        super().__init__()
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] = None
        self.body_color = SNAKE_BODY_COLOR
        self.head_color = SNAKE_HEAD_COLOR

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Двигает змейку по полю."""
        head_position = (
            (self.get_head_position()[0] + self.direction[0] * GRID_SIZE)
            % SCREEN_WIDTH,
            (self.get_head_position()[1] + self.direction[1] * GRID_SIZE)
            % SCREEN_HEIGHT,
        )
        self.positions.insert(0, head_position)
        self.removed: list[tuple[int, int]] = []
        while len(self.positions) > self.length:
            self.removed.append(self.positions.pop())

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает игру и возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        directions = [UP, DOWN, LEFT, RIGHT]
        self.direction = choice(directions)
        screen.fill(BOARD_BACKGROUND_COLOR)

    def draw(self) -> None:
        """Отображает змейку на экране."""
        for position in getattr(self, 'removed', []):
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.head_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)


class WrongApple(GameObject):
    """Класс неправильного яблока, которое уменьшает длину змейки."""

    def __init__(self) -> None:
        super().__init__()
        self.randomize_position()
        self.body_color = WRONG_APPLE_COLOR


class Rock(GameObject):
    """Класс препятствия (камня), с которым змейка не должна сталкиваться."""

    def __init__(self) -> None:
        super().__init__()
        self.randomize_position()
        self.body_color = ROCK_COLOR


class Game:
    """Основной класс игры."""

    def __init__(self) -> None:
        self.apple = Apple()
        self.snake = Snake()
        self.wrong_apple = WrongApple()
        self.rock = Rock()
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
        """Перемещает все объекты в случайные позиции на поле и проверяет
        не появились ли они друг в друге.
        """
        for item in self.items:
            while True:
                item.randomize_position()
                item_positions = [
                    other_item.position
                    for other_item in self.items
                    if other_item != item
                ]
                if (item.position not in self.snake.positions
                        and item.position not in item_positions):
                    screen.fill(BOARD_BACKGROUND_COLOR)
                    break

    def object_status(self, item: GameObject) -> None:
        """Проверяет, есть ли пересечение между объектом и змейкой."""
        if self.snake.get_head_position() == item.position:
            if isinstance(item, Rock):
                self.game_over()
            elif isinstance(item, WrongApple):
                self.snake.length -= 1
                self.randomize_all_items()
                if self.snake.length < 1:
                    self.game_over()
            elif isinstance(item, Apple):
                self.snake.length += 1
                self.randomize_all_items()
                self.increase_speed()
        elif (item.position in self.snake.positions[1:]
              or any(item.position == other.position
                     for other in self.items if other != item)):
            self.randomize_all_items()

    def game_over(self) -> None:
        """Выводит экран с сообщением о конце игры и кнопками Restart, Exit."""
        self.game_speed = DEFAULT_GAME_SPEED
        running = True
        font = pygame.font.SysFont(None, 48)
        small_font = pygame.font.SysFont(None, 36)

        game_over_text = font.render('Game Over', True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )

        restart_text = small_font.render('Restart', True, (0, 0, 0))
        restart_rect = restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )

        exit_text = small_font.render('Exit', True, (0, 0, 0))
        exit_rect = exit_text.get_rect(center=(
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
        )

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif (event.type == pygame.MOUSEBUTTONDOWN
                      and event.button == 1):
                    if restart_rect.collidepoint(event.pos):
                        self.snake.reset()
                        return
                    elif exit_rect.collidepoint(event.pos):
                        pygame.quit()
                        exit()

            screen.fill((BOARD_BACKGROUND_COLOR))
            screen.blit(game_over_text, game_over_rect)

            pygame.draw.rect(screen, (200, 200, 200),
                             restart_rect.inflate(20, 10))
            pygame.draw.rect(screen, (200, 200, 200),
                             exit_rect.inflate(20, 10))

            screen.blit(restart_text, restart_rect)
            screen.blit(exit_text, exit_rect)

            pygame.display.update()

    def increase_speed(self) -> None:
        """Увеличивает скорость игры после
        каждого пятого роста длины змейки.
        """
        if self.snake.length % 5 == 0:
            self.game_speed += 1


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш и меняет направление змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Основной цикл игры."""
    pygame.init()
    pygame.font.init()
    game = Game()
    while True:
        clock.tick(game.game_speed)
        handle_keys(game.snake)
        pygame.display.set_caption(
            f'Snake | Length: {game.snake.length}'
            f'| Speed: {game.game_speed - 3}'
        )
        game.snake.update_direction()
        game.snake.move()
        game.check_snake_colission()
        game.object_status(game.apple)
        game.object_status(game.wrong_apple)
        game.object_status(game.rock)
        game.wrong_apple.draw()
        game.rock.draw()
        game.apple.draw()
        game.snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
