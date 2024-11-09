import numpy as np
import pygame
from engine import Renderer3D
from physics import Physics3D

pygame.init()
screen = pygame.display.set_mode((900, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

def text(text, pos):
    screen.blit(font.render(text, 1, (255, 255, 255)), pos)

# Initialize Renderer3D and Physics3D instances
r = Renderer3D((900, 600))
p = Physics3D()

camera_speed = 10
rotation_speed = 2
r.render_distance = 2000

# Initial ground box in the scene
p.create_box((0, 0, 0), (0, 0, 0), 1000, 0, 1000, 1)

r.cPOS = np.array([510, -320, -470], dtype=float)

while True:
    # Clear render list for each frame
    r.Render_3D = []
    
    # Generate and add 3D render lines for each item in physics
    for item in p.items:
        r.Render_3D.extend(r.generate_cube(
            [(255, 255, 255)] * 6,
            (item["x"] + item["width"]/2, item["y"], item["z"] + item["depth"]/2),
            (item["angle_x"], item["angle_y"], item["angle_z"]),
            item["width"], item["height"], item["depth"],
            fill=0
            
        ))

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Add a box when mouse button is pressed
            p.create_box(r.cPOS, r.cORENTATION, 100, 100, 100)

    # Camera movement control
    keys = pygame.key.get_pressed()
    forward = np.array([0, 0, 1])
    up = np.array([0, 1, 0])
    right = np.array([1, 0, 0])
    
    direction_forward = np.dot(r.cached_rotation_matrix, forward)
    direction_up = np.dot(r.cached_rotation_matrix, up)
    direction_right = np.dot(r.cached_rotation_matrix, right)
    
    if keys[pygame.K_w]: r.cPOS += direction_forward * camera_speed
    if keys[pygame.K_s]: r.cPOS -= direction_forward * camera_speed
    if keys[pygame.K_d]: r.cPOS += direction_right * camera_speed
    if keys[pygame.K_a]: r.cPOS -= direction_right * camera_speed
    if keys[pygame.K_LSHIFT]: r.cPOS += direction_up * camera_speed
    if keys[pygame.K_SPACE]: r.cPOS -= direction_up * camera_speed

    # Camera rotation control
    if keys[pygame.K_LEFT]: r.cORENTATION[1] += rotation_speed
    if keys[pygame.K_RIGHT]: r.cORENTATION[1] -= rotation_speed
    if keys[pygame.K_UP]: r.cORENTATION[0] -= rotation_speed
    if keys[pygame.K_DOWN]: r.cORENTATION[0] += rotation_speed

    # Adjust render distance
    if keys[pygame.K_i]: r.render_distance += 10
    if keys[pygame.K_o]: r.render_distance -= 10

    # Update renderer and physics for each frame
    r.tick()
    p.tick()    

    # Render each line in the to_render list
    for line in r.to_render:
        if line[1][0] and line[1][1]:  # Ensure points are valid
            pygame.draw.line(screen, line[2], line[1][0], line[1][1], 1)

    
    # Display camera position, orientation, and FPS
    text(f"Position: {r.cPOS}, Orientation: {r.cORENTATION}", (10, 10))
    text(f"FPS: {clock.get_fps():.2f}", (10, 40))
    text(f"Render Distance: {r.render_distance}, lines: {len(r.Render_3D)}, parts: {len(p.items)}", (10, 60))

    pygame.display.flip()
    clock.tick(60)  # Set frame rate to 60 FPS
