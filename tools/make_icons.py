"""
여행 회화 앱 아이콘 만들기 도구

초록 바탕에 말풍선 두 개(Hi! / 你好)가 들어간 아이콘을 만든다.
  icons/icon-192.png, icon-512.png       일반 아이콘
  icons/icon-maskable-512.png            안드로이드가 둥글게 잘라 쓰는 아이콘 (여백 10%)
  icons/apple-touch-icon.png (180px)     아이폰 홈 화면 아이콘

사용법 (저장소 맨 위 폴더에서, 윈도우 PC):
    pip install pillow
    python tools/make_icons.py
글꼴은 윈도우 기본 글꼴(Arial Bold, Microsoft YaHei Bold)을 쓴다.
아이콘을 바꾼 뒤에는 sw.js의 VERSION도 올려야 폰에 반영된다.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'icons')
FONT_EN = 'C:/Windows/Fonts/arialbd.ttf'   # 'Hi!'
FONT_ZH = 'C:/Windows/Fonts/msyhbd.ttc'    # '你好'
GREEN, WHITE, SUN, INK = '#0f6b5c', '#ffffff', '#f3c56b', '#14231f'


def make(size, pad=0.0):
    """1024px로 그린 뒤 줄인다. pad는 가장자리 여백 비율 (maskable 아이콘용)."""
    S = 1024
    im = Image.new('RGB', (S, S), GREEN)
    d = ImageDraw.Draw(im)
    k, o = 1 - pad * 2, S * pad
    P = lambda x, y: (o + x * k, o + y * k)   # 여백을 반영한 좌표
    # 큰 흰 말풍선 + 꼬리
    d.rounded_rectangle([P(150, 200), P(760, 600)], radius=110 * k, fill=WHITE)
    d.polygon([P(260, 580), P(420, 580), P(230, 720)], fill=WHITE)
    d.text(P(455, 400), 'Hi!', font=ImageFont.truetype(FONT_EN, int(260 * k)), fill=GREEN, anchor='mm')
    # 작은 노란 말풍선 + 꼬리
    d.rounded_rectangle([P(470, 560), P(880, 840)], radius=90 * k, fill=SUN)
    d.polygon([P(760, 820), P(860, 820), P(840, 920)], fill=SUN)
    d.text(P(675, 695), '你好', font=ImageFont.truetype(FONT_ZH, int(170 * k)), fill=INK, anchor='mm')
    return im.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, size, pad in [('icon-192.png', 192, 0), ('icon-512.png', 512, 0),
                            ('apple-touch-icon.png', 180, 0), ('icon-maskable-512.png', 512, 0.1)]:
        make(size, pad).save(os.path.join(OUT, name))
        print('icons/' + name)


if __name__ == '__main__':
    main()
