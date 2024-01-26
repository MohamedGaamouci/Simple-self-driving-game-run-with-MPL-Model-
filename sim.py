import pygame
import joblib as jb
import numpy as np
import random

'''The Notice '''
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# Initialize Pygame
pygame.init()

# Set up the screen and other constants
width, height = 600, 150
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Notice')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font settings
font = pygame.font.Font(None, 36)


def show_popup():
    popup_width, popup_height = 600, 150
    popup_x = (width - popup_width) // 2
    popup_y = (height - popup_height) // 2

    popup_surface = pygame.Surface((popup_width, popup_height))
    popup_surface.fill(WHITE)

    # Draw text on the popup surface
    message_text = font.render(
        "You can replace the car place by the mouse click ", True, BLACK)
    message_rect = message_text.get_rect(
        center=(popup_width // 2, popup_height // 2 - 20))
    popup_surface.blit(message_text, message_rect)

    # Draw the OK button
    ok_button_rect = pygame.Rect(250, 100, 100, 40)
    pygame.draw.rect(popup_surface, (0, 255, 0), ok_button_rect)
    ok_text = font.render("OK", True, WHITE)
    ok_text_rect = ok_text.get_rect(center=ok_button_rect.center)
    popup_surface.blit(ok_text, ok_text_rect)

    # Draw the popup on the main screen
    screen.blit(popup_surface, (popup_x, popup_y))
    pygame.display.flip()


def exit_game():
    print('exit popup')
    pygame.quit()
    exit()


# Game loop
run = True
show_popup()
while run:
    for event in pygame.event.get():
        if event.type == QUIT or event.type == MOUSEBUTTONDOWN:
            run = False

    pygame.display.flip()

pygame.quit()


'''The Game'''
# intialize a pygame "create a constuctor pygame "
pygame.init()

# intialize a screen of game
# size of screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
# title of
pygame.display.set_caption('CAR GAME with AI')
# load a image
img_back = pygame.image.load('back.png')
# transform  size of picture to size of the screen
img_back = pygame.transform.scale(img_back, (width, height))
image = pygame.image.load('car1.png')
# object settings
object_size = 50
object_speed = 1
# initialize class of car


class car(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        # initialize dimensions of robot
        image_scale = 45 / image.get_rect().width
        new_w = image.get_rect().width * image_scale
        new_h = image.get_rect().height * image_scale
        self.original_image = pygame.transform.scale(
            image, (int(new_w), int(new_h)))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.angle = 0

    def rotate2(self, direction):
        dir = ''
        if direction == "turn_left":
            print('enter left')
            self.angle = 90
            dir = 'left'
        elif direction == 'turn_right':
            self.angle = -90
            dir = 'right'
        elif direction == 'advance':
            self.angle = 0
            dir = 'top'
        elif direction == 'retreat':
            self.angle = 180
            dir = 'back'

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        return dir
# Obstacle class


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))  # Red color for the obstacle
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


x_c_car, y_c_car = 250, 370

# car = car(image, 550, 650)
# car = car(image, 777, 650)
car = car(image, x_c_car, y_c_car)
# car = car(image, 400, 400)

all_sprites = pygame.sprite.Group()
all_sprites.add(car)


# Initialize fixed obstacles
obstacles = pygame.sprite.Group()

for i in range(40):
    car_x, car_y = car.rect.center
    xObstacle = random.randint(0, width-object_size)
    yObstacle = random.randint(0, height-object_size)
    if xObstacle not in range(car_x-30, car_x+30) and yObstacle not in range(car_y-object_size, car_y+object_size):
        obstacles.add(Obstacle(xObstacle, yObstacle))

all_sprites.add(obstacles)


run = True


def calculate_distance():
    car_x, car_y = car.rect.center

    f_d = car_y - object_size  # 50 the car dimension
    b_d = height - car_y - object_size
    r_d = width - car_x - object_size
    l_d = car_x - object_size
    if f_d < 0:
        f_d = 0
    elif b_d < 0:
        b_d = 0
    elif r_d < 0:
        r_d = 0
    elif l_d < 0:
        l_d = 0
    sensor = {
        "frond_d": f_d,
        "back_d": b_d,
        "right_d": r_d,
        "left_d": l_d
    }

    for obs in obstacles:
        x = obs.rect.centerx
        y = obs.rect.centery
        if car_x in range(x-object_size, x+object_size):
            distx = car_y - y
            if distx < 0:
                distx = abs(distx)-75  # 75 hight of the car
                if distx < 0:
                    distx = 0
                sensor['back_d'] = min(min(distx, sensor['back_d']), 300)
            else:
                distx = abs(distx)-75
                if distx < 0:
                    distx = 0
                sensor['frond_d'] = min(min(distx, sensor['frond_d']), 300)
            # print('distance in vertical :: ', distx)
        if car_y in range(y-50, y+50):
            disty = car_x - x
            if disty < 0:
                disty = abs(disty)-75
                if disty < 0:
                    disty = 0
                sensor['right_d'] = min(min(disty, sensor['right_d']), 300)
            else:
                disty = abs(disty)-75
                if disty < 0:
                    disty = 0
                sensor['left_d'] = min(min(disty, sensor['left_d']), 300)
            # print('distance in horizontal :: ', disty)
    return sensor


def make_decision(input_model):
    predicted_direction = np.argmax(model.predict(input_model))+1
    predicted_direction = decode[predicted_direction]
    return predicted_direction


decode = {
    1: 'advance',
    2: 'turn_right',
    3: 'turn_left',
    4: 'retreat'
}
'''model loading'''
model = jb.load("apprentisage.joblib")  # model load
t = 0  # for the first dicision
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse click
            # Change car position to the mouse cursor position
            car.rect.center = pygame.mouse.get_pos()
            car.angle = 90

    print('*'*50)

    dis = calculate_distance()
    print(dis)
    input_model = np.array(
        [[dis['frond_d'], dis['back_d'], dis['left_d'], dis['right_d']]])

    if t == 0:
        predicted_direction = make_decision(input_model=input_model)
        t = t+1
        print('first decision')

    if predicted_direction == 'turn_left' and car.rect.left > 0:
        dir = car.rotate2(direction='turn_left')
        car.rect.x -= object_speed
    elif predicted_direction == 'turn_right' and car.rect.right < width:
        dir = car.rotate2(direction='turn_right')
        car.rect.x += object_speed
    elif predicted_direction == 'advance' and car.rect.top > 0:
        dir = car.rotate2(direction='advance')
        car.rect.y -= object_speed
    elif predicted_direction == 'retreat' and car.rect.bottom < height:
        dir = car.rotate2(direction='retreat')
        car.rect.y += object_speed
    print(dir)

    if input_model[0, 0] <= 1 and dir == 'top':
        predicted_direction = make_decision(input_model=input_model)
        print('decision ...')
    if input_model[0, 1] <= 1 and dir == 'back':
        predicted_direction = make_decision(input_model=input_model)
        print('decision ...')
    if input_model[0, 2] <= 1 and dir == 'left':
        predicted_direction = make_decision(input_model=input_model)
        print('decision ...')
    if input_model[0, 3] <= 1 and dir == 'right':
        predicted_direction = make_decision(input_model=input_model)
        print('decision ...')

    # print(dis)
    for y in (width * -2, height, width*2):
        # condition collision
        if pygame.sprite.spritecollide(car, obstacles, False):
            print("Collision!")
            pygame.time.delay(100)  # Pause for a moment
            # Reset player position
            car.rect.center = (x_c_car, y_c_car)
            car.angle = 90
    screen.blit(img_back, (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
