import supervisor

from kmk.keys import KC
from kmk.keys import make_key
from kmk.handlers.sequences import send_string
from kmk.handlers.sequences import simple_key_sequence
from kmk.handlers.sequences import unicode_string_sequence

kouchi_shift = False # 後置シフトを許す

pressed_keys = set() # 同時に押しているキー
nginput = [] # 未変換のキー KeyActionの配列
max_keys = 4 # 5キーの組み合わせは遅すぎる。4キーでもオーバーフロー処理をすれば正しく変換できてる。
# pure_shift_keys = [KC.NGSFT, KC.NGSFT2]
# shift_keys = [KC.NGSFT, KC.NGSFT2, KC.NGF, KC.NGV, KC.NGJ, KC.NGM]
now = 0
ng_layer = 0
kblayers = None
kb = None
henshu_mode = 0

class KeyAction:
    def __init__(self, keycode, press_at, release_at):
        self.keycode = keycode
        self.press_at = press_at
        self.release_at = release_at
    
    def keycode_s(self):
        return self.keycode if self.keycode != KC.NGSFT2 else KC.NGSFT
    
    def release_at_t(self):
        now = supervisor.ticks_ms()
        return self.release_at if self.release_at > 0 else max(now, self.press_at + 10)

    def is_shift(self):
        return self.keycode in [KC.NGSFT, KC.NGSFT2, KC.NGF, KC.NGV, KC.NGJ, KC.NGM]

    def is_pure_shift(self):
        return self.keycode in [KC.NGSFT, KC.NGSFT2]

def initNaginata(_kb, _layers, _ng_layer):
    global kb, kblayers, ng_layer
    kb = _kb
    kblayers = _layers
    ng_layer = _ng_layer

def ng_henshu(*args, **kwargs):
    kc = args[0]
    if henshu_mode == 0:
        return True
    elif henshu_mode == 1:
        hk = nghenshu1dic[kc]
        if hk:
            kb.tap_key(simple_key_sequence(hk))
        return False
    elif henshu_mode == 2:
        kb.tap_key(KC.N2)
        return False

#　かな変換の処理
def ng_press(*args, **kwargs):
    global pressed_keys, now
    now = supervisor.ticks_ms()
    kc = args[0]

    # シフトキーのキャリーオーバー
    # まだおかしい
    # jklで、あいう、のはずが、ああいう、になる
    if len(nginput) < len(pressed_keys):
        for pk in pressed_keys:
            if pk in [KC.NGSFT, KC.NGSFT2, KC.NGF, KC.NGV, KC.NGJ, KC.NGM]:
                nginput.insert(0, KeyAction(pk, now, 0))
                break

    pressed_keys.add(kc)

    # オーバーフロー
    if len(pressed_keys) > max_keys or len(nginput) >= max_keys:
        s = ng_type(True)
        del nginput[0:s]

    nginput.append(KeyAction(kc, now, 0))

    # 早期確定
    if number_of_candidates() < 2:
        s = ng_type(True)
        del nginput[0:s]

    return False

def ng_release(*args, **kwargs):
    global pressed_keys, now
    now = supervisor.ticks_ms()
    kc = args[0]
    pressed_keys.discard(kc)
    
    # リリース時間保存
    for ka in nginput:
        if ka.keycode == kc and ka.release_at == 0:
            ka.release_at = now
            break

    # かな変換し出力
    if len(pressed_keys) == 0 and len(nginput) > 0:
        ng_type()
        nginput.clear()

    return False

