# EEG arcade game - controlled by Muse 2 headband
"""
Requirements: * muselsl library running in the background ('muselsl stream')
              * Muse headband (only tested with Muse 2 so far)
Developer:      Christoph Döllinger (christoph.d@posteo.de)
"""
import pygame
import random
import paho.mqtt.client as mqtt_client
import subprocess
import time

# Game dimensions
WIDTH = 1280
HEIGHT = 800

# Colors
YELLOW = (255, 255, 0)
LIGHTGREEN = (0, 255, 150)
LIGHTBLUE = (0, 200, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# plane dimensions
PLANE_WIDTH = 40
PLANE_HEIGHT = 40
PLANE_SPEED_X = 1
PLANE_SPEED_Y = 5

STAR_SIZE = 24

# run neurofeedback.py in thread
process = subprocess.Popen('python neurofeedback.py', shell=True, stdout=subprocess.PIPE)

# server for MUSE signal
broker = "test.mosquitto.org"
port = 1883
topic = "ShipGame"
client_id = f'subscribe-{random.randint(0, 1000)}'

eeg_signal = 0
counter = 0

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# subscribe to MUSE signal
def subscribe(client: mqtt_client): # type: ignore
    def on_message(client, userdata, msg):
        global eeg_signal
        eeg_signal = float(msg.payload.decode())
        #print(f"Received `{eeg_signal}` from `{msg.topic}` topic")

    client.subscribe(topic) # type: ignore
    client.on_message = on_message # type: ignore

# access and subscribe to MUSE signal
client = connect_mqtt()
subscribe(client) # type: ignore
client.loop_start()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ship Game")
font = pygame.font.Font(None, 36)
star_img = pygame.image.load("star.png")
plane_img = pygame.image.load("plane.png")

# Set up initial game variables
clock = pygame.time.Clock()
plane_pos = [0, HEIGHT // 2]
score = 0

# calibrate the minimum and maximum eeg signal
min_eeg = 2.0
max_eeg = -2.0

# calibrate the minimum eeg signal
def calibrate_min():
    global min_eeg
    global counter
    global eeg_signal
    global client
    counter = 0
    time.sleep(1)
    while counter < 100:
        if eeg_signal < min_eeg:
            min_eeg = eeg_signal
        counter += 2
        screen.fill(BLACK)
        print("Current EEG Signal: ", eeg_signal)
        calibrate_text = font.render("Calibrating Minimum EEG value... Please look around and try not to focus on something special.", True, WHITE)
        screen.blit(calibrate_text, (50, 50))
        progress_text = font.render("Progress " + str(counter) + "%", True, LIGHTGREEN)
        screen.blit(progress_text, (50, 100))
        pygame.display.flip()
        time.sleep(0.15)

    if min_eeg < -2.0:
        min_eeg = -2.0

    min_eeg = min_eeg * 1.2
    print("Min: ", min_eeg)    

# calibrate the maximum eeg signal
def calibrate_max():
    global max_eeg
    global counter
    global eeg_signal
    global client

    # reset plane position
    plane_pos_x = 50
    plane_pos_y = int(HEIGHT // 2)
    
    # calibration text
    screen.fill(BLACK)
    calibrate_text = font.render("Calibrating Maximum EEG Value", True, WHITE)
    screen.blit(calibrate_text, (100, 100))
    pygame.display.flip()
    time.sleep(1)

    # move the plane
    while plane_pos_x < WIDTH - PLANE_WIDTH:
        plane_pos_x += 8
        plane_pos_y += 8 * eeg_signal

        # clamp plane position
        if plane_pos_y < 0:
            plane_pos_y = 0
        elif plane_pos_y > HEIGHT - PLANE_HEIGHT:
            plane_pos_y = HEIGHT - PLANE_HEIGHT

        # clear screen
        screen.fill(BLACK)

        # calibration text
        calibrate_text = font.render("Calibrating Maximum EEG Value", True, WHITE)
        screen.blit(calibrate_text, (100, 100))
        
        # Draw the plane from plane.png
        screen.blit(plane_img, (plane_pos_x, plane_pos_y))
        pygame.display.flip()

        # get max eeg signal
        if eeg_signal > max_eeg:
            max_eeg = eeg_signal
        
        print("Current EEG Signal: ", eeg_signal)
        time.sleep(0.05)

    if max_eeg > 2.0:
        max_eeg = 2.0

    max_eeg = max_eeg * 1.2
    print("Max: ", max_eeg)

def show_calibration():
    calibrate_text = font.render("Min: " + str(round(min_eeg, 2)) + " Max: " + str(round(max_eeg, 2)), True, WHITE)
    screen.blit(calibrate_text, (370, 10))
    # show eeg signal
    eeg_text = font.render("EEG Signal: " + str(round(eeg_signal, 2)), True, WHITE)
    screen.blit(eeg_text, (150, 10))
    # show acceleration
    accel_text = font.render("Acceleration: " + str(round(acceleration, 2)), True, WHITE)
    screen.blit(accel_text, (550, 10))
    pygame.display.flip()

def show_score():
    score_text = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_text, (WIDTH - 150, 10))
    pygame.display.flip()

#screen.fill(LIGHTGREEN)
#calibrate_min()
#calibrate_max()
#screen.fill(BLACK)

# reset plane position
plane_pos_x = 0
plane_pos_y = HEIGHT - PLANE_HEIGHT 

acceleration = 5

# jingle sound
pygame.mixer.music.load("jingle.wav")

stars = []

# Game loop
running = True
counter = 0

# record start time
start_time = time.time()

# run the game for 120 seconds
while running and time.time() - start_time < 120:
    counter += 1

    # Handle keyboard events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            # Quit the game
            process.terminate()
            pygame.quit()
        # move the acceleration up and down
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                acceleration = acceleration+1
            elif event.key == pygame.K_DOWN and acceleration > 1:
                acceleration = acceleration-1
            elif event.key == pygame.K_SPACE:
                acceleration = 5
    # add gradient background
    screen.fill(LIGHTBLUE)
    pygame.draw.rect(screen, LIGHTGREEN, (0, HEIGHT-50, WIDTH, HEIGHT-50))

    if counter % 80 == 0:
        # Create star on random positions on the right side
        star_x = WIDTH - STAR_SIZE
        star_y = random.randint(STAR_SIZE, HEIGHT // 2)

        # check distance to other stars and correct position
        if len(stars) > 0:
            for star in stars:
                if abs(star[1] - star_y) < STAR_SIZE:
                    star_y += STAR_SIZE + 5            

        stars.append([star_x, star_y])

    # Move the stars
    for star in stars:
        star[0] -= 5

        # check if star is out of screen
        if star[0] < 0:
            stars.remove(star)
            
            # add new star
            star_x = WIDTH - STAR_SIZE
            star_y = random.randint(STAR_SIZE, HEIGHT // 2)
            stars.append([star_x, star_y])

        # Draw the stars from star.png
        screen.blit(star_img, (star[0], star[1]))

    # normalize eeg signal
    # if eeg_signal > max_eeg:
    #     eeg_signal = max_eeg
    # elif eeg_signal < min_eeg:
    #     eeg_signal = min_eeg

    # minimum shall be 0.0 and maximum shall be 1.0
    #eeg_signal_norm = (eeg_signal - min_eeg) / (max_eeg - min_eeg)

    print("EEG: ", eeg_signal)
    #print("EEG (norm): ", eeg_signal_norm)

    # calculate plane position
    plane_pos_y -= acceleration * eeg_signal * (plane_pos_y / HEIGHT)

    print("Plane Y: ", plane_pos_y)
    # apply gravity to plane
    plane_pos_y += 1

    # clamp the plane position to the screen height
    if plane_pos_y < PLANE_HEIGHT:
        plane_pos_y = PLANE_HEIGHT
    elif plane_pos_y > HEIGHT - PLANE_HEIGHT:
        plane_pos_y = HEIGHT - PLANE_HEIGHT

    # Draw the plane from plane.png
    screen.blit(plane_img, (plane_pos_x, plane_pos_y))

    # Check for collisions
    for star in stars:
        if plane_pos_x + PLANE_WIDTH > star[0] and plane_pos_x < star[0] + STAR_SIZE:
            if plane_pos_y + PLANE_HEIGHT > star[1] and plane_pos_y < star[1] + STAR_SIZE:
                # increase score
                score += 1

                # play jingle sound
                pygame.mixer.music.play()

                # remove star
                stars.remove(star)

    # Display the score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Display the calibration values
    show_calibration()

    # Display the time left
    time_left = 120 - int(time.time() - start_time)
    time_text = font.render(f"Time: {time_left}", True, WHITE)

    # Update the screen
    pygame.display.flip()

    clock.tick(60)

# Display total score
screen.fill(BLACK)
score_text = font.render(f"Total Score: {score}", True, WHITE)
screen.blit(score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
pygame.display.flip()
time.sleep(5)
