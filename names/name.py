days: dict = {}
dates: dict = {}
commercial_keys: list = ['commercial', 'times', 'content_type', 'file_id', 'file_unique_id', 'link', 'button_text']
publishing: list = ['not_published', 'will_be_published', 'published']
stories_id: list = []
time_format = "%Y-%m-%d %H:%M:%S.%f"
utc: int = 7
count: int = 6
banned_users: list = []
hiragana: dict = {'あ': 'а', 'い': 'и', 'う': 'у', 'え': 'э', 'お': 'о',
                  'か': 'ка', 'き': 'ки', 'く': 'ку', 'け': 'кэ', 'こ': 'ко',
                  'さ': 'са', 'し': 'си', 'す': 'су', 'せ': 'сэ', 'そ': 'со'}
# 'た': 'тa', 'ち': 'ти', 'つ': 'цу', 'て': 'тэ', 'と': 'то',
# 'な': 'на', 'に': 'ни', 'ぬ': 'ну', 'ね': 'нэ', 'の': 'но',
# 'は': 'хa', 'ひ': 'хи', 'ふ': 'фу', 'へ': 'хэ', 'эほ': 'хо',
# 'ま': 'мa', 'み': 'ми', 'む': 'му', 'め': 'мэ', 'も': 'мо',
# 'や': 'я', 'ゆ': 'ю', 'よ': 'ё',
# 'ら': 'рa', 'り': 'ри', 'る': 'ру', 'れ': 'рэ', 'ろ': 'ро',
# 'わ': 'вa', 'ん': 'н', 'を': 'во/о'}