def ng_type(partial = False):
    tstart = supervisor.ticks_ms()
    # partial nginputの全部を出力するか、最初だけ出力するか
    if len(nginput) == 1 and nginput[0].keycode == KC.NGSFT2:
        kb.tap_key(KC.ENT)
        return 1

    # キーの組合せから、辞書にあるものだけを抜き出す
    lllka = [] # list(list(list(KeyAction)))
    l = min([len(nginput), max_keys]) # ガード
    for lindex in ngcomb[l]: # list(list(num))
        llka = [] # list(list(KeyAction))
        is_exist = True # 辞書にある組み合わせかどうか
        inc_ks = False # 後置シフトを含むかどうか
        if lindex[0]: # 連続シフトがある組み合わせ
            for ka in nginput:
                if ka.is_shift(): #　連続シフトが入っている & シフトキーを含んでいる
                    break
            else: # 連続シフトが入っている & シフトキーを含んでなかった
                continue
        for cindex in lindex[1:]: # list(num)
            lka = [] # list(KeyAction)
            for i, ci in enumerate(cindex): # num
                if i > 0 and nginput[ci].is_pure_shift():
                    inc_ks = True
                lka.append(nginput[ci])
            skc = set(map(lambda x: x.keycode_s(), lka))
            for k in ngdic: # (set(KC), list(KC))
                if k[0] == skc:
                    break
            else:
                is_exist = False
                break
            llka.append(lka)
        if is_exist:
            if kouchi_shift:
                lllka.append(llka)
            else:
                if not inc_ks:
                    lllka.append(llka)
    
    print('ng_type 1 %d ms' % (supervisor.ticks_ms() - tstart))

    # 組み合わせの点数づけをして、点数の高い組合せを選ぶ
    best_score = 0
    best_comb = [] # list(list(KeyAction))
    for c in lllka:
        s = scoring(c)
        if s >= best_score:
            best_comb = c
            best_score = s

    if partial:
        bc = best_comb[0:1] # 最初の組合せだけ変換する
    else:
        bc = best_comb

    # かなに変換する
    keyseq = []
    ks = set() # 削除するキーセット
    for k in bc:
        s = set(map(lambda x: x.keycode_s(), k))
        for ka in k:
            ks.add(ka)
        for l in ngdic:
            if l[0] == s:
                keyseq += l[1]
                break

    kcs = simple_key_sequence(keyseq)
    kb.tap_key(kcs)

    print('ng_type %d-keys took %d ms' % (len(nginput), supervisor.ticks_ms() - tstart))

    # 何キー処理したが返す
    return len(ks)

def number_of_candidates():
    noc = 0
    
    skc = set(map(lambda x: x.keycode_s(), nginput))
    for k in ngdic: # (set(KC), list(KC))
        if skc <= k[0]:
            noc += 1
            # if noc > 1:
            #     break

    print('NG num of candidates %d' % noc)
    return noc

def scoring(comb): #list(list(KeyAction))
    score = 0
    for lka in comb: # list(KeyAction)
        if len(lka) == 1:
            score += 100
        else:
            latest_press = max(map(lambda x: x.press_at, lka))
            earliest_release = min(map(lambda x: x.release_at_t(), lka))
            overlap = earliest_release - latest_press
            for ka in lka:
                if ka.release_at_t() - ka.press_at > 0:
                    score += overlap * 1000 / (ka.release_at_t() - ka.press_at)
    
    return score / len(comb)

def naginata_on(*args, **kwargs):
    kblayers.activate_layer(kb, ng_layer)
    nginput.clear()
    kb.tap_key(KC.LANG1)
    kb.tap_key(KC.INT4)
    return False

def naginata_off(*args, **kwargs):
    kblayers.deactivate_layer(kb, ng_layer)
    nginput.clear()
    kb.tap_key(KC.LANG2)
    kb.tap_key(KC.INT5)
    return False

def ng_henshu1_on(*args, **kwargs):
    global henshu_mode
    henshu_mode = 1
    return False

def ng_henshu2_on(*args, **kwargs):
    global henshu_mode
    henshu_mode = 2
    return False

def ng_henshu_off(*args, **kwargs):
    global henshu_mode
    henshu_mode = 0
    return False

# キーの定義
ngkeys = [
    'NGQ', 'NGW', 'NGE', 'NGR', 'NGT', 'NGY', 'NGU', 'NGI', 'NGO', 'NGP', 
    'NGA', 'NGS', 'NGD', 'NGF', 'NGG', 'NGH', 'NGJ', 'NGK', 'NGL', 'NGSCLN',
    'NGZ', 'NGX', 'NGC', 'NGV', 'NGB', 'NGN', 'NGM', 'NGCOMM', 'NGDOT', 'NGSLSH',
    'NGSFT', 'NGSFT2'
]
for k in ngkeys:
    make_key(names=(k,), on_press = ng_press, on_release = ng_release)

make_key(names=('NGON' ,), on_release = naginata_on) # on_releaseの方が安定する
make_key(names=('NGOFF',), on_release = naginata_off)
make_key(names=('NGH1', ), on_press = ng_henshu1_on, on_release = ng_henshu_off)
make_key(names=('NGH2', ), on_press = ng_henshu2_on, on_release = ng_henshu_off)

KC.A.before_press_handler(ng_henshu)
KC.NGA.before_press_handler(ng_henshu)

