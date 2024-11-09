'''
A basic 3d engine made for pygame and other libs 
(ps: import Render3D)

some tips are
all secne items are give befor the first tick()
then each item is given to Render_3D
after every tick() to_render has all the 2d lines in this manner
(((startx, starty), (endx, endy)), colour(rgb))

the screen size of your view port ie window size is give at __init__()
rest is done by the Renderer

I the maker recoment a line width of 3.5 to 5 but you can choose your own


'''

import numpy as np
class Renderer3D:
    def __init__(self, screen_size):
        self.Render_3D = []  # Store 3D lines to render
        self.to_render = []  # Store lines ready for 2D rendering
        self.cPOS = np.array([0, 0, -500], dtype=float)  # Camera position
        self.cORENTATION = np.array([0, 0, 0], dtype=float)  # Camera orientation (pitch, yaw, roll)
        self.fov = 400  # Field of view
        self.screenw = screen_size[0]
        self.screenh = screen_size[1]
        self.cached_rotation_matrix = np.identity(3)
        self.render_distance = 100
        
    def EulerRotationMatrix(self, pitch, yaw, roll):
        pitch, yaw, roll = np.radians([pitch, yaw, roll])
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch)],
            [0, np.sin(pitch), np.cos(pitch)]
        ])
        Ry = np.array([
            [np.cos(yaw), 0, np.sin(yaw)],
            [0, 1, 0],
            [-np.sin(yaw), 0, np.cos(yaw)]
        ])
        Rz = np.array([
            [np.cos(roll), -np.sin(roll), 0],
            [np.sin(roll), np.cos(roll), 0],
            [0, 0, 1]
        ])
        return Rz @ Ry @ Rx

    def convert_3d_to_2d(self, point_3d):
        point_cam = np.dot(self.cached_rotation_matrix, np.subtract(point_3d, self.cPOS))

        if point_cam[2] <= 0 or np.linalg.norm(point_cam) > self.render_distance:
            return None

        x_2d = self.fov * (point_cam[0] / point_cam[2]) + self.screenw / 2
        y_2d = self.fov * (point_cam[1] / point_cam[2]) + self.screenh / 2
        return (x_2d, y_2d)
    
    def GenerateTriangle(self, p1, p2, p3, color=(255, 255, 255), fill=0):
        '''
        core function for anything
        (ps: fill fills the triangle)
        '''
        
        
        lines = []
        edges = [
            ((p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2]), color),
            ((p2[0], p2[1], p2[2]), (p3[0], p3[1], p3[2]), color),
            ((p3[0], p3[1], p3[2]), (p1[0], p1[1], p1[2]), color)
        ]
        lines.extend(edges)
        if not fill:
            return lines
        vertices = sorted([p1, p2, p3], key=lambda v: v[1])
        v_top, v_mid, v_bot = vertices
        def interpolate(p_start, p_end, y):
            t = (y - p_start[1]) / (p_end[1] - p_start[1]) if p_end[1] != p_start[1] else 0
            x = p_start[0] + t * (p_end[0] - p_start[0])
            z = p_start[2] + t * (p_end[2] - p_start[2])
            return (x, y, z)
        for y in range(int(v_top[1]), int(v_bot[1]) + 1):
            if y < v_mid[1]:  
                p_left = interpolate(v_top, v_bot, y)
                p_right = interpolate(v_top, v_mid, y)
            else:  
                p_left = interpolate(v_top, v_bot, y)
                p_right = interpolate(v_mid, v_bot, y)
            if p_left[0] > p_right[0]:
                p_left, p_right = p_right, p_left
            lines.append(((p_left[0], y, p_left[2]), (p_right[0], y, p_right[2]), color))
        return lines

    def generate_cube(self, colors, pos, orientation=(0, 0, 0), L=100, B=100, H=100, fill=0):
        '''
        Utility function for generating cubes with a specified orientation.
        (ps: fill fills the triangle)
        '''
        out = []
        
        # Generate the rotation matrix based on the given orientation
        rotation_matrix = self.EulerRotationMatrix(*orientation)
        
        # Define vertices relative to the cube's center position
        local_vertices = [
            (-L/2, -B/2, -H/2), (L/2, -B/2, -H/2), (L/2, B/2, -H/2), (-L/2, B/2, -H/2),
            (-L/2, -B/2, H/2), (L/2, -B/2, H/2), (L/2, B/2, H/2), (-L/2, B/2, H/2)
        ]
        
        # Rotate and translate each vertex
        vertices = [
            tuple(np.dot(rotation_matrix, np.array([x, y, z])) + pos)
            for x, y, z in local_vertices
        ]
        
        # Define the faces using the rotated vertices
        faces = [
            (0, 1, 2, 3),  # Back face
            (4, 5, 6, 7),  # Front face
            (0, 1, 5, 4),  # Bottom face
            (2, 3, 7, 6),  # Top face
            (0, 3, 7, 4),  # Left face
            (1, 2, 6, 5)   # Right face
        ]
        
        # Generate the triangles for each face
        for i, face in enumerate(faces):
            color = colors[i]
            v1, v2, v3, v4 = [vertices[idx] for idx in face]
            out.extend(self.GenerateTriangle(v1, v2, v3, color, fill))
            out.extend(self.GenerateTriangle(v1, v3, v4, color, fill))
        
        return out

    def tick(self):
        '''
        god of the class
        run each frame
        every half a frame if required
        updates ERM and self.to_render
        '''

        # Update the ERM if needed
        if not np.array_equal(self.cached_rotation_matrix, self.cORENTATION):
            self.cached_rotation_matrix = self.EulerRotationMatrix(*self.cORENTATION)


        self.to_render = [
            (np.mean([line[0][2], line[1][2]]), (self.convert_3d_to_2d(line[0]), self.convert_3d_to_2d(line[1])), line[2])
            for line in self.Render_3D
            if self.convert_3d_to_2d(line[0]) and self.convert_3d_to_2d(line[1])
        ]
        self.to_render.sort(reverse=True, key=lambda x: x[0])
