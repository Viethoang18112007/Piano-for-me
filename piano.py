import pygame
import math
import sys

# Khởi tạo pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Kích thước cửa sổ
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 400

# Kích thước phím
WHITE_KEY_WIDTH = 60
WHITE_KEY_HEIGHT = 300
BLACK_KEY_WIDTH = 40
BLACK_KEY_HEIGHT = 180

# Tạo cửa sổ
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Đàn Piano - Nhấn phím hoặc click chuột để chơi")

# Font chữ
font = pygame.font.Font(None, 24)

# Tần số các nốt nhạc (Octave 4)
NOTES = {
    'C': 261.63,
    'C#': 277.18,
    'D': 293.66,
    'D#': 311.13,
    'E': 329.63,
    'F': 349.23,
    'F#': 369.99,
    'G': 392.00,
    'G#': 415.30,
    'A': 440.00,
    'A#': 466.16,
    'B': 493.88,
}

# Ánh xạ phím bàn phím với nốt nhạc
KEYBOARD_MAPPING = {
    pygame.K_a: 'C',
    pygame.K_w: 'C#',
    pygame.K_s: 'D',
    pygame.K_e: 'D#',
    pygame.K_d: 'E',
    pygame.K_f: 'F',
    pygame.K_t: 'F#',
    pygame.K_g: 'G',
    pygame.K_y: 'G#',
    pygame.K_h: 'A',
    pygame.K_u: 'A#',
    pygame.K_j: 'B',
    pygame.K_k: 'C',  # Octave tiếp theo
    pygame.K_o: 'C#',
    pygame.K_l: 'D',
}

# Danh sách các phím trắng và đen
WHITE_KEYS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
BLACK_KEYS = ['C#', 'D#', 'F#', 'G#', 'A#']

# Vị trí các phím đen (offset từ phím trắng)
BLACK_KEY_POSITIONS = {
    'C#': 0,
    'D#': 1,
    'F#': 3,
    'G#': 4,
    'A#': 5,
}

def generate_tone(frequency, duration=0.3, sample_rate=22050):
    """Tạo âm thanh cho một nốt nhạc"""
    frames = int(duration * sample_rate)
    arr = []
    for i in range(frames):
        wave = 4096 * math.sin(2 * math.pi * frequency * i / sample_rate)
        arr.append([int(wave), int(wave)])
    return arr

def play_note(note_name):
    """Phát âm thanh của một nốt nhạc"""
    if note_name in NOTES:
        frequency = NOTES[note_name]
        sound_array = generate_tone(frequency)
        sound = pygame.sndarray.make_sound(sound_array)
        sound.play()

def draw_piano(white_key_positions, black_key_positions):
    """Vẽ đàn piano"""
    # Vẽ phím trắng
    for key_name, (x, note) in white_key_positions.items():
        # Vẽ phím trắng
        key_rect = pygame.Rect(x, WINDOW_HEIGHT - WHITE_KEY_HEIGHT, 
                              WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT)
        pygame.draw.rect(screen, WHITE, key_rect)
        pygame.draw.rect(screen, BLACK, key_rect, 2)
        
        # Vẽ tên nốt
        text = font.render(note, True, BLACK)
        text_rect = text.get_rect(center=(x + WHITE_KEY_WIDTH // 2, 
                                          WINDOW_HEIGHT - 30))
        screen.blit(text, text_rect)
    
    # Vẽ phím đen
    for key_name, (x, note) in black_key_positions.items():
        # Vẽ phím đen
        key_rect = pygame.Rect(x, WINDOW_HEIGHT - WHITE_KEY_HEIGHT, 
                              BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT)
        pygame.draw.rect(screen, BLACK, key_rect)
        pygame.draw.rect(screen, DARK_GRAY, key_rect, 2)

def get_note_from_position(pos, white_key_positions, black_key_positions):
    """Xác định nốt nhạc từ vị trí click chuột"""
    x, y = pos
    
    # Kiểm tra phím đen trước (vì chúng ở trên)
    for key_name, (key_x, note) in black_key_positions.items():
        if (key_x <= x <= key_x + BLACK_KEY_WIDTH and 
            WINDOW_HEIGHT - WHITE_KEY_HEIGHT <= y <= WINDOW_HEIGHT - WHITE_KEY_HEIGHT + BLACK_KEY_HEIGHT):
            return note
    
    # Kiểm tra phím trắng
    for key_name, (key_x, note) in white_key_positions.items():
        if (key_x <= x <= key_x + WHITE_KEY_WIDTH and 
            WINDOW_HEIGHT - WHITE_KEY_HEIGHT <= y <= WINDOW_HEIGHT):
            return note
    
    return None

def draw_instructions():
    """Vẽ hướng dẫn sử dụng"""
    instructions = [
        "Phím bàn phím: A S D F G H J K L (trắng) | W E T Y U O (đen)",
        "Click chuột vào các phím để chơi nhạc"
    ]
    y_offset = 10
    for instruction in instructions:
        text = font.render(instruction, True, BLACK)
        screen.blit(text, (10, y_offset))
        y_offset += 25

def main():
    """Hàm chính"""
    clock = pygame.time.Clock()
    pressed_keys = set()
    
    # Tính toán vị trí các phím
    white_key_positions = {}
    black_key_positions = {}
    
    # Tính vị trí phím trắng (2 octaves)
    all_white_keys = WHITE_KEYS * 2
    for i, note in enumerate(all_white_keys):
        x = i * WHITE_KEY_WIDTH
        # Tạo key duy nhất cho mỗi phím (thêm index để phân biệt octave)
        key_name = f"{note}_{i // len(WHITE_KEYS)}"
        white_key_positions[key_name] = (x, note)
    
    # Tính vị trí phím đen (2 octaves)
    for octave in range(2):
        for note in BLACK_KEYS:
            base_pos = BLACK_KEY_POSITIONS[note] + octave * 7
            x = base_pos * WHITE_KEY_WIDTH + WHITE_KEY_WIDTH - BLACK_KEY_WIDTH // 2
            key_name = f"{note}_{octave}"
            black_key_positions[key_name] = (x, note)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click chuột trái
                    note = get_note_from_position(event.pos, white_key_positions, black_key_positions)
                    if note:
                        play_note(note)
            
            elif event.type == pygame.KEYDOWN:
                if event.key in KEYBOARD_MAPPING and event.key not in pressed_keys:
                    note = KEYBOARD_MAPPING[event.key]
                    play_note(note)
                    pressed_keys.add(event.key)
            
            elif event.type == pygame.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)
        
        # Vẽ
        screen.fill(LIGHT_GRAY)
        draw_piano(white_key_positions, black_key_positions)
        draw_instructions()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

