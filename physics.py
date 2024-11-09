class Physics3D:
    DRAG = 1.1
    GRAVITY = 0.5

    def __init__(self):
        self.items = []

    def create_box(self, pos, deg, L, H, D, tick=2, bottom_points=100):
        """Creates a box and adds it to the simulation."""
        self.items.append({
            "x": pos[0],
            "y": pos[1],
            "z": pos[2],
            "xv": 0,
            "yv": 0,
            "zv": 0,
            "angle_x": deg[0],
            "angle_y": deg[1],
            "angle_z": deg[2],
            "angular_velocity_x": 0,
            "angular_velocity_y": 0,
            "angular_velocity_z": 0,
            "width": L,
            "height": H,
            "depth": D,
            "bottom_points": bottom_points,  # Number of points on bottom face for gravity simulation
            "target_angle_x": 0,
            "target_angle_y": 0,
            "target_angle_z": 0,
            "energy": 100,
            "tick?": tick # 0 == none 1 ==  collstion 2 == everything
        })

    def tick(self):
        """Update all boxes for each tick in the simulation."""
        for box in self.items:
            if not box["tick?"]:
                continue
            

            if box["tick?"] > 1:
                # Apply gravity only based on unsupported points on the bottom face
                unsupported_points = self.calculate_unsupported_points(box)
                if unsupported_points > 0:
                    # Calculate proportional gravitational pull
                    gravitational_pull = (unsupported_points / box["bottom_points"]) * self.GRAVITY
                    box["yv"] += gravitational_pull

                    # Apply torque to rotate the box toward the unsupported side
                    self.apply_torque(box, unsupported_points)

                # Update position and velocity
                box["x"] += box["xv"]
                box["y"] += box["yv"]
                box["z"] += box["zv"]

                # Apply drag to reduce velocities
                box["xv"] /= self.DRAG
                box["yv"] /= self.DRAG
                box["zv"] /= self.DRAG
                box["angular_velocity_x"] /= self.DRAG
                box["angular_velocity_y"] /= self.DRAG
                box["angular_velocity_z"] /= self.DRAG



            if box["tick?"] > 0:
                for other in self.items:
                    if other != box:
                        self.handle_collision(box, other)

    def calculate_unsupported_points(self, box):
        """Calculate the number of unsupported points on the bottom face of the box."""
        unsupported_points = 0
        for point in range(box["bottom_points"]):
            # Check if each point is supported using a placeholder logic
            if not self.is_supported(box, point):
                unsupported_points += 1
        return unsupported_points

    def is_supported(self, box, point_index):
        """Check if a specific point on the bottom face of the box has support."""
        # Calculate the coordinates of the specific point on the bottom face
        bottom_face_y = box["y"]  # Bottom face is at `y` for this box
        point_x = box["x"] + (point_index % (box["width"] // 10)) * 10  # Spacing based on width
        point_z = box["z"] + (point_index // (box["width"] // 10)) * 10  # Spacing based on depth

        # Check against other boxes
        for other in self.items:
            if other == box:
                continue  # Skip self

            # Check if point is within the x and z bounds of `other`'s top face
            if (other["x"] <= point_x <= other["x"] + other["width"] and
                other["z"] <= point_z <= other["z"] + other["depth"] and
                abs(bottom_face_y - (other["y"] + other["height"])) <= 1):  # Close enough to rest

                return True  # Point is supported by another box

        return False  # No support found for this point

    def apply_torque(self, box, unsupported_points):
        """Apply rotational force based on unsupported points."""
        # Calculate torque magnitude and direction based on unsupported points
        torque_factor = (unsupported_points / box["bottom_points"]) * 0.05  # Adjust strength as needed
        box["angular_velocity_x"] += torque_factor
        box["angular_velocity_y"] += torque_factor

    def check_tipping(self, box):
        """Check if the box is tipping over based on its angles and reset if necessary."""
        tipping_threshold = 20  # degrees, adjust as needed
        if abs(box["angle_x"]) > tipping_threshold or abs(box["angle_y"]) > tipping_threshold:
            # Reset to prevent box from falling through ground and stop further rotation
            box["y"] = max(box["y"], 0)
            box["angular_velocity_x"] = 0
            box["angular_velocity_y"] = 0
            box["angle_x"] = 0
            box["angle_y"] = 0

    def handle_collision(self, box1, box2):
        """Handle collision between two boxes in 3D space."""
        if (box1["x"] < box2["x"] + box2["width"] and
            box1["x"] + box1["width"] > box2["x"] and
            box1["y"] < box2["y"] + box2["height"] and
            box1["y"] + box1["height"] > box2["y"] and
            box1["z"] < box2["z"] + box2["depth"] and
            box1["z"] + box1["depth"] > box2["z"]):

            # Calculate overlap in each dimension
            overlap_x = min(box1["x"] + box1["width"] - box2["x"], box2["x"] + box2["width"] - box1["x"])
            overlap_y = min(box1["y"] + box1["height"] - box2["y"], box2["y"] + box2["height"] - box1["y"])
            overlap_z = min(box1["z"] + box1["depth"] - box2["z"], box2["z"] + box2["depth"] - box1["z"])

            # Resolve collision by moving boxes along the smallest overlap dimension
            if overlap_x < overlap_y and overlap_x < overlap_z:
                if box1["x"] < box2["x"]:
                    box1["x"] = box2["x"] - box1["width"]
                else:
                    box1["x"] = box2["x"] + box2["width"]
                self.resolve_energy_loss(box1, box2, "xv")
            elif overlap_y < overlap_x and overlap_y < overlap_z:
                if box1["y"] < box2["y"]:
                    box1["y"] = box2["y"] - box1["height"]
                else:
                    box1["y"] = box2["y"] + box2["height"]
                self.resolve_energy_loss(box1, box2, "yv")
            else:
                if box1["z"] < box2["z"]:
                    box1["z"] = box2["z"] - box1["depth"]
                else:
                    box1["z"] = box2["z"] + box2["depth"]
                self.resolve_energy_loss(box1, box2, "zv")

    def resolve_energy_loss(self, box1, box2, velocity_axis):
        """Adjust velocities based on energy loss in a collision."""
        energy_loss = min(box1["energy"], 10)  # Energy loss on collision
        box1["energy"] -= energy_loss
        box2["energy"] -= energy_loss
        # Reverse and reduce velocity based on energy loss and drag
        box1[velocity_axis] = -box1[velocity_axis] * (1 - energy_loss / 100) / self.DRAG
        box2[velocity_axis] = -box2[velocity_axis] * (1 - energy_loss / 100) / self.DRAG
