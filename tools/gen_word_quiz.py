#!/usr/bin/env python3
"""產生 quiz-words.js：依第 1~6 課語詞表，加入選擇題到 QUIZ_BANK（語詞大師與各課闖關都會用到）。
執行：python3 tools/gen_word_quiz.py
"""
import json, random, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, 'data/chinese-lessons-1-6.json'), encoding='utf-8'))

# 使用者提供的各課語詞 (撿柴已依課本資料更正)
WORDS = {
 1: "等待 寸 忙碌 飛奔 彈簧 縮短 悲傷 忍氣吞聲 蝸牛",
 2: "便利貼 提醒 準時 睡覺 鬧鐘 有效 而且 冰箱 循序漸進",
 3: "統計 公車票 作業本 該 喊 文具 因此 準備 容易 天涯海角",
 4: "食堂 師父 撿柴 鍋子 冒 沸騰 解 揚湯止沸 釜底抽薪",
 5: "梨花 撐傘 甜蜜 腐爛 筷子 綁 遮雨 如膠似漆",
 6: "製成 筆芯 斷裂 機器 凹槽 三明治 筆桿 削鉛筆機 墨守成規",
}
WORDS = {k: v.split() for k, v in WORDS.items()}
# 單字詞 → 用課本生字表中的詞語出題
vocab_word = {(v['lesson'], v['c']): v['w'] for v in data['vocab']}

IDIOMS = {
 '忍氣吞聲': '受了委屈卻忍耐著,不敢說話或反抗',
 '循序漸進': '照著順序,一步一步慢慢進步',
 '天涯海角': '形容非常遙遠的地方',
 '揚湯止沸': '把滾水舀起再倒回去想讓它停止沸騰,比喻只處理表面,沒有解決根本問題',
 '釜底抽薪': '抽掉鍋子底下的柴火,比喻從根本上解決問題',
 '如膠似漆': '像膠和漆黏在一起一樣,形容感情很好,分不開',
 '墨守成規': '固守舊的方法和規矩,不知道變通',
}
# 手寫語境句 (＿＿ 為空格)，選項皆為同課語詞，並避免多個選項都說得通
SENTENCES = {
 '等待': ('公車還沒來，我站在站牌下＿＿。', ['縮短', '蝸牛', '彈簧']),
 '忙碌': ('媽媽每天上班又做家事，總是很＿＿。', ['縮短', '蝸牛', '彈簧']),
 '飛奔': ('下課鐘聲一響，同學們＿＿衝向操場。', ['等待', '縮短', '彈簧']),
 '縮短': ('把太長的褲管剪掉一截，長度就＿＿了。', ['等待', '蝸牛', '忙碌']),
 '悲傷': ('小狗走丟了，小明難過又＿＿。', ['忙碌', '飛奔', '彈簧']),
 '彈簧': ('按下原子筆，裡面的＿＿會把筆尖彈回去。', ['蝸牛', '縮短', '悲傷']),
 '蝸牛': ('＿＿爬得很慢，背上還背著一個殼。', ['飛奔', '彈簧', '忙碌']),
 '鬧鐘': ('早上七點，＿＿響了，我趕快起床。', ['冰箱', '便利貼', '準時']),
 '有效': ('老師教的方法很＿＿，我的成績進步了。', ['而且', '提醒', '準時']),
 '冰箱': ('吃不完的菜要放進＿＿保存。', ['鬧鐘', '睡覺', '便利貼']),
 '公車票': ('我把＿＿弄丟了，沒辦法搭車回家。', ['作業本', '文具', '統計']),
 '因此': ('他每天認真練習，＿＿比賽得到第一名。', ['容易', '準備', '統計']),
 '容易': ('這題很簡單，我覺得很＿＿。', ['因此', '準備', '統計']),
 '師父': ('他跟著＿＿學做麵包。', ['食堂', '鍋子', '沸騰']),
 '甜蜜': ('全家人一起吃蛋糕，大家笑得好＿＿。', ['腐爛', '筷子', '遮雨']),
 '筷子': ('我用＿＿夾起一塊豆腐。', ['梨花', '遮雨', '腐爛']),
 '遮雨': ('撐開大傘可以幫我們＿＿。', ['甜蜜', '腐爛', '筷子']),
 '腐爛': ('香蕉放太久，就會＿＿發臭。', ['甜蜜', '筷子', '梨花']),
 '削鉛筆機': ('把鉛筆插進＿＿，轉一轉就削尖了。', ['三明治', '筆桿', '凹槽']),
}
for w, (s, d) in SENTENCES.items():
    assert '＿＿' in s and w not in s, w

