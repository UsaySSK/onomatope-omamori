# main06.py（bold + turbulence反映済み完全版）
# onoma_text_particle_full.py

import pygame
import random
import math
import os
import csv
from datetime import datetime, timedelta

WIDTH, HEIGHT = 400, 600
FPS = 60
FONT_NAME = "meiryo"
BG_FOLDER = "backgrounds"
BGM_FILE = "bgm.mp3"
CSV_FILE = "data.csv"
HEADER_IMAGE = "beta.png"
HEADER_COLOR = (0, 230, 221)
HEADER_ALPHA = 100

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.mixer.init()
if os.path.exists(BGM_FILE):
    pygame.mixer.music.load(BGM_FILE)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

bg_images = [
    pygame.transform.scale(pygame.image.load(os.path.join(BG_FOLDER, f)).convert(), (WIDTH, HEIGHT))
    for f in os.listdir(BG_FOLDER)
    if f.endswith(".jpg") or f.endswith(".png")
]
bg_index = random.randint(0, len(bg_images) - 1)
bg_next_index = (bg_index + 1) % len(bg_images)
last_switch = pygame.time.get_ticks()

header_img = None
if os.path.exists(HEADER_IMAGE):
    mask = pygame.image.load(HEADER_IMAGE).convert_alpha()
    mask = pygame.transform.scale(mask, (WIDTH, 88))
    header_img = pygame.Surface((WIDTH, 88), pygame.SRCALPHA)
    for x in range(WIDTH):
        for y in range(88):
            _, _, _, a = mask.get_at((x, y))
            if a > 0:
                header_img.set_at((x, y), (*HEADER_COLOR, min(HEADER_ALPHA, a)))

FORTUNE_MAP = {
    "最高！": "★★★★ 最高！",
    "まあまあ": "★★☆☆ まあまあ",
    "注意！": "★☆☆☆ 注意！",
    "最注意！": "☆☆☆☆ 注意Max！",
}

