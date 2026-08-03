import pygame
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
SPACE_BG = (10, 15, 26)          # חלל עמוק
STATION_COLOR = (148, 163, 184)  # כסף מתכתי
DOCK_PORT_COLOR = (34, 197, 94)  # ירוק עגינה
SHIP_COLOR = (59, 130, 246)     # כחול חללית
THRUSTER_COLOR = (249, 115, 22)  # אש מנוע
TEXT_COLOR = (241, 245, 249)
ALERT_COLOR = (239, 68, 68)     # אדום אזהרה

class SpaceSimulator:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Docking Simulator - 6DOF RCS Control")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"ג'ויסטיק מחובר: {self.joystick.get_name()}")

        # פיזיקת חללית
        self.ship_x = 200.0
        self.ship_y = 350.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        
        self.ship_angle = 0.0     # זווית במעלות
        self.angular_vel = 0.0   # מהירות סיבוב
        
        self.main_thrust = 0.0
        self.rcs_active = False

        # תחנת חלל ופתח עגינה (Docking Port)
        self.station_x = 800
        self.station_y = 350
        self.dock_rect = pygame.Rect(self.station_x - 30, self.station_y - 25, 20, 50)

        # מצבי משחק
        self.docked = False
        self.crashed = False

    def handle_input(self):
        if self.docked or self.crashed:
            return

        thrust_power = 0.12
        rotation_power = 0.15
        self.rcs_active = False

        if self.joystick:
            axis_x = self.joystick.get_axis(0) # RCS ימינה/שמאלה
            axis_y = self.joystick.get_axis(1) # RCS למעלה/למטה

            deadzone = 0.1

            # תרגום דחף צידי (RCS translation)
            if abs(axis_x) > deadzone:
                self.vel_x += axis_x * thrust_power
                self.rcs_active = True
            if abs(axis_y) > deadzone:
                self.vel_y += axis_y * thrust_power
                self.rcs_active = True

            # Twist (ציר 2) - סיבוב החללית
            if self.joystick.get_numaxes() > 2:
                twist = self.joystick.get_axis(2)
                if abs(twist) > deadzone:
                    self.angular_vel += twist * rotation_power
                    self.rcs_active = True

            # Throttle (ציר 3) - מנוע ראשי קדימה
            if self.joystick.get_numaxes() > 3:
                throttle = self.joystick.get_axis(3)
                # המרה מ-[-1, 1] לדחף חיובי
                self.main_thrust = max(0.0, (1.0 - throttle) / 2.0)
                if self.main_thrust > 0.05:
                    rad = math.radians(self.ship_angle)
                    self.vel_x += math.cos(rad) * self.main_thrust * 0.2
                    self.vel_y += math.sin(rad) * self.main_thrust * 0.2

            # הדק (Button 0) - בולמי חירום / איפוס סיבוב
            if self.joystick.get_button(0):
                self.angular_vel *= 0.85
                self.vel_x *= 0.92
                self.vel_y *= 0.92

        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: self.angular_vel -= rotation_power
            if keys[pygame.K_RIGHT]: self.angular_vel += rotation_power
            if keys[pygame.K_UP]:
                rad = math.radians(self.ship_angle)
                self.vel_x += math.cos(rad) * thrust_power * 1.5
                self.vel_y += math.sin(rad) * thrust_power * 1.5
                self.rcs_active = True
            if keys[pygame.K_SPACE]: # בולמי חירום
                self.angular_vel *= 0.85
                self.vel_x *= 0.92
                self.vel_y *= 0.92

    def update_physics(self):
        if self.docked or self.crashed:
            return

        # עדכון מיקום וזווית (ללא חיכוך!)
        self.ship_x += self.vel_x
        self.ship_y += self.vel_y
        self.ship_angle += self.angular_vel

        # נורמליזציה של הזווית בין 0 ל-360
        self.ship_angle %= 360

        # בדיקת התנגשות בעגינה
        ship_rect = pygame.Rect(self.ship_x - 15, self.ship_y - 15, 30, 30)
        
        if ship_rect.colliderect(self.dock_rect):
            speed = math.hypot(self.vel_x, self.vel_y)
            angle_diff = abs(self.ship_angle - 0) # צריך להיות מופנה ימינה (0 מעלות)

            # תנאי עגינה מוצלחת: מהירות נמוכה + זווית ישרה
            if speed < 1.5 and (angle_diff < 15 or angle_diff > 345):
                self.docked = True
                self.vel_x = 0
                self.vel_y = 0
                self.angular_vel = 0
            else:
                self.crashed = True

        # התרסקות בקירות המסך
        if not (0 <= self.ship_x <= SCREEN_WIDTH and 0 <= self.ship_y <= SCREEN_HEIGHT):
            self.crashed = True

    def draw(self):
        self.screen.fill(SPACE_BG)

        # 1. ציור תחנת החלל
        # גוף התחנה
        pygame.draw.circle(self.screen, STATION_COLOR, (self.station_x + 50, self.station_y), 60)
        pygame.draw.rect(self.screen, (51, 65, 85), (self.station_x + 30, self.station_y - 120, 40, 240)) # פאנלים סולאריים
        
        # פתח עגינה (Docking Port)
        pygame.draw.rect(self.screen, DOCK_PORT_COLOR, self.dock_rect, 3)

        # 2. ציור החללית (משולש מסובב)
        ship_surface = pygame.Surface((34, 24), pygame.SRCALPHA)
        
        # גוף החללית
        points = [(30, 12), (0, 0), (8, 12), (0, 24)]
        pygame.draw.polygon(ship_surface, SHIP_COLOR, points)
        
        # אש מנוע (אם מופעל)
        if self.rcs_active or self.main_thrust > 0.05:
            pygame.draw.polygon(ship_surface, THRUSTER_COLOR, [(0, 6), (-10, 12), (0, 18)])

        rotated_ship = pygame.transform.rotate(ship_surface, -self.ship_angle)
        ship_rect = rotated_ship.get_rect(center=(int(self.ship_x), int(self.ship_y)))
        self.screen.blit(rotated_ship, ship_rect.topleft)

        # 3. מדדים וטלמטריה (HUD)
        speed = math.hypot(self.vel_x, self.vel_y)
        
        speed_color = DOCK_PORT_COLOR if speed < 1.5 else ALERT_COLOR
        hud_speed = self.font.render(f"Relative Speed: {speed:.2f} m/s", True, speed_color)
        hud_angle = self.font.render(f"Approach Angle: {self.ship_angle:.1f}°", True, TEXT_COLOR)
        hud_rcs = self.font.render(f"RCS Status: {'ACTIVE' if self.rcs_active else 'STANDBY'}", True, TEXT_COLOR)

        self.screen.blit(hud_speed, (20, 20))
        self.screen.blit(hud_angle, (20, 50))
        self.screen.blit(hud_rcs, (20, 80))

        # 4. הודעות סיום
        if self.docked:
            win_txt = self.title_font.render("DOCKING SUCCESSFUL!", True, DOCK_PORT_COLOR)
            self.screen.blit(win_txt, (SCREEN_WIDTH // 2 - 180, 80))
        elif self.crashed:
            fail_txt = self.title_font.render("CRASH DETECTED! DOCKING FAILED", True, ALERT_COLOR)
            self.screen.blit(fail_txt, (SCREEN_WIDTH // 2 - 250, 80))

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
    game = SpaceSimulator()
    game.run()