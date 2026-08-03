import pygame
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
BG_COLOR = (24, 24, 27)         # אפור כהה
ARM_COLOR = (234, 179, 8)       # צהוב תעשייתי
JOINT_COLOR = (71, 85, 105)     # אפור מתכתי
BOX_COLOR = (239, 68, 68)       # אדום
DROP_ZONE_COLOR = (34, 197, 94)  # ירוק
TEXT_COLOR = (241, 245, 249)

class RoboticArmGame:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("RoboticArm - Joystick Cargo Control")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        print(f"✅Connected Succesfully to {self.joystick.get_name()}")

        # פרמטרים של הזרוע הרובוטית
        self.base_x = SCREEN_WIDTH // 2
        self.base_y = SCREEN_HEIGHT - 100
        self.length1 = 180  # אורך זרוע ראשונה
        self.length2 = 150  # אורך זרוע שנייה

        # זוויות מפרקים (ברדיאנים)
        self.angle1 = -math.pi / 3  # כתף
        self.angle2 = math.pi / 4   # מרפק

        # מצב תפסן (Gripper)
        self.is_holding = False
        self.gripper_open = True

        # קופסה והיעד
        self.box_size = 35
        self.box_x = 200
        self.box_y = SCREEN_HEIGHT - 120
        self.drop_zone = pygame.Rect(750, SCREEN_HEIGHT - 130, 100, 40)
        self.score = 0

    def get_joint_positions(self):
        # חישוב מיקום מפרק 1 (מרפק)
        elbow_x = self.base_x + self.length1 * math.cos(self.angle1)
        elbow_y = self.base_y + self.length1 * math.sin(self.angle1)

        # חישוב מיקום קצה הזרוע (תפסן)
        hand_x = elbow_x + self.length2 * math.cos(self.angle1 + self.angle2)
        hand_y = elbow_y + self.length2 * math.sin(self.angle1 + self.angle2)

        return (elbow_x, elbow_y), (hand_x, hand_y)

    def handle_input(self):
        speed = 0.03
        
        if self.joystick:
            # ציר X שולט בזווית הכתף, ציר Y שולט בזווית המרפק
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)

            deadzone = 0.1
            if abs(axis_x) > deadzone:
                self.angle1 += axis_x * speed
            if abs(axis_y) > deadzone:
                self.angle2 += axis_y * speed

            # כפתור הדק (Button 0) לפתיחה/סגירה של התפסן
            button_trigger = self.joystick.get_button(0)
            self.gripper_open = not button_trigger
        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: self.angle1 -= speed
            if keys[pygame.K_RIGHT]: self.angle1 += speed
            if keys[pygame.K_UP]: self.angle2 -= speed
            if keys[pygame.K_DOWN]: self.angle2 += speed
            self.gripper_open = not keys[pygame.K_SPACE]

        # הגבלת זוויות למניעת תנועה לא טבעית
        self.angle1 = max(-math.pi + 0.2, min(-0.1, self.angle1))
        self.angle2 = max(-math.pi / 1.2, min(math.pi / 1.2, self.angle2))

    def update_logic(self):
        _, (hand_x, hand_y) = self.get_joint_positions()

        # מרחק מהקופסה לתפסן
        dist_to_box = math.hypot(hand_x - self.box_x, hand_y - self.box_y)

        # לוגיקת תפיסה
        if not self.gripper_open and dist_to_box < 40 and not self.is_holding:
            self.is_holding = True

        if self.gripper_open and self.is_holding:
            self.is_holding = False
            # בדיקת פריקה באזור היעד
            if self.drop_zone.collidepoint(self.box_x, self.box_y):
                self.score += 1
                # איפוס מיקום הקופסה
                self.box_x = 200
                self.box_y = SCREEN_HEIGHT - 120

        # אם תפוס - הקופסה זזה עם התפסן
        if self.is_holding:
            self.box_x = hand_x
            self.box_y = hand_y
        else:
            # נפילת קופסה בגרביטציה לרצפה
            floor_level = SCREEN_HEIGHT - 120
            if self.box_y < floor_level:
                self.box_y += 5

    def draw(self):
        self.screen.fill(BG_COLOR)

        # 1. משטח/רצפה
        pygame.draw.rect(self.screen, (51, 65, 85), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))

        # 2. אזור היעד (Drop Zone)
        pygame.draw.rect(self.screen, DROP_ZONE_COLOR, self.drop_zone, 3)
        target_txt = self.font.render("DROP ZONE", True, DROP_ZONE_COLOR)
        self.screen.blit(target_txt, (self.drop_zone.x + 5, self.drop_zone.y - 30))

        # 3. בסיס הרובוט
        pygame.draw.rect(self.screen, JOINT_COLOR, (self.base_x - 40, self.base_y, 80, 40))

        # 4. חישוב וציור זרועות
        (elbow_x, elbow_y), (hand_x, hand_y) = self.get_joint_positions()

        # זרוע 1
        pygame.draw.line(self.screen, ARM_COLOR, (self.base_x, self.base_y), (elbow_x, elbow_y), 14)
        # זרוע 2
        pygame.draw.line(self.screen, ARM_COLOR, (elbow_x, elbow_y), (hand_x, hand_y), 10)

        # מפרקים
        pygame.draw.circle(self.screen, JOINT_COLOR, (self.base_x, self.base_y), 12)
        pygame.draw.circle(self.screen, JOINT_COLOR, (int(elbow_x), int(elbow_y)), 10)

        # 5. תפסן (Gripper)
        grip_gap = 20 if self.gripper_open else 8
        pygame.draw.circle(self.screen, (220, 38, 38), (int(hand_x), int(hand_y)), 6)
        pygame.draw.line(self.screen, TEXT_COLOR, (hand_x - grip_gap, hand_y + 10), (hand_x, hand_y), 4)
        pygame.draw.line(self.screen, TEXT_COLOR, (hand_x + grip_gap, hand_y + 10), (hand_x, hand_y), 4)

        # 6. הקופסה
        box_rect = pygame.Rect(self.box_x - self.box_size // 2, self.box_y - self.box_size // 2, self.box_size, self.box_size)
        pygame.draw.rect(self.screen, BOX_COLOR, box_rect, border_radius=4)

        # 7. טקסט ו-HUD
        status_grip = "OPEN" if self.gripper_open else "CLOSED (GRIPPING)"
        info_txt = f"Delivered Cargo: {self.score}  |  Gripper: {status_grip}"
        controls_txt = "Controls: Stick X (Shoulder) | Stick Y (Elbow) | Trigger (Grip)"
        
        self.screen.blit(self.font.render(info_txt, True, TEXT_COLOR), (20, 20))
        self.screen.blit(self.font.render(controls_txt, True, (148, 163, 184)), (20, 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.handle_input()
            self.update_logic()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = RoboticArmGame()
    game.run()