import pygame
import random
import time
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
BG_COLOR = (15, 23, 42)       # כחול כהה
TARGET_COLOR = (239, 68, 68)   # אדום
CROSSHAIR_COLOR = (59, 130, 246) # כחול
TEXT_COLOR = (241, 245, 249)
SUCCESS_COLOR = (34, 197, 94)  # ירוק

class PrecisionLab:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PrecisionLab - Joystick Aim Trainer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)

        # בדיקת חיבור ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"ג'ויסטיק מחובר: {self.joystick.get_name()}")
        else:
            print("אזהרה: לא נמצא ג'ויסטיק מחובר! המשחק יעבוד עם העכבר לבדיקה.")

        # מיקום כוונת
        self.cross_x = SCREEN_WIDTH // 2
        self.cross_y = SCREEN_HEIGHT // 2
        self.speed = 8.0  # רגישות תנועת הכוונת

        # משתני משחק
        self.target_radius = 35
        self.target_x, self.target_y = self.spawn_target()
        
        self.hold_time_needed = 0.5  # כמה שניות צריך להחזיק על המטרה
        self.current_hold = 0.0
        
        self.score = 0
        self.total_targets = 0
        self.game_duration = 60.0  # זמן משחק בשניות
        self.start_time = time.time()
        self.is_over = False

        # מטריקות
        self.time_on_target = 0.0
        self.total_time = 0.0

    def spawn_target(self):
        margin = 80
        x = random.randint(margin, SCREEN_WIDTH - margin)
        y = random.randint(margin, SCREEN_HEIGHT - margin)
        return x, y

    def update_position(self, dt):
        if self.joystick:
            # קריאת הצירים של הג'ויסטיק (מוגבל בין -1.0 ל-1.0)
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)

            # Deadzone קטן למניעת סחיפה
            deadzone = 0.1
            if abs(axis_x) < deadzone: axis_x = 0
            if abs(axis_y) < deadzone: axis_y = 0

            self.cross_x += axis_x * self.speed
            self.cross_y += axis_y * self.speed
        else:
            # גיבוי - עכבר (למקרה והג'ויסטיק מנותק)
            self.cross_x, self.cross_y = pygame.mouse.get_pos()

        # הגבלת הכוונת לגבולות המסך
        self.cross_x = max(10, min(SCREEN_WIDTH - 10, self.cross_x))
        self.cross_y = max(10, min(SCREEN_HEIGHT - 10, self.cross_y))

    def check_hit(self, dt):
        dist = math.hypot(self.cross_x - self.target_x, self.cross_y - self.target_y)
        
        if dist <= self.target_radius:
            self.current_hold += dt
            self.time_on_target += dt
            if self.current_hold >= self.hold_time_needed:
                self.score += 1
                self.total_targets += 1
                self.current_hold = 0.0
                self.target_x, self.target_y = self.spawn_target()
        else:
            self.current_hold = max(0.0, self.current_hold - dt * 2) # יורד מהר כשיוצאים

    def draw_hud(self, elapsed_time):
        remaining_time = max(0.0, self.game_duration - elapsed_time)
        accuracy = (self.time_on_target / elapsed_time * 100) if elapsed_time > 0 else 0.0

        # לוח מדדים עליון
        hud_text = f"Score: {self.score}  |  Time: {remaining_time:.1f}s  |  Accuracy: {accuracy:.1f}%"
        txt_surface = self.font.render(hud_text, True, TEXT_COLOR)
        self.screen.blit(txt_surface, (20, 20))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # דלתא-טיים בשניות
            elapsed = time.time() - self.start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if not self.is_over:
                if elapsed >= self.game_duration:
                    self.is_over = True

                self.update_position(dt)
                self.check_hit(dt)

            # --- ציור המסך ---
            self.screen.fill(BG_COLOR)

            if not self.is_over:
                # 1. ציור המטרה
                pygame.draw.circle(self.screen, TARGET_COLOR, (int(self.target_x), int(self.target_y)), self.target_radius, 3)
                
                # טבעת התקדמות החזקה (Hold Progress)
                progress_angle = (self.current_hold / self.hold_time_needed) * 2 * math.pi
                if progress_angle > 0:
                    pygame.draw.circle(self.screen, SUCCESS_COLOR, (int(self.target_x), int(self.target_y)), int(self.target_radius * (self.current_hold / self.hold_time_needed)))

                # 2. ציור הכוונת (Crosshair)
                cx, cy = int(self.cross_x), int(self.cross_y)
                pygame.draw.line(self.screen, CROSSHAIR_COLOR, (cx - 15, cy), (cx + 15, cy), 2)
                pygame.draw.line(self.screen, CROSSHAIR_COLOR, (cx, cy - 15), (cx, cy + 15), 2)
                pygame.draw.circle(self.screen, CROSSHAIR_COLOR, (cx, cy), 4)

                # 3. HUD
                self.draw_hud(elapsed)
            else:
                # מסך סיכום
                final_acc = (self.time_on_target / self.game_duration * 100)
                over_txt = self.title_font.render("SESSION COMPLETE", True, SUCCESS_COLOR)
                stats_txt = self.font.render(f"Final Score: {self.score}  |  Precision Tracking: {final_acc:.1f}%", True, TEXT_COLOR)
                
                self.screen.blit(over_txt, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
                self.screen.blit(stats_txt, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 10))

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = PrecisionLab()
    game.run()