# かな変換テーブル setはdictionaryのキーにできないので配列に
ngdic = [
    ({ KC.NGU                         }, [ KC.BSPC                      ]),
    ({ KC.NGSFT                       }, [ KC.SPC                       ]),
    ({ KC.NGM   , KC.NGV              }, [ KC.ENT                       ]),
    ({ KC.NGT                         }, [ KC.LEFT                      ]),
    ({ KC.NGY                         }, [ KC.RIGHT                     ]),
    ({ KC.NGSFT , KC.NGT              }, [ KC.LSFT(KC.LEFT)             ]), # 操作感悪い
    ({ KC.NGSFT , KC.NGY              }, [ KC.LSFT(KC.RIGHT)            ]), # 操作感悪い

  # 清音外来音 濁音外来音
    ({ KC.NGJ                         }, [ KC.A                         ]), # あ
    ({ KC.NGK                         }, [ KC.I                         ]), # い
    ({ KC.NGL                         }, [ KC.U                         ]), # う
    ({ KC.NGSFT , KC.NGO              }, [ KC.E                         ]), # え
    ({ KC.NGSFT , KC.NGN              }, [ KC.O                         ]), # お
    ({ KC.NGF                         }, [ KC.K, KC.A                   ]), # か
    ({ KC.NGW                         }, [ KC.K, KC.I                   ]), # き
    ({ KC.NGH                         }, [ KC.K, KC.U                   ]), # く
    ({ KC.NGS                         }, [ KC.K, KC.E                   ]), # け
    ({ KC.NGV                         }, [ KC.K, KC.O                   ]), # こ
    ({ KC.NGSFT , KC.NGU              }, [ KC.S, KC.A                   ]), # さ
    ({ KC.NGR                         }, [ KC.S, KC.I                   ]), # し
    ({ KC.NGO                         }, [ KC.S, KC.U                   ]), # す
    ({ KC.NGSFT , KC.NGA              }, [ KC.S, KC.E                   ]), # せ
    ({ KC.NGB                         }, [ KC.S, KC.O                   ]), # そ
    ({ KC.NGN                         }, [ KC.T, KC.A                   ]), # た
    ({ KC.NGSFT , KC.NGG              }, [ KC.T, KC.I                   ]), # ち
    ({ KC.NGSFT , KC.NGL              }, [ KC.T, KC.U                   ]), # つ
    ({ KC.NGE                         }, [ KC.T, KC.E                   ]), # て
    ({ KC.NGD                         }, [ KC.T, KC.O                   ]), # と
    ({ KC.NGM                         }, [ KC.N, KC.A                   ]), # な
    ({ KC.NGSFT , KC.NGD              }, [ KC.N, KC.I                   ]), # に
    ({ KC.NGSFT , KC.NGW              }, [ KC.N, KC.U                   ]), # ぬ
    ({ KC.NGSFT , KC.NGR              }, [ KC.N, KC.E                   ]), # ね
    ({ KC.NGSFT , KC.NGJ              }, [ KC.N, KC.O                   ]), # の
    ({ KC.NGC                         }, [ KC.H, KC.A                   ]), # は
    ({ KC.NGX                         }, [ KC.H, KC.I                   ]), # ひ
    ({ KC.NGSFT , KC.NGX              }, [ KC.H, KC.I                   ]), # ひ
    ({ KC.NGSFT , KC.NGSCLN           }, [ KC.H, KC.U                   ]), # ふ
    ({ KC.NGP                         }, [ KC.H, KC.E                   ]), # へ
    ({ KC.NGZ                         }, [ KC.H, KC.O                   ]), # ほ
    ({ KC.NGSFT , KC.NGZ              }, [ KC.H, KC.O                   ]), # ほ
    ({ KC.NGSFT , KC.NGF              }, [ KC.M, KC.A                   ]), # ま
    ({ KC.NGSFT , KC.NGB              }, [ KC.M, KC.I                   ]), # み
    ({ KC.NGSFT , KC.NGCOMM           }, [ KC.M, KC.U                   ]), # む
    ({ KC.NGSFT , KC.NGS              }, [ KC.M, KC.E                   ]), # め
    ({ KC.NGSFT , KC.NGK              }, [ KC.M, KC.O                   ]), # も
    ({ KC.NGSFT , KC.NGH              }, [ KC.Y, KC.A                   ]), # や
    ({ KC.NGSFT , KC.NGP              }, [ KC.Y, KC.U                   ]), # ゆ
    ({ KC.NGSFT , KC.NGI              }, [ KC.Y, KC.O                   ]), # よ
    ({ KC.NGDOT                       }, [ KC.R, KC.A                   ]), # ら
    ({ KC.NGSFT , KC.NGE              }, [ KC.R, KC.I                   ]), # り
    ({ KC.NGI                         }, [ KC.R, KC.U                   ]), # る
    ({ KC.NGSLSH                      }, [ KC.R, KC.E                   ]), # れ
    ({ KC.NGSFT , KC.NGSLSH           }, [ KC.R, KC.E                   ]), # れ
    ({ KC.NGA                         }, [ KC.R, KC.O                   ]), # ろ
    ({ KC.NGSFT , KC.NGDOT            }, [ KC.W, KC.A                   ]), # わ
    ({ KC.NGSFT , KC.NGC              }, [ KC.W, KC.O                   ]), # を
    ({ KC.NGCOMM                      }, [ KC.N, KC.N                   ]), # ん
    ({ KC.NGSCLN                      }, [ KC.MINS                      ]), # ー
    ({ KC.NGSFT , KC.NGV              }, [ KC.COMM, KC.ENT              ]), # 、{Enter}
    ({ KC.NGSFT , KC.NGM              }, [ KC.DOT, KC.ENT               ]), # 。{Enter}
    ({ KC.NGQ                         }, [ KC.V, KC.U                   ]), # ゔ
    ({ KC.NGSFT , KC.NGQ              }, [ KC.V, KC.U                   ]), # ゔ
    ({ KC.NGJ   , KC.NGF              }, [ KC.G, KC.A                   ]), # が
    ({ KC.NGJ   , KC.NGW              }, [ KC.G, KC.I                   ]), # ぎ
    ({ KC.NGF   , KC.NGH              }, [ KC.G, KC.U                   ]), # ぐ
    ({ KC.NGJ   , KC.NGS              }, [ KC.G, KC.E                   ]), # げ
    ({ KC.NGJ   , KC.NGV              }, [ KC.G, KC.O                   ]), # ご
    ({ KC.NGF   , KC.NGU              }, [ KC.Z, KC.A                   ]), # ざ
    ({ KC.NGJ   , KC.NGR              }, [ KC.Z, KC.I                   ]), # じ
    ({ KC.NGF   , KC.NGO              }, [ KC.Z, KC.U                   ]), # ず
    ({ KC.NGJ   , KC.NGA              }, [ KC.Z, KC.E                   ]), # ぜ
    ({ KC.NGJ   , KC.NGB              }, [ KC.Z, KC.O                   ]), # ぞ
    ({ KC.NGF   , KC.NGN              }, [ KC.D, KC.A                   ]), # だ
    ({ KC.NGJ   , KC.NGG              }, [ KC.D, KC.I                   ]), # ぢ
    ({ KC.NGF   , KC.NGL              }, [ KC.D, KC.U                   ]), # づ
    ({ KC.NGJ   , KC.NGE              }, [ KC.D, KC.E                   ]), # で
    ({ KC.NGJ   , KC.NGD              }, [ KC.D, KC.O                   ]), # ど
    ({ KC.NGJ   , KC.NGC              }, [ KC.B, KC.A                   ]), # ば
    ({ KC.NGJ   , KC.NGX              }, [ KC.B, KC.I                   ]), # び
    ({ KC.NGF   , KC.NGSCLN           }, [ KC.B, KC.U                   ]), # ぶ
    ({ KC.NGF   , KC.NGP              }, [ KC.B, KC.E                   ]), # べ
    ({ KC.NGJ   , KC.NGZ              }, [ KC.B, KC.O                   ]), # ぼ
    ({ KC.NGF   , KC.NGL              }, [ KC.V, KC.U                   ]), # ゔ
    ({ KC.NGM   , KC.NGC              }, [ KC.P, KC.A                   ]), # ぱ
    ({ KC.NGM   , KC.NGX              }, [ KC.P, KC.I                   ]), # ぴ
    ({ KC.NGV   , KC.NGSCLN           }, [ KC.P, KC.U                   ]), # ぷ
    ({ KC.NGV   , KC.NGP              }, [ KC.P, KC.E                   ]), # ぺ
    ({ KC.NGM   , KC.NGZ              }, [ KC.P, KC.O                   ]), # ぽ
    ({ KC.NGQ   , KC.NGH              }, [ KC.X, KC.Y, KC.A             ]), # ゃ
    ({ KC.NGQ   , KC.NGP              }, [ KC.X, KC.Y, KC.U             ]), # ゅ
    ({ KC.NGQ   , KC.NGI              }, [ KC.X, KC.Y, KC.O             ]), # ょ
    ({ KC.NGQ   , KC.NGJ              }, [ KC.X, KC.A                   ]), # ぁ
    ({ KC.NGQ   , KC.NGK              }, [ KC.X, KC.I                   ]), # ぃ
    ({ KC.NGQ   , KC.NGL              }, [ KC.X, KC.U                   ]), # ぅ
    ({ KC.NGQ   , KC.NGO              }, [ KC.X, KC.E                   ]), # ぇ
    ({ KC.NGQ   , KC.NGN              }, [ KC.X, KC.O                   ]), # ぉ
    ({ KC.NGQ   , KC.NGDOT            }, [ KC.X, KC.W, KC.A             ]), # ゎ
    ({ KC.NGG                         }, [ KC.X, KC.T, KC.U             ]), # っ
    ({ KC.NGQ   , KC.NGS              }, [ KC.X, KC.K, KC.E             ]), # ヶ
    ({ KC.NGQ   , KC.NGF              }, [ KC.X, KC.K, KC.A             ]), # ヵ
    ({ KC.NGR   , KC.NGH              }, [ KC.S, KC.Y, KC.A             ]), # しゃ
    ({ KC.NGR   , KC.NGP              }, [ KC.S, KC.Y, KC.U             ]), # しゅ
    ({ KC.NGR   , KC.NGI              }, [ KC.S, KC.Y, KC.O             ]), # しょ
    ({ KC.NGJ   , KC.NGR   , KC.NGH   }, [ KC.Z, KC.Y, KC.A             ]), # じゃ
    ({ KC.NGJ   , KC.NGR   , KC.NGP   }, [ KC.Z, KC.Y, KC.U             ]), # じゅ
    ({ KC.NGJ   , KC.NGR   , KC.NGI   }, [ KC.Z, KC.Y, KC.O             ]), # じょ
    ({ KC.NGW   , KC.NGH              }, [ KC.K, KC.Y, KC.A             ]), # きゃ
    ({ KC.NGW   , KC.NGP              }, [ KC.K, KC.Y, KC.U             ]), # きゅ
    ({ KC.NGW   , KC.NGI              }, [ KC.K, KC.Y, KC.O             ]), # きょ
    ({ KC.NGJ   , KC.NGW   , KC.NGH   }, [ KC.G, KC.Y, KC.A             ]), # ぎゃ
    ({ KC.NGJ   , KC.NGW   , KC.NGP   }, [ KC.G, KC.Y, KC.U             ]), # ぎゅ
    ({ KC.NGJ   , KC.NGW   , KC.NGI   }, [ KC.G, KC.Y, KC.O             ]), # ぎょ
    ({ KC.NGG   , KC.NGH              }, [ KC.T, KC.Y, KC.A             ]), # ちゃ
    ({ KC.NGG   , KC.NGP              }, [ KC.T, KC.Y, KC.U             ]), # ちゅ
    ({ KC.NGG   , KC.NGI              }, [ KC.T, KC.Y, KC.O             ]), # ちょ
    ({ KC.NGJ   , KC.NGG   , KC.NGH   }, [ KC.D, KC.Y, KC.A             ]), # ぢゃ
    ({ KC.NGJ   , KC.NGG   , KC.NGP   }, [ KC.D, KC.Y, KC.U             ]), # ぢゅ
    ({ KC.NGJ   , KC.NGG   , KC.NGI   }, [ KC.D, KC.Y, KC.O             ]), # ぢょ
    ({ KC.NGD   , KC.NGH              }, [ KC.N, KC.Y, KC.A             ]), # にゃ
    ({ KC.NGD   , KC.NGP              }, [ KC.N, KC.Y, KC.U             ]), # にゅ
    ({ KC.NGD   , KC.NGI              }, [ KC.N, KC.Y, KC.O             ]), # にょ
    ({ KC.NGX   , KC.NGH              }, [ KC.H, KC.Y, KC.A             ]), # ひゃ
    ({ KC.NGX   , KC.NGP              }, [ KC.H, KC.Y, KC.U             ]), # ひゅ
    ({ KC.NGX   , KC.NGI              }, [ KC.H, KC.Y, KC.O             ]), # ひょ
    ({ KC.NGJ   , KC.NGX   , KC.NGH   }, [ KC.B, KC.Y, KC.A             ]), # びゃ
    ({ KC.NGJ   , KC.NGX   , KC.NGP   }, [ KC.B, KC.Y, KC.U             ]), # びゅ
    ({ KC.NGJ   , KC.NGX   , KC.NGI   }, [ KC.B, KC.Y, KC.O             ]), # びょ
    ({ KC.NGM   , KC.NGX   , KC.NGH   }, [ KC.P, KC.Y, KC.A             ]), # ぴゃ
    ({ KC.NGM   , KC.NGX   , KC.NGP   }, [ KC.P, KC.Y, KC.U             ]), # ぴゅ
    ({ KC.NGM   , KC.NGX   , KC.NGI   }, [ KC.P, KC.Y, KC.O             ]), # ぴょ
    ({ KC.NGB   , KC.NGH              }, [ KC.M, KC.Y, KC.A             ]), # みゃ
    ({ KC.NGB   , KC.NGP              }, [ KC.M, KC.Y, KC.U             ]), # みゅ
    ({ KC.NGB   , KC.NGI              }, [ KC.M, KC.Y, KC.O             ]), # みょ
    ({ KC.NGE   , KC.NGH              }, [ KC.R, KC.Y, KC.A             ]), # りゃ
    ({ KC.NGE   , KC.NGP              }, [ KC.R, KC.Y, KC.U             ]), # りゅ
    ({ KC.NGE   , KC.NGI              }, [ KC.R, KC.Y, KC.O             ]), # りょ
    ({ KC.NGM   , KC.NGE   , KC.NGK   }, [ KC.T, KC.H, KC.I             ]), # てぃ
    ({ KC.NGM   , KC.NGE   , KC.NGP   }, [ KC.T, KC.H, KC.U             ]), # てゅ
    ({ KC.NGJ   , KC.NGE   , KC.NGK   }, [ KC.D, KC.H, KC.I             ]), # でぃ
    ({ KC.NGJ   , KC.NGE   , KC.NGP   }, [ KC.D, KC.H, KC.U             ]), # でゅ
    ({ KC.NGM   , KC.NGD   , KC.NGL   }, [ KC.T, KC.O, KC.X, KC.U       ]), # とぅ
    ({ KC.NGJ   , KC.NGD   , KC.NGL   }, [ KC.D, KC.O, KC.X, KC.U       ]), # どぅ
    ({ KC.NGM   , KC.NGR   , KC.NGO   }, [ KC.S, KC.Y, KC.E             ]), # しぇ
    ({ KC.NGM   , KC.NGG   , KC.NGO   }, [ KC.T, KC.Y, KC.E             ]), # ちぇ
    ({ KC.NGJ   , KC.NGR   , KC.NGO   }, [ KC.Z, KC.Y, KC.E             ]), # じぇ
    ({ KC.NGJ   , KC.NGG   , KC.NGO   }, [ KC.D, KC.Y, KC.E             ]), # ぢぇ
    ({ KC.NGV   , KC.NGSCLN, KC.NGJ   }, [ KC.F, KC.A                   ]), # ふぁ
    ({ KC.NGV   , KC.NGSCLN, KC.NGK   }, [ KC.F, KC.I                   ]), # ふぃ
    ({ KC.NGV   , KC.NGSCLN, KC.NGO   }, [ KC.F, KC.E                   ]), # ふぇ
    ({ KC.NGV   , KC.NGSCLN, KC.NGN   }, [ KC.F, KC.O                   ]), # ふぉ
    ({ KC.NGV   , KC.NGSCLN, KC.NGP   }, [ KC.F, KC.Y, KC.U             ]), # ふゅ
    ({ KC.NGV   , KC.NGK   , KC.NGO   }, [ KC.I, KC.X, KC.E             ]), # いぇ
    ({ KC.NGV   , KC.NGL   , KC.NGK   }, [ KC.W, KC.I                   ]), # うぃ
    ({ KC.NGV   , KC.NGL   , KC.NGO   }, [ KC.W, KC.E                   ]), # うぇ
    ({ KC.NGV   , KC.NGL   , KC.NGN   }, [ KC.U, KC.X, KC.O             ]), # うぉ
    ({ KC.NGM   , KC.NGQ   , KC.NGJ   }, [ KC.V, KC.A                   ]), # ゔぁ
    ({ KC.NGM   , KC.NGQ   , KC.NGK   }, [ KC.V, KC.I                   ]), # ゔぃ
    ({ KC.NGM   , KC.NGQ   , KC.NGO   }, [ KC.V, KC.E                   ]), # ゔぇ
    ({ KC.NGM   , KC.NGQ   , KC.NGN   }, [ KC.V, KC.O                   ]), # ゔぉ
    ({ KC.NGM   , KC.NGQ   , KC.NGP   }, [ KC.V, KC.U, KC.X, KC.Y, KC.U ]), # ゔゅ
    ({ KC.NGV   , KC.NGH   , KC.NGJ   }, [ KC.K, KC.U, KC.X, KC.A       ]), # くぁ
    ({ KC.NGV   , KC.NGH   , KC.NGK   }, [ KC.K, KC.U, KC.X, KC.I       ]), # くぃ
    ({ KC.NGV   , KC.NGH   , KC.NGO   }, [ KC.K, KC.U, KC.X, KC.E       ]), # くぇ
    ({ KC.NGV   , KC.NGH   , KC.NGN   }, [ KC.K, KC.U, KC.X, KC.O       ]), # くぉ
    ({ KC.NGV   , KC.NGH   , KC.NGDOT }, [ KC.K, KC.U, KC.X, KC.W, KC.A ]), # くゎ
    ({ KC.NGF   , KC.NGH   , KC.NGJ   }, [ KC.G, KC.U, KC.X, KC.A       ]), # ぐぁ
    ({ KC.NGF   , KC.NGH   , KC.NGK   }, [ KC.G, KC.U, KC.X, KC.I       ]), # ぐぃ
    ({ KC.NGF   , KC.NGH   , KC.NGO   }, [ KC.G, KC.U, KC.X, KC.E       ]), # ぐぇ
    ({ KC.NGF   , KC.NGH   , KC.NGN   }, [ KC.G, KC.U, KC.X, KC.O       ]), # ぐぉ
    ({ KC.NGF   , KC.NGH   , KC.NGDOT }, [ KC.G, KC.U, KC.X, KC.W, KC.A ]), # ぐゎ
    ({ KC.NGV   , KC.NGL   , KC.NGJ   }, [ KC.T, KC.S, KC.A             ]), # つぁ

]

