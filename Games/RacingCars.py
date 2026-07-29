import pygame
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
GRASS_COLOR = (34, 197, 94)      # ירוק דשא
TRACK_COLOR = (71, 85, 105)      # אספלט
BORDER_COLOR = (241, 245, 249)    # שולי המסלול
CAR_COLOR = (239, 68, 68)        # אדום ספורט
TEXT_COLOR = (241, 245, 249)

class RacingGame:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Joystick Racing Challenge")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"✅ Connected Succesfully to {self.joystick.get_name()}")

        # פיזיקה ומיקום של המכונית
        self.car_x = 500.0
        self.car_y = 600.0
        self.car_angle = 0.0      # זווית הפנייה במעלות (0 = ימינה)
        self.speed = 0.0
        self.max_speed = 9.0
        self.acceleration = 0.18
        self.friction = 0.97
        self.turn_speed = 3.5

        # הגדרת המסלול (נקודות ליצירת מסלול מורכב)
        self.track_inner = [
            (250, 200), (750, 200), (800, 300), (750, 500), 
            (500, 450), (350, 500), (200, 400)
        ]
        self.track_outer = [
            (150, 100), (850, 100), (950, 300), (850, 600), 
            (500, 550), (300, 600), (100, 400)
        ]

        # הילוכים / דלתא
        self.laps = 0
        self.checkpoint_passed = False

    def handle_input(self):
        steering = 0.0
        throttle = 0.0

        if self.joystick:
            # ציר X = ההגה
            axis_x = self.joystick.get_axis(0)
            # ציר Y = גז/ברקס (הפוך: למעלה/דחיפה קדימה זה שלילי ב-Pygame)
            axis_y = self.joystick.get_axis(1)

            deadzone = 0.1
            if abs(axis_x) > deadzone:
                steering = axis_x
            if abs(axis_y) > deadzone:
                throttle = -axis_y  # היפוך ציר Y של פייתון
        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: steering = -1.0
            if keys[pygame.K_RIGHT]: steering = 1.0
            if keys[pygame.K_UP]: throttle = 1.0
            if keys[pygame.K_DOWN]: throttle = -0.5

        # עדכון זווית ומהירות
        if abs(self.speed) > 0.2:
            # סיבוב משפיע רק כשהמכונית בתנועה
            direction = 1 if self.speed >= 0 else -1
            self.car_angle += steering * self.turn_speed * direction

        if throttle > 0:
            self.speed = min(self.max_speed, self.speed + throttle * self.acceleration)
        elif throttle < 0:
            self.speed = max(-self.max_speed / 2, self.speed + throttle * self.acceleration)
        else:
            self.speed *= self.friction

    def update_physics(self):
        # חישוב תנועה לפי זווית המכונית
        rad = math.radians(self.car_angle)
        self.car_x += math.cos(rad) * self.speed
        self.car_y += math.sin(rad) * self.speed

        # בדיקת צ'קפוינט והקפות (קו סיום ב-(500, 550)-(500, 600))
        if 480 < self.car_x < 520 and 500 < self.car_y < 620:
            if self.checkpoint_passed:
                self.laps += 1
                self.checkpoint_passed = False
        elif 480 < self.car_x < 520 and 100 < self.car_y < 200:
            self.checkpoint_passed = True

    def draw(self):
        # 1. דשא (רקע)
        self.screen.fill(GRASS_COLOR)

        # 2. ציור המסלול (פוליגונים חיצוני ופנימי)
        pygame.draw.polygon(self.screen, TRACK_COLOR, self.track_outer)
        pygame.draw.polygon(self.screen, BORDER_COLOR, self.track_outer, 4)
        
        # השטח הפנימי (החור של המסלול)
        pygame.draw.polygon(self.screen, GRASS_COLOR, self.track_inner)
        pygame.draw.polygon(self.screen, BORDER_COLOR, self.track_inner, 4)

        # 3. קו זינוק / סיום
        pygame.draw.line(self.screen, BORDER_COLOR, (500, 550), (500, 600), 5)

        # 4. ציור המכונית (מלבן מסובב)
        car_surface = pygame.Surface((30, 16), pygame.SRCALPHA)
        car_surface.fill(CAR_COLOR)
        # גלגלים/פנסים קטנים
        pygame.draw.rect(car_surface, (15, 23, 42), (22, 2, 6, 12)) # שרמשה קדמית

        rotated_car = pygame.transform.rotate(car_surface, -self.car_angle)
        new_rect = rotated_car.get_rect(center=(int(self.car_x), int(self.car_y)))
        self.screen.blit(rotated_car, new_rect.topleft)

        # 5. HUD ונתונים
        speed_kmh = int(abs(self.speed) * 18)
        hud_txt = f"Speed: {speed_kmh} KM/H  |  Laps Completed: {self.laps}"
        self.screen.blit(self.font.render(hud_txt, True, TEXT_COLOR), (20, 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input()
            self.update_physics()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = RacingGame()
    game.run()