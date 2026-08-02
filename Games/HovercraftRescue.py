import pygame
import math
import random

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
WATER_COLOR = (15, 23, 42)         # מים כהים (לילה)
HOVER_COLOR = (245, 158, 11)       # כתום חילוץ
SPOTLIGHT_COLOR = (254, 240, 138)  # צהוב אור
SURVIVOR_COLOR = (239, 68, 68)     # אדום ניצול
BASE_COLOR = (34, 197, 94)         # ירוק בסיס בטוח
TEXT_COLOR = (241, 245, 249)

class Survivor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rescued = False

class HovercraftRescue:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hovercraft Rescue - Night Search")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"ג'ויסטיק מחובר: {self.joystick.get_name()}")

        # פיזיקת רחפת
        self.x = 150.0
        self.y = 150.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.heading_angle = 0.0   # כיוון החרטום (מעלות)
        self.spotlight_angle = 0.0 # זווית הזרקור ביחס לחרטום (מעלות)
        
        self.thrust = 0.0
        self.max_speed = 7.0
        self.drag = 0.985          # חיכוך מים נמוך מאוד (החלקה)

        # ניצולים ובסיס
        self.survivors = [Survivor(random.randint(300, 900), random.randint(100, 600)) for _ in range(6)]
        self.onboard_survivors = 0
        self.saved_survivors = 0
        self.base_rect = pygame.Rect(50, 50, 120, 120)

    def handle_input(self):
        turn_speed = 3.5
        thrust_accel = 0.15

        if self.joystick:
            axis_x = self.joystick.get_axis(0) # פנייה
            axis_y = self.joystick.get_axis(1) # דחף קדימה/אחורה

            deadzone = 0.1
            if abs(axis_x) > deadzone:
                self.heading_angle += axis_x * turn_speed
            
            if abs(axis_y) > deadzone:
                # דחיפה קדימה (axis_y שלילי ב-Pygame)
                forward_thrust = -axis_y
                rad = math.radians(self.heading_angle)
                self.vel_x += math.cos(rad) * forward_thrust * thrust_accel
                self.vel_y += math.sin(rad) * forward_thrust * thrust_accel

            # Twist (ציר 2) - כיוון הזרקור באופן עצמאי!
            if self.joystick.get_numaxes() > 2:
                twist = self.joystick.get_axis(2)
                if abs(twist) > deadzone:
                    self.spotlight_angle += twist * 4.0

        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: self.heading_angle -= turn_speed
            if keys[pygame.K_RIGHT]: self.heading_angle += turn_speed
            if keys[pygame.K_UP]:
                rad = math.radians(self.heading_angle)
                self.vel_x += math.cos(rad) * thrust_accel
                self.vel_y += math.sin(rad) * thrust_accel

            if keys[pygame.K_a]: self.spotlight_angle -= 4.0
            if keys[pygame.K_d]: self.spotlight_angle += 4.0

    def update_physics(self):
        # תנועה וחיכוך
        self.x += self.vel_x
        self.y += self.vel_y
        
        self.vel_x *= self.drag
        self.vel_y *= self.drag

        # גבולות מסך
        self.x = max(20, min(SCREEN_WIDTH - 20, self.x))
        self.y = max(20, min(SCREEN_HEIGHT - 20, self.y))

        # בדיקת איסוף ניצולים
        hover_rect = pygame.Rect(self.x - 20, self.y - 20, 40, 40)
        for s in self.survivors:
            if not s.rescued and hover_rect.collidepoint(s.x, s.y):
                if self.onboard_survivors < 3: # מקסימום 3 ברחפת בבת אחת
                    s.rescued = True
                    self.onboard_survivors += 1

        # הורדת ניצולים בבסיס
        if hover_rect.colliderect(self.base_rect) and self.onboard_survivors > 0:
            self.saved_survivors += self.onboard_survivors
            self.onboard_survivors = 0

    def draw(self):
        self.screen.fill(WATER_COLOR)

        # 1. ציור הבסיס (Safety Zone)
        pygame.draw.rect(self.screen, BASE_COLOR, self.base_rect, 3)
        base_txt = self.font.render("BASE", True, BASE_COLOR)
        self.screen.blit(base_txt, (self.base_rect.x + 35, self.base_rect.y + 45))

        # 2. ציור הזרקור (Spotlight Cone)
        total_spotlight_deg = self.heading_angle + self.spotlight_angle
        spot_rad = math.radians(total_spotlight_deg)
        
        cone_length = 250
        cone_width = 0.35 # רדיאנים (זווית פיזור)
        
        p1 = (self.x, self.y)
        p2 = (self.x + math.cos(spot_rad - cone_width) * cone_length, self.y + math.sin(spot_rad - cone_width) * cone_length)
        p3 = (self.x + math.cos(spot_rad + cone_width) * cone_length, self.y + math.sin(spot_rad + cone_width) * cone_length)

        # משטח שקוף לאור הזרקור
        spot_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(spot_surface, (254, 240, 138, 60), [p1, p2, p3])
        self.screen.blit(spot_surface, (0, 0))

        # 3. ציור ניצולים במים (נחשפים כשהם באור או קרובים)
        for s in self.survivors:
            if not s.rescued:
                # בדיקה אם הניצול בתוך הזרקור
                dist = math.hypot(s.x - self.x, s.y - self.y)
                angle_to_s = math.degrees(math.atan2(s.y - self.y, s.x - self.x))
                angle_diff = (angle_to_s - total_spotlight_deg + 180) % 360 - 180

                # ציור רק אם קרוב או בתוך אלומת האור
                if dist < 80 or (dist < cone_length and abs(angle_diff) < 22):
                    pygame.draw.circle(self.screen, SURVIVOR_COLOR, (int(s.x), int(s.y)), 6)
                    pygame.draw.circle(self.screen, (255, 255, 255), (int(s.x), int(s.y)), 8, 1)

        # 4. ציור הרחפת
        hover_surface = pygame.Surface((40, 26), pygame.SRCALPHA)
        # כרית אוויר / גוף
        pygame.draw.ellipse(hover_surface, (30, 41, 59), (0, 0, 40, 26))
        pygame.draw.ellipse(hover_surface, HOVER_COLOR, (4, 3, 32, 20))
        # מנוע אחורי
        pygame.draw.rect(hover_surface, (15, 23, 42), (0, 8, 8, 10))

        rotated_hover = pygame.transform.rotate(hover_surface, -self.heading_angle)
        rect = rotated_hover.get_rect(center=(int(self.x), int(self.y)))
        self.screen.blit(rotated_hover, rect.topleft)

        # 5. מדדים (HUD)
        hud_onboard = self.font.render(f"Onboard: {self.onboard_survivors}/3", True, TEXT_COLOR)
        hud_saved = self.font.render(f"Saved: {self.saved_survivors}/{len(self.survivors)}", True, BASE_COLOR)
        
        self.screen.blit(hud_onboard, (20, SCREEN_HEIGHT - 60))
        self.screen.blit(hud_saved, (20, SCREEN_HEIGHT - 35))

        if self.saved_survivors == len(self.survivors):
            win_txt = self.title_font.render("ALL SURVIVORS RESCUED!", True, BASE_COLOR)
            self.screen.blit(win_txt, (SCREEN_WIDTH // 2 - 200, 50))

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
    game = HovercraftRescue()
    game.run()