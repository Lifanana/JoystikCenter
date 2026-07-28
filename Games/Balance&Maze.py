import pygame
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
BG_COLOR = (15, 23, 42)         # כחול-כהה עמוק
BOARD_COLOR = (30, 41, 59)      # משטח המבוך
WALL_COLOR = (148, 163, 184)    # קירות
BALL_COLOR = (59, 130, 246)     # כדור
GOAL_COLOR = (34, 197, 94)      # יעד ירוק
TEXT_COLOR = (241, 245, 249)

class BalanceMazeGame:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Balance & Maze - Joystick Tilt Control")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"ג'ויסטיק מחובר: {self.joystick.get_name()}")

        # משתני הטיה של המשטח (Inclinometer)
        self.tilt_x = 0.0  # הטיה ימינה/שמאלה
        self.tilt_y = 0.0  # הטיה למעלה/למטה

        # מיקום ופיזיקה של הכדור
        self.ball_radius = 12
        self.ball_x = 180.0
        self.ball_y = 180.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.friction = 0.98  # חיכוך משטח

        # גבולות המשטח (Tilt Board)
        self.board_rect = pygame.Rect(120, 100, 760, 500)

        # יצירת הקירות של המבוך (Rectangles)
        self.walls = [
            # קירות חיצוניים (פנימיים ללוח)
            pygame.Rect(120, 100, 760, 15),
            pygame.Rect(120, 585, 760, 15),
            pygame.Rect(120, 100, 15, 500),
            pygame.Rect(865, 100, 15, 500),
            
            # קירות פנימיים ליצירת מסלול מבוך
            pygame.Rect(250, 100, 15, 350),
            pygame.Rect(380, 230, 15, 370),
            pygame.Rect(510, 100, 15, 350),
            pygame.Rect(640, 230, 15, 370),
            pygame.Rect(750, 100, 15, 350)
        ]

        # היעד (Goal)
        self.goal = pygame.Rect(780, 480, 70, 70)
        self.won = False

    def handle_input(self):
        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)

            deadzone = 0.08
            self.tilt_x = axis_x if abs(axis_x) > deadzone else 0.0
            self.tilt_y = axis_y if abs(axis_y) > deadzone else 0.0
        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            self.tilt_x = (1.0 if keys[pygame.K_RIGHT] else 0.0) - (1.0 if keys[pygame.K_LEFT] else 0.0)
            self.tilt_y = (1.0 if keys[pygame.K_DOWN] else 0.0) - (1.0 if keys[pygame.K_UP] else 0.0)

    def update_physics(self):
        if self.won:
            return

        # תאוצה נגזרת מתזוזת/הטית הג'ויסטיק
        gravity_mult = 0.45
        accel_x = self.tilt_x * gravity_mult
        accel_y = self.tilt_y * gravity_mult

        # עדכון מהירות
        self.vel_x += accel_x
        self.vel_y += accel_y

        # איבוד אנרגיה מחיכוך
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # ניסיון תנועה בציר X + התנגשות בקירות
        self.ball_x += self.vel_x
        ball_rect_x = pygame.Rect(int(self.ball_x - self.ball_radius), int(self.ball_y - self.ball_radius), 
                                 self.ball_radius * 2, self.ball_radius * 2)
        for wall in self.walls:
            if ball_rect_x.colliderect(wall):
                if self.vel_x > 0:
                    self.ball_x = wall.left - self.ball_radius
                elif self.vel_x < 0:
                    self.ball_x = wall.right + self.ball_radius
                self.vel_x = -self.vel_x * 0.4  # ניתור קל במכה

        # ניסיון תנועה בציר Y + התנגשות בקירות
        self.ball_y += self.vel_y
        ball_rect_y = pygame.Rect(int(self.ball_x - self.ball_radius), int(self.ball_y - self.ball_radius), 
                                 self.ball_radius * 2, self.ball_radius * 2)
        for wall in self.walls:
            if ball_rect_y.colliderect(wall):
                if self.vel_y > 0:
                    self.ball_y = wall.top - self.ball_radius
                elif self.vel_y < 0:
                    self.ball_y = wall.bottom + self.ball_radius
                self.vel_y = -self.vel_y * 0.4  # ניתור קל במכה

        # בדיקת הגעה ליעד
        ball_point = (int(self.ball_x), int(self.ball_y))
        if self.goal.collidepoint(ball_point):
            self.won = True

    def draw(self):
        self.screen.fill(BG_COLOR)

        # 1. משטח המבוך
        pygame.draw.rect(self.screen, BOARD_COLOR, self.board_rect, border_radius=8)

        # 2. אזור הסיום (Goal)
        pygame.draw.rect(self.screen, GOAL_COLOR, self.goal, border_radius=6)
        goal_text = self.font.render("FINISH", True, BG_COLOR)
        self.screen.blit(goal_text, (self.goal.x + 5, self.goal.y + 20))

        # 3. קירות המבוך
        for wall in self.walls:
            pygame.draw.rect(self.screen, WALL_COLOR, wall, border_radius=2)

        # 4. הכדור
        pygame.draw.circle(self.screen, BALL_COLOR, (int(self.ball_x), int(self.ball_y)), self.ball_radius)
        # אפקט ברק/תלת-ממד קטן על הכדור
        pygame.draw.circle(self.screen, (147, 197, 253), (int(self.ball_x - 3), int(self.ball_y - 3)), 4)

        # 5. מד הטיות HUD
        tilt_str = f"Board Tilt -> X: {self.tilt_x * 100:.0f}% | Y: {self.tilt_y * 100:.0f}%"
        self.screen.blit(self.font.render(tilt_str, True, TEXT_COLOR), (20, 20))

        if self.won:
            win_txt = self.font.render("MAZE CLEARED! PERFECT BALANCE!", True, GOAL_COLOR)
            self.screen.blit(win_txt, (SCREEN_WIDTH // 2 - 180, 50))

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
    game = BalanceMazeGame()
    game.run()