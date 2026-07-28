import sys
import math
import pygame

# 1. אתחול Pygame וה-Joystick
pygame.init()
pygame.joystick.init()

# בדיקה אם מחובר ג'ויסטיק
if pygame.joystick.get_count() == 0:
    print("❌ Connected Joystick not found,Try Again")
    pygame.quit()
    sys.exit()

# חיבור ל-Joystick הראשון
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"✅ Connected Succesfully to {joystick.get_name()}")

# הגדרות חלון המשחק
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("JoysticGames - Flight Simulator 🛩️")
clock = pygame.time.Clock()

# צבעים
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (20, 40, 80)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GOLD = (255, 215, 0)

# נתוני המטוס
plane_x = WIDTH // 2
plane_y = HEIGHT // 2
pitch = 0  # הטיות מעלה/מטה
roll = 0   # הטיות ימינה/שמאלה
speed = 5  # מהירות טיסה
altitude = 1000  # גובה המטוס

# נתוני הטבעות/מטרות בשמיים
rings = [
    {"x": 300, "y": 200, "size": 60, "active": True},
    {"x": 700, "y": 400, "size": 50, "active": True},
    {"x": 500, "y": 150, "size": 70, "active": True},
]
score = 0

# --- לולאת המשחק הראשי ---
running = True
while running:
    # 1. טיפול באירועים
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. קריאת נתונים מה-Joystick
    # ציר 0 = שמאל/ימין (Roll), ציר 1 = למעלה/למטה (Pitch)
    axis_roll = joystick.get_axis(0)   # ערך בין 1.0- ל-1.0
    axis_pitch = joystick.get_axis(1)  # ערך בין 1.0- ל-1.0
    
    # "Deadzone" קטן למניעת סטייה של סטיק רגיש מדי
    DEADZONE = 0.08
    if abs(axis_roll) < DEADZONE: axis_roll = 0
    if abs(axis_pitch) < DEADZONE: axis_pitch = 0

    # עדכון זווית המטוס והגובה לפי הג'ויסטיק
    roll = axis_roll * 30  # זווית הטיות שמאלה/ימינה
    pitch = axis_pitch * 20  # זווית הטיות מעלה/מטה

    # תזזית המטוס לפי הסטיק
    plane_x += axis_roll * 6
    plane_y += axis_pitch * 6
    
    # הגבלת המטוס לגבולות המסך
    plane_x = max(100, min(WIDTH - 100, plane_x))
    plane_y = max(100, min(HEIGHT - 100, plane_y))

    # 3. ציור הרקע (אופק דינמי לפי ה-Pitch/Roll)
    screen.fill(SKY_BLUE)
    
    # ציור הקרקע הירוקה
    horizon_y = (HEIGHT // 2) + (pitch * 5)
    pygame.draw.rect(screen, GREEN, (0, horizon_y, WIDTH, HEIGHT - horizon_y))

    # 4. ציור הטבעות (מטרות)
    for ring in rings:
        if ring["active"]:
            pygame.draw.circle(screen, GOLD, (ring["x"], ring["y"]), ring["size"], 8)
            
            # בדיקת פגיעה (חצייה בתוך הטבעת)
            dist = math.hypot(plane_x - ring["x"], plane_y - ring["y"])
            if dist < ring["size"]:
                ring["active"] = False
                score += 100

    # 5. ציור הכוונת / המטוס (Crosshair/HUD)
    # גוף המטוס (מרכז)
    pygame.draw.circle(screen, RED, (int(plane_x), int(plane_y)), 8)
    # כנפיים הצידה
    wing_offset_x = math.cos(math.radians(roll)) * 40
    wing_offset_y = math.sin(math.radians(roll)) * 40
    pygame.draw.line(screen, RED, 
                     (plane_x - wing_offset_x, plane_y - wing_offset_y), 
                     (plane_x + wing_offset_x, plane_y + wing_offset_y), 5)

    # 6. הצגת ניקוד ונתוני HUD (תצוגת טיסה)
    font = pygame.font.SysFont("Arial", 24, bold=True)
    score_text = font.render(f"Score: {score}", True, WHITE)
    pitch_text = font.render(f"Pitch: {-int(axis_pitch*100)}%", True, WHITE)
    roll_text = font.render(f"Roll: {int(axis_roll*100)}%", True, WHITE)
    
    screen.blit(score_text, (20, 20))
    screen.blit(pitch_text, (20, 50))
    screen.blit(roll_text, (20, 80))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()