nghenshu1dic = {
    KC.S     : [unicode_string_sequence('()'), KC.LEFT],
    KC.NGS   : [unicode_string_sequence('（）'), KC.LEFT],
    KC.F     : [unicode_string_sequence('「」'), KC.LEFT],
    KC.NGF   : [unicode_string_sequence('「」'), KC.LEFT],
}

ngcomb = { # 連続シフト、組み合わせ
    1: [ # 1キー
        [False, [0      ]], # 0
    ],
    2: [ # 2キー
        [False, [0      ], [1      ]], # 0 1
        [False, [0, 1   ]           ], # 01
    ],
    3: [ # 3キー
        # 連続シフトなし
        [False, [0      ], [1      ], [2      ]], # 0   1   2
        [False, [0, 1   ], [2      ]           ], # 01  2
        [False, [0      ], [1, 2   ]           ], # 0   12
        [False, [0, 1, 2]                      ], # 012
        # 連続シフトあり
        [True,  [0, 1   ], [0, 2   ]           ], # 01  02 : 0が連続シフト
        [True,  [0, 1   ], [1, 2   ]           ], # 01  12 : 1が連続シフト
    ],
    4: [ # 4キー
        # 連続シフトなし
        [False, [0      ], [1      ], [2      ], [3      ]], # 0   1   2   3
        [False, [0, 1   ], [2      ], [3      ]           ], # 01  2   3
        [False, [0      ], [1, 2   ], [3      ]           ], # 0   12  3
        [False, [0      ], [1      ], [2, 3   ]           ], # 0   1   23
        [False, [0, 1, 2], [3      ]                      ], # 012 3
        [False, [0, 1   ], [2, 3   ]                      ], # 01  23
        [False, [0      ], [1, 2, 3]                      ], # 0   123
        # 0の連続シフト
        [True,  [0, 1   ], [0, 2   ], [0, 3   ]           ], # 01  02  03
        [True,  [0, 1   ], [0, 2   ], [3      ]           ], # 01  02  3
        [True,  [0, 1, 2], [0, 3   ]                      ], # 012 03
        [True,  [0, 1   ], [0, 2, 3]                      ], # 01  023
        # 1の連続シフト
        [True,  [0, 1   ], [1, 2   ], [3      ]           ], # 01  12  3
        [True,  [0, 1   ], [1, 2   ], [1, 3   ]           ], # 01  12  13
        [True,  [0      ], [1, 2   ], [1, 3   ]           ], # 0   12  13
        [True,  [0, 1   ], [1, 2, 3]                      ], # 01  123
        [True,  [0, 1, 2], [1, 3   ]                      ], # 012 13
        # 2の連続シフト
        [True,  [0      ], [1, 2   ], [2, 3   ]           ], # 0   12  23
        [True,  [0, 1, 2], [2, 3   ]                      ], # 012 23
    ],
    # 5キーの組み合わせは遅すぎる。4キーでもオーバーフロー処理をすれば正しく変換できてる。
    # 5: [ # 5キー
    #     # 5分割 連続シフトなし
    #     [[0      ], [1      ], [2      ], [3      ], [4      ]], # 0 1 2 3 4
    #     # 4分割 連続シフトなし
    #     [[0, 1   ], [2      ], [3      ], [4      ]           ], # 01  2   3   4
    #     [[0      ], [1, 2   ], [3      ], [4      ]           ], # 0   12  3   4
    #     [[0      ], [1      ], [2, 3   ], [4      ]           ], # 0   1   23  4
    #     [[0      ], [1      ], [2      ], [3, 4   ]           ], # 0   1   2   34
    #     # 3分割 連続シフトなし
    #     [[0, 1, 2], [3      ], [4      ]                      ], # 012 3   4
    #     [[0      ], [1, 2, 3], [4      ]                      ], # 0   123 4
    #     [[0      ], [1      ], [2, 3, 4]                      ], # 0   1   234
    #     [[0, 1   ], [2, 3   ], [4      ]                      ], # 01  23  4
    #     [[0      ], [1, 2   ], [3, 4   ]                      ], # 0   12  34
    #     [[0, 1   ], [2      ], [3, 4   ]                      ], # 01  2   34
    #     # 2分割 連続シフトなし
    #     [[0, 1, 2], [3, 4   ]                                 ], # 012 34
    #     [[0, 1   ], [2, 3, 4]                                 ], # 01  234
    #     # 0の連続シフト
    #     [[0, 1   ], [0, 2   ], [3      ], [4      ]           ], # 01  02  3   4 : 2キー同時
    #     [[0, 1   ], [0, 2   ], [0, 3   ], [4      ]           ], # 01  02  03  4
    #     [[0, 1   ], [0, 2   ], [0, 3   ], [0, 4   ]           ], # 01  02  03  04
    #     [[0, 1, 2], [0, 3, 4]                                 ], # 012 034 : 3キー同時
    #     [[0, 1   ], [0, 2, 3], [4      ]                      ], # 01  023 4
    #     [[0, 1   ], [0, 2, 3], [0, 4   ]                      ], # 01  023 04
    #     [[0, 1   ], [0, 2   ], [0, 3, 4]                      ], # 01  02  034
    #     # 1の連続シフト
    #     [[0, 1   ], [1, 2   ], [3      ], [4      ]           ], # 01  12  3   4 : 2キー同時
    #     [[0, 1   ], [1, 2   ], [1, 3   ], [4      ]           ], # 01  12  13  4
    #     [[0, 1   ], [1, 2   ], [1, 3   ], [1, 4   ]           ], # 01  12  13  14
    #     [[0      ], [1, 2   ], [1, 3   ], [4      ]           ], # 0   12  13  4
    #     [[0      ], [1, 2   ], [1, 3   ], [1, 4   ]           ], # 0   12  13  14
    #     [[0, 1, 2], [1, 3, 4]                                 ], # 012 134 : 3キー同時
    #     [[0, 1, 2], [1, 3   ], [4      ]                      ], # 012 13  4
    #     [[0      ], [1, 2, 3], [1, 4   ]                      ], # 0   123 14
    #     [[0      ], [1, 2   ], [1, 3, 4]                      ], # 0   12  134
    #     # 2の連続シフト
    #     [[0      ], [1, 2   ], [2, 3   ], [4      ]           ], # 0   12  23 4 : 2キー同時
    #     [[0      ], [1      ], [2, 3   ], [2, 4   ]           ], # 0   1   23 24
    #     [[0, 1, 2], [2, 3, 4]                                 ], # 012 234 : 3キー同時
    #     [[0      ], [1, 2   ], [2, 3, 4]                      ], # 0   12  234
    #     [[0      ], [1, 2, 3], [2, 4   ]                      ], # 0   123 24
    #     # 3の連続シフト
    #     [[0      ], [1      ], [2, 3   ], [3, 4   ]           ], # 0   1   23  34 : 2キー
    #     [[0      ], [1, 2, 3], [3, 4   ]                      ], # 0   123 34 : 3キー同時
    # ],
}
