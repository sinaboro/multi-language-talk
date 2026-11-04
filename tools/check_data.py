"""
여행 회화 데이터 검사 도구

index.html의 문장 데이터를 검사한다. 문장을 추가·수정한 뒤에 실행한다.
  - 영어(RAW)와 다른 언어(LANG_RAW)의 줄 수가 같은지 (순서가 어긋나면 뜻이 엉뚱하게 붙음)
  - 줄마다 칸 수가 맞는지 (영어 5칸, 일본어·이탈리아어·프랑스어 2칸, 중국어 3칸)
  - 상황 이름이 CATS에 있는지, 같은 문장이 두 번 들어가지 않았는지
    (영어 문장은 즐겨찾기 저장 열쇠라서 겹치면 오류)

사용법 (저장소 맨 위 폴더에서):
    python tools/check_data.py           # 검사
    python tools/check_data.py --show 20 # 21번째 문장을 언어별로 나란히 보기 (0부터 셈)
    python tools/check_data.py --bump    # 검사 통과하면 sw.js의 VERSION 숫자 1 올리기
추가 설치는 필요 없다.
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
SW = os.path.join(ROOT, 'sw.js')
FIELDS = {'ja': 2, 'zh': 3, 'it': 2, 'fr': 2}   # 언어별 칸 수: 문장|한글 발음(|병음)


def load():
    src = open(INDEX, encoding='utf-8').read()
    cats = re.findall(r"\['(\w+)','[^']+'\]", src.split('const CATS = [')[1].split('];')[0])
    en = [l for l in src.split('const RAW = `')[1].split('`')[0].strip().split('\n')]
    langs = {}
    body = src.split('const LANG_RAW = {')[1].split('\n};')[0]
    for lg in FIELDS:
        langs[lg] = body.split(f'{lg}:`')[1].split('`')[0].strip().split('\n')
    return cats, en, langs


def check(cats, en, langs):
    errors, notes = [], []
    for i, l in enumerate(en):
        f = l.split('|')
        if len(f) != 5:
            errors.append(f'영어 {i}번: 칸이 5개가 아님 (상황|영어|발음|뜻|도움말) → {l}')
        elif f[0] not in cats:
            errors.append(f'영어 {i}번: 상황 "{f[0]}"이 CATS에 없음')
    for lg, lines in langs.items():
        if len(lines) != len(en):
            errors.append(f'{lg}: {len(lines)}줄 - 영어 {len(en)}줄과 다름 (어딘가 빠지거나 더 들어감)')
        for i, l in enumerate(lines):
            if len(l.split('|')) != FIELDS[lg]:
                errors.append(f'{lg} {i}번: 칸이 {FIELDS[lg]}개가 아님 → {l}')
        dup = [t for t, c in collections.Counter(l.split('|')[0] for l in lines).items() if c > 1]
        if dup:
            notes.append(f'{lg}: 같은 문장이 두 번 → {dup}')
    # 영어 문장은 즐겨찾기 저장 열쇠라서 겹치면 안 된다
    dup = [t for t, c in collections.Counter(l.split('|')[1] for l in en if '|' in l).items() if c > 1]
    if dup:
        errors.append(f'영어: 같은 문장이 두 번 (즐겨찾기 열쇠가 겹침) → {dup}')
    return errors, notes


def show(i, en, langs):
    f = en[i].split('|')
    print(f'[{i}] {f[0]} - {f[3]}')
    print(f'  en: {f[1]}  ({f[2]})')
    for lg, lines in langs.items():
        if i < len(lines):
            print(f'  {lg}: ' + '  /  '.join(lines[i].split('|')))


def bump():
    s = open(SW, encoding='utf-8').read()
    m = re.search(r"const VERSION = '([^']*?)(\d+)';", s)
    if not m:
        sys.exit('sw.js에서 VERSION을 찾지 못했어요.')
    old, new = m.group(1) + m.group(2), m.group(1) + str(int(m.group(2)) + 1)
    open(SW, 'w', encoding='utf-8', newline='\n').write(s.replace(f"'{old}'", f"'{new}'", 1))
    print(f'sw.js VERSION: {old} → {new}')


def main():
    # 한국어 윈도우 콘솔에서 출력할 수 없는 문자가 있어도 멈추지 않게
    sys.stdout.reconfigure(errors='replace')
    ap = argparse.ArgumentParser(description='여행 회화 데이터 검사')
    ap.add_argument('--show', type=int, help='이 번호의 문장을 언어별로 보기')
    ap.add_argument('--bump', action='store_true', help='검사 통과 후 sw.js VERSION 올리기')
    a = ap.parse_args()
    cats, en, langs = load()
    if a.show is not None:
        show(a.show, en, langs)
        return
    errors, notes = check(cats, en, langs)
    print(f'상황 {len(cats)}개 · 문장 {len(en)}개 · 언어 {1 + len(langs)}개')
    for n in notes:
        print('  [확인]', n)
    if errors:
        print('\n오류가 있어 멈춥니다:')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('검사 통과')
    if a.bump:
        bump()


if __name__ == '__main__':
    main()
