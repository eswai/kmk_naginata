# v15fix版
# KMKのかな定義を書くコード

tanda = <<ETANDA
ゔ|き|て|し|{←}|{→}|{BS}|る|す|へ|@|[  |
ろ|け|と|か|っ  |く  |あ  |い|う|ー|:|]  |
ほ|ひ|は|こ|そ  |た  |な  |ん|ら|れ|\|
ETANDA

shifted = <<ESHIFTED
 ゔ|ぬ|り |ね       |+{←}|+{→}|さ       |よ|え|ゆ|`|{{}|
 せ|め|に |ま       |ち   |や   |の       |も|つ|ふ|*|{}}|
 ほ|ひ|を |、{Enter}|み   |お   |。{Enter}|む|わ|れ|_|
ESHIFTED

mode1l = <<MEND
^{End}    |『』{改行}{↑}|/*ディ*/|^s            |・            ||||||||
……{改行}|(){改行}{↑}  |？{改行}|「」{改行}{↑}|《》{改行}{↑}||||||||
――{改行}|【】{改行}{↑}|！{改行}|{改行}{↓}    |{改行}{←}    |||||||
MEND

mode1r = <<MEND
|||||{Home}      |+{End}{BS}|{vk1Csc079}|{Del}  |{Esc 3}|  |  |
|||||{Enter}{End}|{↑}      |+{↑}      |+{↑ 7}|^i     |  |  |
|||||{End}       |{↓}      |+{↓}      |+{↓ 7}|^u     |  |
MEND

mode2l = <<MEND
{Home}{→}{End}{Del 4}{←}      |^x『^v』{改行}{Space}+{↑}^x|{Home}{改行}{Space 3}{←}|{Space 3}                      |〇{改行}                                ||||||||
{Home}{→}{End}{Del 2}{←}      |^x(^v){改行}{Space}+{↑}^x  |{Home}{改行}{Space 1}{←}|^x「^v」{改行}{Space}+{↑}^x   |^x｜{改行}^v《》{改行}{↑}{Space}+{↑}^x||||||||
　　　×　　　×　　　×{改行 2}|^x【^v】{改行}{Space}+{↑}^x|／{改行}                 |{改行}{End}{改行}「」{改行}{↑}|{改行}{End}{改行}{Space}                |||||||
MEND

mode2r = <<MEND
|||||+{Home}|^x  |^v   |^y      |^z      |  |  |
|||||^c     |{→}|+{→}|+{→ 5} |+{→ 20}|  |  |
|||||+{End} |{←}|+{←}|+{← 5} |+{← 20}|  |
MEND

koyul = <<MEND
|臨兵闘者皆陣烈在前|天狗      |シンイチ  |ネムカケ  ||||||||
三神     |峯        |小鴉      |光太郎    |          ||||||||
火よ、在れ|火の剣   |罵詈雑    |心の闇    |          ||||||||
MEND

koyur = <<MEND
|||||才一      |さくら    |酒田      |          |          |          |          |
|||||鞍馬      |青鬼      |百地      |      |不動金縛りの術|          |
|||||鬼塚      |赤石      |八幡      |          |霊槍      |          |
MEND

eiji    = %w(Q W E R T  Y U I O P  A S D F G  H J K L SCLN  Z X C V B  N M COMM DOT SLSH)
eiji_r  = %w(Y U I O P  H J K L SCLN N M COMM DOT SLSH)
eiji_l  = %w(Q W E R T  A S D F G  Z X C V B)

tanda = tanda.split("|").map{|c| c.strip}
tanda.delete_at(35)
tanda.delete_at(34)
tanda.delete_at(23)
tanda.delete_at(22)
tanda.delete_at(11)
tanda.delete_at(10)

shifted = shifted.split("|").map{|c| c.strip}
shifted.delete_at(35)
shifted.delete_at(34)
shifted.delete_at(23)
shifted.delete_at(22)
shifted.delete_at(11)
shifted.delete_at(10)

kana      = %w(あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん ー 、{Enter} 。{Enter} ゔ)
r_kana    = %w(a i u e o ka ki ku ke ko sa si su se so ta ti tu te to na ni nu ne no ha hi hu he ho ma mi mu me mo ya yu yo ra ri ru re ro wa wo nn - , . vu)

daku      = %w(が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ば び ぶ べ ぼ ゔ)
r_daku    = %w(ga gi gu ge go za zi zu ze zo da di du de do ba bi bu be bo vu)
t_daku    = %w(か き く け こ さ し す せ そ た ち つ て と は ひ ふ へ ほ う)

handaku   = %w(ぱ ぴ ぷ ぺ ぽ)
t_handaku = %w(は ひ ふ へ ほ)
r_handaku = %w(pa pi pu pe po)

kogaki    = %w(ゃ ゅ ょ ぁ ぃ ぅ ぇ ぉ ゎ っ ヶ ヵ)
t_kogaki  = %w(や ゆ よ あ い う え お わ っ け か)
r_kogaki  = %w(xya xyu xyo xa xi xu xe xo xwa xtu xke xka)

kumiawase = []
r_kumiawase = []
kumiawase << %w(しゃ しゅ しょ じゃ じゅ じょ)
r_kumiawase << %w(sya syu syo zya zyu zyo)
kumiawase << %w(きゃ きゅ きょ ぎゃ ぎゅ ぎょ)
r_kumiawase << %w(kya kyu kyo gya gyu gyo)
kumiawase << %w(ちゃ ちゅ ちょ ぢゃ ぢゅ ぢょ)
r_kumiawase << %w(tya tyu tyo dya dyu dyo)
kumiawase << %w(にゃ にゅ にょ)
r_kumiawase << %w(nya nyu nyo)
kumiawase << %w(ひゃ ひゅ ひょ びゃ びゅ びょ ぴゃ ぴゅ ぴょ)
r_kumiawase << %w(hya hyu hyo bya byu byo pya pyu pyo)
kumiawase << %w(みゃ みゅ みょ)
r_kumiawase << %w(mya myu myo)
kumiawase << %w(りゃ りゅ りょ)
r_kumiawase << %w(rya ryu ryo)

gairai = []
r_gairai = []
gairai << %w(てぃ てゅ でぃ でゅ)
r_gairai << %w(thi thu dhi dhu)
gairai << %w(とぅ どぅ)
r_gairai << %w(toxu doxu)
gairai << %w(しぇ ちぇ じぇ ぢぇ)
r_gairai << %w(sye tye zye dye)

gairai << %w(ふぁ ふぃ ふぇ ふぉ ふゅ)
r_gairai << %w(fa fi fe fo fyu)
gairai << %w(いぇ)
r_gairai << %w(ixe)
gairai << %w(うぃ うぇ うぉ ゔぁ ゔぃ ゔぇ ゔぉ ゔゅ)
r_gairai << %w(wi we uxo va vi ve vo vuxyu)
gairai << %w(くぁ くぃ くぇ くぉ くゎ ぐぁ ぐぃ ぐぇ ぐぉ ぐゎ)
r_gairai << %w(kuxa kuxi kuxe kuxo kuxwa guxa guxi guxe guxo guxwa)
# gairai << %w(つぁ つぃ つぇ つぉ)
# r_gairai << %w(tsa tsi tse tso)
gairai << %w(つぁ)
r_gairai << %w(tsa)

kumiawase.flatten!
r_kumiawase.flatten!
gairai.flatten!
r_gairai.flatten!

$kfreq = ['い', 'う', 'ん', 'か', 'の', 'と', 'し', 'た', '、', 'く', 'な', 'て', 'に', 'は', 'こ', 'る', '。', 'が', 'で', 'っ', 'す', 'き', 'ま', 'も', 'つ', 'お', 'ら', 'を', 'さ', 'あ', 'り', 'れ', 'だ', 'せ', 'け', 'じ', 'ー', 'よ', 'ど', 'そ', 'え', 'わ', 'ち', 'み', 'め', 'ば', 'や', 'ひ', 'ろ', 'ほ', 'しょ', 'ぶ', 'ふ', 'ね', 'ご', 'じょ', 'げ', 'しゅ', 'む', 'きょ', 'ず', 'ぎ', 'しゃ', 'ちょ', 'び', 'ざ', 'ぐ', 'ぜ', 'へ', 'べ', 'ゆ', 'じゅ', 'ぼ', 'ぷ', 'りょ', 'ぞ', 'ぱ', 'きゅ', 'ちゅ', 'ぎょ', 'ぽ', 'にゅ', 'ひょ', 'づ', 'じゃ', 'ちゃ', 'ぬ', 'てぃ', 'ぴ', 'りゅ', 'ぺ', 'きゃ', 'ふぁ', 'でぃ', 'ぁ', 'しぇ', 'びょ', 'りゃ', 'ふぃ', 'ちぇ', 'ぎゃ', 'うぇ', 'なぁ', 'ぃ', 'ふぇ', 'ぴょ', 'ぴゅ', 'じぇ', 'ふぉ', 'ぇ', 'ゔ', 'びゅ', 'ぢ', 'みょ', 'ひゃ', 'みゅ', 'ぎゅ', 'ぉ', 'みぃ', 'ゔぁ', 'うぃ', 'にょ', 'ねぇ', 'ぅ', 'まぁ', 'ゅ', 'ねぃ', 'でゅ', 'みゃ', 'にゃ', 'うぉ', 'かぁ', 'とぅ', 'くぉ', 'ひゅ', 'りぃ', 'はぁ', 'へぇ', 'だぁ', 'ぎぃ', 'どぅ', 'しぃ', 'ゔぃ', 'おぉ', 'ゔぇ', 'てぇ', 'やぁ', 'ぴゃ', 'びゃ', 'あぁ', 'つぁ', 'もぉ', 'ゃぁ', 'つぃ', 'ふゅ', 'ぅぃ', 'さぁ', 'よぉ', 'ぬぁ', 'げぇ', 'ぁぁ', 'たぁ', 'わぁ', 'らぁ', 'にぇ', 'ぉぉ', 'ぉぃ', 'ょ', 'ぃぃ', 'つぇ', 'にぃ', 'ぅぅ', 'ふぅ', 'るぅ', 'えぇ', 'じぃ', 'ぜぃ', 'びぃ', 'べぇ', 'とぉ', 'つぉ', 'ぞぉ', 'ゃ', 'るぁ', 'きぃ', 'ちぃ', 'すぃ', 'ぬぃ', 'いぃ', 'うぅ', 'よぅ', 'むぅ', 'ぐぅ', 'くぅ', 'っぅ', 'のぅ', 'ぜぇ', 'でぇ', 'やぇ', 'けぇ', 'ひぇ', 'せぇ', 'きぇ', 'さぇ', 'まぇ', 'ゔぉ', 'ぢゃ', 'ゎ', ]

def teigi(a, b, c, prefix=nil, suffix=nil)
  _a = prefix ? [sprintf("KC.NG%-4s", prefix)] : []
  _a += [a].flatten.map{|k| sprintf("KC.NG%-4s", k)}
  _a += [sprintf("KC.NG%-4s", suffix)] if suffix
  _b = []
  for i in 0..(b.length - 1)
    _b.push sprintf("KC.%-1s", b[i].upcase)
  end
  r = sprintf("    ({ %-31s}", _a.join(", "))
  r+= sprintf(", [ %-29s]", _b.join(", ")) + "), # #{c}"
  r
end

norder = []

puts "  # 清音"
kana.each_with_index do |k, i|
  j = tanda.index(k)
  if j && j >= 0
    norder << [k, teigi(eiji[j], r_kana[i], k)]
  end
  j = shifted.index(k)
  if j && j >= 0
    norder << [k, teigi(eiji[j], r_kana[i], k, "SFT")]
  end
end

puts
puts "  # 濁音"
daku.each_with_index do |k, i|
  j = tanda.index(t_daku[i]) || shifted.index(t_daku[i])
  if j && j >= 0
    if eiji_r.index(eiji[j])
      norder << [k, teigi(eiji[j], r_daku[i], k, "F")]
      # puts teigi(eiji[j], r_daku[i], k + "(冗長)", "B_F|", "|B_SHFT")
    else
      norder << [k, teigi(eiji[j], r_daku[i], k, "J")]
      # puts teigi(eiji[j], r_daku[i], k + "(冗長)", "B_J|", "|B_SHFT")
    end
  end
end

puts
puts "  # 半濁音"
handaku.each_with_index do |k, i|
  j = tanda.index(t_handaku[i]) || shifted.index(t_handaku[i])
  if j && j >= 0
    if eiji_r.index(eiji[j])
      norder << [k, teigi(eiji[j], r_handaku[i], k, "V")]
      # puts teigi(eiji[j], r_handaku[i], k + "(冗長)", "B_V|", "|B_SHFT")
    else
      norder << [k, teigi(eiji[j], r_handaku[i], k, "M")]
      # puts teigi(eiji[j], r_handaku[i], k + "(冗長)", "B_M|", "|B_SHFT")
    end
  end
end

puts
puts "  # 小書き"
kogaki.each_with_index do |k, i|
  j = tanda.index(k)
  if j && j >= 0
    norder << [k, teigi(eiji[j], r_kogaki[i], k)]
    next
  end
  j = shifted.index(k)
  if j && j >= 0
    norder << [k, teigi(eiji[j], r_kogaki[i], k, "SFT")]
    next
  end

  j = tanda.index(t_kogaki[i]) || shifted.index(t_kogaki[i])
  if j && j >= 0
    norder << [k, teigi(eiji[j], r_kogaki[i], k, "Q")]
    # puts teigi(eiji[j], r_kogaki[i], k, "B_Q|B_SHFT|")
    # puts teigi(eiji[j], r_kogaki[i], k, "B_V|B_M|")
    # puts teigi(eiji[j], r_kogaki[i], k + "(冗長)", "B_V|B_M|", "|B_SHFT")
  end
end

puts
puts "  # 清音拗音 濁音拗音 半濁拗音"
kumiawase.each_with_index do |k, i|
  j = tanda.index(k[0])
  if j && j >= 0
    e0 = eiji[j]
  end
  unless e0
    j = shifted.index(k[0])
    if j && j >= 0
      e0 = eiji[j]
    end
  end
  unless e0
    l = daku.index(k[0])
    if l && l >= 0
      j = tanda.index(t_daku[l]) || shifted.index(t_daku[l])
      if j && j >= 0
        if eiji_r.index(eiji[j])
          e0 = ["F", eiji[j]]
        else
          e0 = ["J", eiji[j]]
        end
      end
    end
  end
  unless e0
    l = handaku.index(k[0])
    if l && l >= 0
      j = tanda.index(t_handaku[l]) || shifted.index(t_handaku[l])
      if j && j >= 0
        if eiji_r.index(eiji[j])
          e0 = ["V", eiji[j]]
        else
          e0 = ["M", eiji[j]]
        end
      end
    end
  end

  l = kogaki.index(k[1])
  j = tanda.index(t_kogaki[l]) || shifted.index(t_kogaki[l])
  if j && j >= 0
    e1 = eiji[j]
    norder << [k, teigi([e0, e1], r_kumiawase[i], k)]
    # puts teigi([e0, e1], r_kumiawase[i], k + "(冗長)", "", "|B_SHFT")
  end
end

puts
puts "  # 清音外来音 濁音外来音"
gairai.each_with_index do |k, i|
  j = tanda.index(k[0]) || shifted.index(k[0])
  if j && j >= 0
    if eiji_r.index(eiji[j])
      e0 = ["V", eiji[j]]
    else
      e0 = ["M", eiji[j]]
    end
  end
  unless e0
    l = daku.index(k[0])
    if l && l >= 0
      j = tanda.index(t_daku[l]) || shifted.index(t_daku[l])
      if j && j >= 0
        if eiji_r.index(eiji[j])
          e0 = ["F", eiji[j]]
        else
          e0 = ["J", eiji[j]]
        end
      end
    end
  end

  l = kogaki.index(k[1])
  j = tanda.index(t_kogaki[l]) || shifted.index(t_kogaki[l])
  if j && j >= 0
    e1 = eiji[j]
    norder << [k, teigi([e0, e1], r_gairai[i], k)]
    # puts teigi([e0, e1], r_gairai[i], k + "(冗長)", "", "|B_SHFT")
  end
end

def kindex(a)
  b = a.gsub('{Enter}', '')
  o = $kfreq.index(b) || 1000
end

# norder.sort!{|a, b| kindex(a[0]) <=> kindex(b[0])}

puts norder.map{|x| x[1]}

# 編集モード

$henshu = {
  "+{End}" => ["register_code(KC_LSFT);", "ng_end();", "unregister_code(KC_LSFT);"],
  "+{Home}" => ["register_code(KC_LSFT);", "ng_home();", "unregister_code(KC_LSFT);"],
  "+{← 20}" => ["register_code(KC_LSFT);", "ng_left(20);", "unregister_code(KC_LSFT);"],
  "+{← 5}" => ["register_code(KC_LSFT);", "ng_left(5);", "unregister_code(KC_LSFT);"],
  "+{←}" => ["register_code(KC_LSFT);", "ng_left(1);", "unregister_code(KC_LSFT);"],
  "+{↑ 7}" => ["register_code(KC_LSFT);", "ng_up(7);", "unregister_code(KC_LSFT);"],
  "+{↑}" => ["register_code(KC_LSFT);", "ng_up(1);", "unregister_code(KC_LSFT);"],
  "+{→ 20}" => ["register_code(KC_LSFT);", "ng_right(20);", "unregister_code(KC_LSFT);"],
  "+{→ 5}" => ["register_code(KC_LSFT);", "ng_right(5);", "unregister_code(KC_LSFT);"],
  "+{→}" => ["register_code(KC_LSFT);", "ng_right(1);", "unregister_code(KC_LSFT);"],
  "+{↓ 7}" => ["register_code(KC_LSFT);", "ng_down(7);", "unregister_code(KC_LSFT);"],
  "+{↓}" => ["register_code(KC_LSFT);", "ng_down(1);", "unregister_code(KC_LSFT);"],
  "/*ディ*/" => [""],
  "^c" => ["ng_copy();"],
  "^i" => ["ng_katakana();"],
  "^s" => ["ng_save();"],
  "^u" => ["ng_hiragana();"],
  "^v" => ["ng_paste();"],
  "^x" => ["ng_cut();"],
  "^y" => ["ng_redo();"],
  "^z" => ["ng_undo();"],
  "^{End}" => ["ng_eof();"],
  "{BS}" => ["tap_code(KC_BSPC);"],
  "{Del 1}" => ["tap_code(KC_DEL);"],
  "{Del 2}" => ["tap_code(KC_DEL);"] * 2,
  "{Del 3}" => ["tap_code(KC_DEL);"] * 3,
  "{Del 4}" => ["tap_code(KC_DEL);"] * 4,
  "{Del}" => ["tap_code(KC_DEL);"],
  "{End}" => ["ng_end();"],
  "{Enter}" => ["tap_code(KC_ENT);"],
  "{Esc 3}" => ["tap_code(KC_ESC);"] * 3,
  "{Home}" => ["ng_home();"],
  "{Space 1}" => ["tap_code(KC_SPC);"],
  "{Space 3}" => ["tap_code(KC_SPC);"] * 3,
  "{Space}" => ["tap_code(KC_SPC);"],
  "{vk1Csc079}" => ["ng_saihenkan();"], # 再変換
  "{← 5}" => ["ng_left(5);"],
  "{←}" => ["ng_left(1);"],
  "{↑}" => ["ng_up(1);"],
  "{→ 5}" => ["ng_right(5);"],
  "{→}" => ["ng_right(1);"],
  "{↓}" => ["ng_down(1);"],
  "{改行 2}" => ["tap_code(KC_ENT);"] * 2,
  "{改行}" => ["tap_code(KC_ENT);"],
 }
 
qwerty    = %w(Q W E R T  Y U I O P NO NO A S D F G  H J K L SCLN NO NO Z X C V B  N M COMM DOT SLSH NO)

mode1l = mode1l.split("|").map{|x| x.strip}
mode1r = mode1r.split("|").map{|x| x.strip}
mode2l = mode2l.split("|").map{|x| x.strip}
mode2r = mode2r.split("|").map{|x| x.strip}


$hcase = []
$hkey = []

def outputHenshu(pk, m, k)
  $hcase << "    case #{pk}|B_#{k}: # #{m}"
  v = m.scan(/((?:\^?\+?{.+?})|(?:\^.)|(?:[^{}\^\+]+))/).flatten
  d = []
  uc = false
  v.each do |i|
    if $henshu.key? i
      if i == "{改行}" && uc
        uc = false
        next
      end
      d << $henshu[i]
    else
      d << "ng_send_unicode_string_P(PSTR(\"#{i}\"));"
      uc = true
    end
  end
  $hcase += d.flatten.map{|x| "      #{x}"}
  $hcase << "      henshu_done = true;"
  $hcase << "      return true;"
  $hcase << "      break;"
  $hkey << "  {.key = #{pk}|B_#{k}}, # #{m}"
end

qwerty.each_with_index do |k, i|
  m =  mode1l[i]
  pk = "B_J|B_K"
  outputHenshu(pk, m, k) unless m == ""
end

qwerty.each_with_index do |k, i|
  m =  mode1r[i]
  pk = "B_D|B_F"
  outputHenshu(pk, m, k) unless m == ""
end

qwerty.each_with_index do |k, i|
  m =  mode2l[i]
  pk = "B_M|B_COMM"
  outputHenshu(pk, m, k) unless m == ""
end

qwerty.each_with_index do |k, i|
  m =  mode2r[i]
  pk = "B_C|B_V"
  outputHenshu(pk, m, k) unless m == ""
end

puts "# 編集モード"
puts $hkey
puts $hcase

$hkey = []
$hcase = []

koyul = koyul.split("|").map{|x| x.strip}
koyur = koyur.split("|").map{|x| x.strip}

qwerty.each_with_index do |k, i|
  m =  koyul[i]
  pk = "B_U|B_I"
  outputHenshu(pk, m, k) unless m == ""
end

qwerty.each_with_index do |k, i|
  m =  koyur[i]
  pk = "B_E|B_R"
  outputHenshu(pk, m, k) unless m == ""
end


puts "# 固有名詞"
puts $hkey
puts $hcase