def load_entries():
    entries = []
    with open(CSV_FILE, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            onoma = row["オノマトペ"].strip()
            imi = row["意味"].strip()
            tag = row["タグ"].strip()
            unsei = row["運勢"].strip()
            hito = row["ひとこと"].strip()
            if not unsei:
                unsei = random.choice(list(FORTUNE_MAP.values()))
            else:
                unsei = FORTUNE_MAP.get(unsei, unsei)
            entries.append((onoma, imi, unsei, tag, hito))
    return entries

entries = load_entries()
random.shuffle(entries)
entry_index = 0
scroll_x = WIDTH

def get_font(size):
    return pygame.font.SysFont(FONT_NAME, size, bold=True)

class Particle:
    def __init__(self, x, y, particle_type="default"):
        self.x = x
        self.y = y
        self.particle_type = particle_type # パーティクルの種類を識別

        if self.particle_type == "onomatope":
            # オノマトペ用のパーティクルは中心から拡散するように
            self.vx = random.uniform(-1.8, 1.8)   # ★調整済み（左右の広がり）
            self.vy = random.uniform(-0.8, 0.8)
            self.life = random.randint(45, 75)
            self.radius = random.choice([1, 2])
            self.color = random.choice([(255,255,255), (255,255,200), (255,220,240)])
            self.turb_angle = random.uniform(0, 2 * math.pi)
            self.turb_speed = random.uniform(0.05, 0.2)
            self.turb_amplitude = random.uniform(0.5, 2.5)
        else: # default (日付横のパーティクル)
            self.vx = random.uniform(1.5, 3.0)
            self.vy = random.uniform(0.5, 1.2)
            self.life = random.randint(45, 75)
            self.radius = random.choice([1, 2])
            self.color = random.choice([(255,255,255), (255,255,200), (255,220,240)])
            self.turb_angle = random.uniform(0, 2 * math.pi)
            self.turb_speed = random.uniform(0.01, 0.1)
            self.turb_amplitude = random.uniform(0.5, 2.5)

        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy + math.sin(self.turb_angle) * self.turb_amplitude
        self.turb_angle += self.turb_speed
        self.life -= 1
        if self.life < 30:
            self.alpha = int(255 * (self.life / 30))

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            surface.blit(s, (int(self.x), int(self.y)))

class ParticleEffect:
    def __init__(self, particle_type="default"):
        self.particles = []
        self.particle_type = particle_type
        # 初期エミッター位置はdefaultタイプのみで意味を持つ
        if self.particle_type == "default":
            self.reset_emitter_position() # 初期化時にエミッター位置をリセット
        
    def reset_emitter_position(self):
        # defaultタイプのパーティクル生成位置をリセットするメソッド
        self.emitter_x = -int(WIDTH * 0.5)
        self.end_x = int(WIDTH * 1.5)
        self.particles = [] # 既存のパーティクルもクリア

    def add_particles_around(self, rect, num_particles):
        # オノマトペ用パーティクル生成メソッド
        for _ in range(num_particles):
            x = random.uniform(rect.left, rect.right)
            y = random.uniform(rect.top, rect.bottom)
            self.particles.append(Particle(x, y, "onomatope")) # オノマトペタイプで生成

    def update(self):
        if self.particle_type == "default":
            # defaultタイプは、emitter_xがend_xに達するまでパーティクルを生成
            if self.emitter_x < self.end_x:
                for _ in range(4): # 1フレームあたりの生成数
                    y = random.randint(30, 50) # 垂直方向の生成範囲
                    self.particles.append(Particle(self.emitter_x, y, "default"))
                self.emitter_x += 6 # 生成位置を右へ移動
            # else: self.emitter_x = -int(WIDTH * 0.5) # この行を削除済み
        
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

def draw_text(surface, text, x, y, font, color, outline_color=None, center=False):
    if outline_color:
        base = font.render(text, True, outline_color)
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            pos = base.get_rect(center=(x+dx, y+dy)).topleft if center else (x+dx, y+dy)
            surface.blit(base, pos)
    text_surface = font.render(text, True, color)
    pos = text_surface.get_rect(center=(x, y)).topleft if center else (x, y)
    surface.blit(text_surface, pos)
    return text_surface.get_rect(center=(x,y)) if center else text_surface.get_rect(topleft=(x,y))


def main():
    global bg_index, bg_next_index, last_switch, entry_index, scroll_x
    frame_count = 0
    today = datetime.today() # 日付をここで管理
    
    # 既存のパーティクルエフェクト (日付横)
    default_particle_effect = ParticleEffect("default") 
    # オノマトペ用のパーティクルエフェクト
    onomatope_particle_effect = ParticleEffect("onomatope")
    
    running = True
    fade_duration = 2000
    bg_display_time = 5000

    while running:
        now = pygame.time.get_ticks()
        elapsed = now - last_switch

        if elapsed > bg_display_time + fade_duration:
            bg_index = bg_next_index
            while True:
                next_idx = random.choice(range(len(bg_images)))
                if next_idx != bg_index:
                    bg_next_index = next_idx
                    break
            last_switch = now
            elapsed = 0

        alpha = min(1.0, max(0.0, (elapsed - bg_display_time) / fade_duration)) if elapsed > bg_display_time else 0.0
        blended = bg_images[bg_index].copy()
        if alpha > 0:
            overlay = bg_images[bg_next_index].copy()
            overlay.set_alpha(int(alpha * 255))
            blended.blit(overlay, (0, 0))
        screen.blit(blended, (0, 0))

        if header_img:
            screen.blit(header_img, (0, -3))

        pygame.draw.rect(screen, (255, 255, 255), screen.get_rect(), 2)

        # 既存のパーティクルエフェクトの更新と描画 (常に実行)
        default_particle_effect.update()
        default_particle_effect.draw(screen)

        onoma, imi, unsei, tag, hito = entries[entry_index]

        # 日付と「今日のオノマトペ」の描画
        date_text_str = today.strftime("%m月%d日（" + "月火水木金土日"[today.weekday()] + "）") + " のオノマトペ"
        date_text_rect = None # 初期化
        if frame_count >= 20:
            date_text_rect = draw_text(
                screen,
                date_text_str,
                WIDTH // 2, 40,
                get_font(24), (255,255,255), (255,0,0), center=True
            )

        # オノマトペの文字とパーティクルの描画
        if frame_count >= 40:
            scale_duration = 6
            zoom_frames = frame_count - 40
            scale = 0.1 + 0.9 * min(1.0, zoom_frames / scale_duration)
            font = get_font(int(56 * scale))
            text_surface = font.render(onoma, True, (255,50,50))
            text_rect = text_surface.get_rect(center=(WIDTH//2, 360))

            # オノマトペ用パーティクルの生成
            if frame_count % 1 == 0 and zoom_frames < scale_duration * 2: # ★調整済み（発生タイミング）
                onomatope_particle_effect.add_particles_around(text_rect, 10) # ★調整済み（パーティクルの数）

            # オノマトペ用パーティクルの更新
            onomatope_particle_effect.update()
            
            # オノマトペ用パーティクルを文字の「後ろ」に描画
            onomatope_particle_effect.draw(screen)

            # 縁取りを2pxの自然な広がりに
            outline_surface = font.render(onoma, True, (255,255,255))
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx != 0 or dy != 0:
                        screen.blit(outline_surface, (text_rect.x + dx, text_rect.y + dy))
            screen.blit(text_surface, text_rect.topleft) # オノマトペ文字の描画

        # 他の情報の描画は変更なし
        if frame_count >= 70:
            draw_text(screen, "意味: " + imi, 20, 415, get_font(18), (50,50,255), (255,255,255))
        if frame_count >= 80:
            draw_text(screen, "運勢: " + unsei, 20, 445, get_font(18), (0,180,0), (255,255,255))
        if frame_count >= 90:
            draw_text(screen, "タグ: " + tag, 20, 475, get_font(18), ("purple"), (255,255,255))
        if frame_count >= 100:
            draw_text(screen, "ひとこと：", 20, 505, get_font(20), (255,50,50), ("white"))
            scroll_surface = get_font(25).render(hito, True, (255,250,250))
            outline_surface = get_font(25).render(hito, True, ("red"))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                screen.blit(outline_surface, (scroll_x + dx, 535 + dy))
            screen.blit(scroll_surface, (scroll_x, 535))
            scroll_x -= 1
            if scroll_x < -scroll_surface.get_width():
                scroll_x = WIDTH

        # 「次のオノマトペ」の描画
        if frame_count >= 120:
            next_display_day = today + timedelta(days=1) 
            draw_text(
                screen,
                next_display_day.strftime("%m月%d日（" + "月火水木金土日"[next_display_day.weekday()] + "）") + " のオノマトペ ▶",
                WIDTH // 2, HEIGHT - 20,
                get_font(18), ("white"), ("red"), center=True
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 画面のどこをクリックしても日付とオノマトペが進むように変更
                today += timedelta(days=1) # 日付を1日進める
                default_particle_effect.reset_emitter_position() # 日付横パーティクルをリセット

                # オノマトペを次に進める
                entry_index = (entry_index + 1) % len(entries)
                scroll_x = WIDTH
                frame_count = 0 # 新しいオノマトペ表示時にアニメーションをリセット
                onomatope_particle_effect = ParticleEffect("onomatope") # オノマトペ用パーティクルをリセット
                
        pygame.display.flip()
        clock.tick(FPS)
        frame_count += 1

    pygame.quit()

if __name__ == "__main__":
    main()