# 這些課文句子拿來挖空後，會有不只一個選項說得通，所以略過
SKIP_CLAUSE = ['幫助我們的', '謝謝您幫我做的', '睡覺前我得先整理好', '小真馬上寫在']

def lesson_of(w):
    return next(l for l, ws in WORDS.items() if w in ws)

def clean(t): return t.replace('【', '').replace('】', '')
passage = {p['lesson']: clean(p['text']) for p in data['passages']}
all_words = [w for ws in WORDS.values() for w in ws]
items = []
def add(lesson, stem, correct, wrong, explain):
    opts = [correct] + wrong[:3]
    assert len(set(opts)) == 4, (stem, opts)
    items.append({'lesson': lesson, 'cat': 'word', 'kind': 'mc', 'stem': stem,
                  'options': opts, 'answer': 0, 'explain': explain, 'id': None, 'src': '使用者語詞表'})

for lesson, ws in WORDS.items():
    rng = random.Random(1000 + lesson)
    pool_chars = list({c for l in WORDS.values() for w in l for c in w if len(w) > 1})
    for w in ws:
        full = vocab_word.get((lesson, w), w)        # 單字用課本詞語
        # A. 補字題
        if len(full) >= 2:
            pos = rng.randrange(len(full))
            ch = full[pos]
            masked = full[:pos] + '＿' + full[pos+1:]
            cands = [c for c in pool_chars if c not in full]
            add(lesson, f'「{masked}」\n＿ 要怎麼寫？', ch, rng.sample(cands, 3), f'{full}')
        # B. 課文語境題
        clause = None
        if len(w) >= 2:
            for sent in re.split(r'[。！？!?]', passage.get(lesson, '')):
                for c in re.split(r'[,，、]', sent):
                    if w in c and len(c) >= 8:
                        clause = c; break
                if clause: break
        if clause and w not in IDIOMS and not any(k in clause for k in SKIP_CLAUSE):
            others = [x for x in ws if x != w and x not in IDIOMS and abs(len(x) - len(w)) <= 1 and x not in clause]
            if len(others) >= 3:
                add(lesson, clause.replace(w, '＿＿', 1), w, rng.sample(others, 3), f'答案:{w}')
        # C. 手寫語境題
        if w in SENTENCES:
            s, d = SENTENCES[w]
            add(lesson, s, w, list(d), f'答案:{w}')
        # D. 成語意思
        if w in IDIOMS:
            wrong = rng.sample([m for k, m in IDIOMS.items() if k != w], 3)
            add(lesson, f'「{w}」是什麼意思？', IDIOMS[w], wrong, f'{w}:{IDIOMS[w]}')

out = '// 自動產生自 tools/gen_word_quiz.py (使用者提供的第1~6課語詞)\nif (typeof QUIZ_BANK !== "undefined") {\n  QUIZ_BANK.push(...' + \
      json.dumps(items, ensure_ascii=False, indent=0) + ');\n}\n'
open(os.path.join(ROOT, 'quiz-words.js'), 'w', encoding='utf-8').write(out)
cover = {w: 0 for w in all_words}
for it in items:
    for w in all_words:
        if w in it['stem'] or w in it['explain']: cover[w] += 1
print('questions:', len(items), 'by lesson', {l: sum(1 for i in items if i['lesson'] == l) for l in WORDS})
print('words with no question:', [w for w, c in cover.items() if c == 0])
