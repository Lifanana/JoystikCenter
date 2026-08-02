import pygame
import math

# --- הגדרות קבועות ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# צבעים
BG_COLOR = (15, 23, 42)         # אפור-כחול כהה
TEXT_COLOR = (241, 245, 249)

class DrawAndTilt:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Draw & Tilt - 3D Joystick Canvas")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)

        # בדיקת ג'ויסטיק
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"ג'ויסטיק מחובר: {self.joystick.get_name()}")

        # מיקום המברשת
        self.brush_x = SCREEN_WIDTH // 2
        self.brush_y = SCREEN_HEIGHT // 2
        self.brush_z = 0.0  # עומק
        
        self.brush_size = 8.0
        self.brush_color = [59, 130, 246]  # כחול התחלתי
        
        # רשימת נקודות שצויירו: [(x, y, z, color, size)]
        self.strokes = []

        # מצבי שליטה
        self.is_drawing = False
        self.tilt_mode = False
        self.rotation_x = 0.0
        self.rotation_y = 0.0

    def handle_input(self):
        speed = 7.0

        if self.joystick:
            # צירי תנועה X, Y
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)

            deadzone = 0.08
            if not self.tilt_mode:
                if abs(axis_x) > deadzone: self.brush_x += axis_x * speed
                if abs(axis_y) > deadzone: self.brush_y += axis_y * speed
            else:
                # במצב Tilt, הסטיק מסובב את הציור במרחב
                if abs(axis_x) > deadzone: self.rotation_y += axis_x * 0.04
                if abs(axis_y) > deadzone: self.rotation_x += axis_y * 0.04

            # Twist (אם קיים - ציר 2) לעומק Z
            if self.joystick.get_numaxes() > 2:
                twist = self.joystick.get_axis(2)
                if abs(twist) > deadzone:
                    self.brush_z += twist * 2.0

            # Throttle (אם קיים - ציר 3) לגודל מברשת
            if self.joystick.get_numaxes() > 3:
                throttle = self.joystick.get_axis(3)
                # נורמליזציה מ-[-1, 1] ל-[3, 25]
                self.brush_size = max(2.0, ((1.0 - throttle) / 2.0) * 25.0 + 3.0)

            # הדק לציור (Button 0)
            self.is_drawing = self.joystick.get_button(0)

            # כפתור 1 להחלפת צבעים
            if self.joystick.get_button(1):
                self.cycle_color()

        else:
            # גיבוי מקלדת
            keys = pygame.key.get_pressed()
            if not self.tilt_mode:
                if keys[pygame.K_LEFT]: self.brush_x -= speed
                if keys[pygame.K_RIGHT]: self.brush_x += speed
                if keys[pygame.K_UP]: self.brush_y -= speed
                if keys[pygame.K_DOWN]: self.brush_y += speed
            else:
                if keys[pygame.K_LEFT]: self.rotation_y -= 0.04
                if keys[pygame.K_RIGHT]: self.rotation_y += 0.04
                if keys[pygame.K_UP]: self.rotation_x -= 0.04
                if keys[pygame.K_DOWN]: self.rotation_x += 0.04

            if keys[pygame.K_w]: self.brush_z += 2.0
            if keys[pygame.K_s]: self.brush_z -= 2.0

            self.is_drawing = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]

        # הגבלת מברשת לגבולות
        self.brush_x = max(20, min(SCREEN_WIDTH - 20, self.brush_x))
        self.brush_y = max(20, min(SCREEN_HEIGHT - 20, self.brush_y))

    def cycle_color(self):
        # שינוי גוון דינמי
        self.brush_color[0] = (self.brush_color[0] + 5) % 255
        self.brush_color[1] = (self.brush_color[1] + 3) % 255
        self.brush_color[2] = (self.brush_color[2] + 8) % 255

    def update(self):
        if self.is_drawing and not self.tilt_mode:
            # הוספת נקודה למסלול הציור
            self.strokes.append((
                self.brush_x - SCREEN_WIDTH // 2, 
                self.brush_y - SCREEN_HEIGHT // 2, 
                self.brush_z, 
                tuple(self.brush_color), 
                self.brush_size
            ))

    def project_3d(self, x, y, z):
        # רוטציה תלת-ממדית בסיסית (3D Projection)
        rad_x = self.rotation_x
        rad_y = self.rotation_y

        # סיבוב סביב Y
        xz = x * math.cos(rad_y) + z * math.sin(rad_y)
        yz = y
        zz = -x * math.sin(rad_y) + z * math.cos(rad_y)

        # סיבוב סביב X
        final_x = xz
        final_y = yz * math.cos(rad_x) - zz * math.sin(rad_x)
        final_z = yz * math.sin(rad_x) + zz * math.cos(rad_x)

        # המרה חזרה לקואורדינטות מסך
        screen_x = int(final_x + SCREEN_WIDTH // 2)
        screen_y = int(final_y + SCREEN_HEIGHT // 2)
        
        # סקיילינג לפי עומק Z
        scale = max(0.2, 1.0 + (final_z / 400.0))

        return screen_x, screen_y, scale

    def draw(self):
        self.screen.fill(BG_COLOR)

        # 1. ציור כל הנקודות ששורטטו
        for p in self.strokes:
            px, py, pz, color, size = p
            sx, sy, scale = self.project_3d(px, py, pz)
            
            draw_size = max(1, int(size * scale))
            pygame.draw.circle(self.screen, color, (sx, sy), draw_size)

        # 2. ציור הכוונת/מברשת
        if not self.tilt_mode:
            bx, by, bscale = self.project_3d(
                self.brush_x - SCREEN_WIDTH // 2, 
                self.brush_y - SCREEN_HEIGHT // 2, 
                self.brush_z
            )
            current_size = max(2, int(self.brush_size * bscale))
            
            # טבעת מברשת חיצונית
            pygame.draw.circle(self.screen, self.brush_color, (bx, by), current_size, 2)
            pygame.draw.circle(self.screen, (241, 245, 249), (bx, by), 3)

        # 3. HUD והוראות
        mode_str = "TILT 3D MODE (Rotate Canvas)" if self.tilt_mode else "DRAWING MODE"
        hud_text = f"Mode: {mode_str}  |  Strokes: {len(self.strokes)}  |  Brush Size: {int(self.brush_size)}"
        controls_txt = "Trigger: Draw | SPACE: Toggle Tilt 3D | C: Clear Canvas | Stick: Move/Rotate"
        
        self.screen.blit(self.font.render(hud_text, True, TEXT_COLOR), (20, 20))
        self.screen.blit(self.font.render(controls_txt, True, (148, 163, 184)), (20, 50))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.tilt_mode = not self.tilt_mode
                    elif event.key == pygame.K_c:
                        self.strokes.clear()  # ניקוי מסך

            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = DrawAndTilt()
    game.run()