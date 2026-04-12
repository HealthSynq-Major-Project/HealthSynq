import os
import pandas as pd
import numpy as np
import random
import warnings
from collections import Counter
from IPython.display import display
from sqlalchemy import create_engine
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)


warnings.filterwarnings('ignore')
pd.set_option('display.max_colwidth', 55)
pd.set_option('display.float_format', '{:.1f}'.format)
# print('✅ Imports done')
# DATASET_PATH = 'Anuvaad_INDB_2024.xlsx'  
# Replace with your actual Render external DB URL
PER100G = ['food_code','food_name','servings_unit','energy_kcal','carb_g','protein_g','fat_g','freesugar_g','fibre_g']
PER_SRV = ['unit_serving_energy_kcal','unit_serving_carb_g','unit_serving_protein_g',
           'unit_serving_fat_g','unit_serving_freesugar_g','unit_serving_fibre_g']
DATABASE_URL = "postgresql://ritik:UXhJKATfH6Bk4qLkD1Q7eWzeS7g59Wa3@dpg-d7dpr8d7vvec73eule1g-a.oregon-postgres.render.com/healthsyncq_diet_dataset"


engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}   # 🔥 required for Render
)
# Load full table
df = pd.read_sql("SELECT * FROM food_data", engine)

df.head()

raw = pd.read_sql("SELECT * FROM food_data", engine)
df  = raw[PER100G + PER_SRV].copy()
df['food_name']     = df['food_name'].str.strip()
df['servings_unit'] = df['servings_unit'].fillna('serving').astype(str)
df = df.dropna(subset=PER_SRV).reset_index(drop=True)
df = df.rename(columns={
    'unit_serving_energy_kcal': 'srv_kcal', 'unit_serving_carb_g':      'srv_carb',
    'unit_serving_protein_g':   'srv_protein','unit_serving_fat_g':       'srv_fat',
    'unit_serving_freesugar_g': 'srv_sugar', 'unit_serving_fibre_g':     'srv_fibre',
})
df = df[df['srv_kcal'] <= 900].reset_index(drop=True)
# print(f'Loaded {len(df)} food items')
HARD_REMOVE = [
   r'\bcooler\b',r'lem-o',r'\biced tea\b',r'\bgin\b',r'\bvodka\b',
    r'whiskey',r'\brum\b',r'\bbeer\b',r'\bwine\b',r'\bpunch\b',r'\bnog\b',r'smoothie',
    r'\bsoup\b',r'\bstock\b',r'\bbroth\b',r'\bconsomm[eé]\b',
    r'\bbaby\b',r'\binfant\b',r'shishu',r'amylase',r'\bpowder\b',r'\bformula\b',r'\bsupplement\b',
    r'\bburfi\b',r'\bbarfi\b',r'\bladoo\b',r'\bpeda\b',r'\bmodak\b',r'\bchikki\b',
    r'peanut brittle',r'\bice cream\b',r'\bcake\b',r'\bpastry\b',r'\bpudding\b',
    r'\bbiscuit\b',r'\bcookie\b',r'\bpickle\b',r'\baachar\b',r'\bketchup\b',r'pickled mustard',
    r'\bjam\b',r'\bjelly\b',r'\bicing\b',r'\bgravy for\b',r'\bchips\b',r'\bpremix\b',
    r'\bspaghetti\b',r'\blasagne\b',r'\bpasta\b',r'\bnoodles\b',r'\bchowmein\b',r'\bpancake\b',
    r'\byakhni\b',r'\bwater\b',r'egg halwa',
    r'\bsouffle\b',r'\bpie\b',r'\bdrop\b',r'\bmathri\b',r'\bpuff\b',r'\bchop\b',
    r'buttermilk biscuit',
]
mask = df['food_name'].str.lower().str.contains('|'.join(HARD_REMOVE), regex=True)
df = df[~mask].reset_index(drop=True)
# print(f'After cleaning: {len(df)} items')
NONVEG_KW = ['chicken','mutton','fish','prawn','keema','lamb','beef','pork',
             'crab','lobster','tuna','salmon','sardine','mackerel','shrimp',
             'meat ball','meatball','minced meat','scotch egg',
             'boti']         
EGG_KW    = ['boiled egg','fried egg','poached egg','scrambled egg','omelette',
             'omlet','egg curry','egg bhujia','anda bhujia','deviled egg',
             'baked egg','egg cutlet','egg sandwich','egg and tomato','egg pakora']
VEG_KOFTA = ['pea kofta','spinach kofta','paneer kofta','lotus stem kofta',
             'raw banana kofta','cauliflower kofta','cabbage kofta','lauki kofta',
             'ghiya kofta','vegetarian egg kofta','vegetarian nargisi kofta',
             'potato kofta','yam kofta','jackfruit kofta','spinach paneer kofta']

def classify_diet(name):
    n = name.lower()
    if any(k in n for k in VEG_KOFTA): return 'veg'
    if any(k in n for k in NONVEG_KW): return 'nonveg'
    if any(k in n for k in EGG_KW):    return 'egg'
    return 'veg'

def diet_filter(frame, diet):
    if diet == 'veg':
        return frame[frame['diet_type'] == 'veg']
    if diet == 'egg':
        return frame[frame['diet_type'].isin(['veg','egg'])]
    if diet == 'nonveg':
        return frame[frame['diet_type'].isin(['veg','egg','nonveg'])]
    return frame

ROLE_KW = {
    'roti': ['chapati','roti','parantha','paratha','naan','phulka','kulcha','thepla',
             'makki ki roti','bajra roti','jowar roti','akki roti','tandoori roti',
             'missi roti','laccha','paushtik roti','soya roti','puranpoli'
             ],
    'dal':  ['washed moong dal','washed urad dal','mixed dal','whole moong','whole masoor',
             'whole moth','whole urad','moti mahal dal','rajmah curry','kidney bean curry',
             'sambar','lobia curry','soyabean curry','black channa curry','chickpeas curry',
             'channa dal with','split bengal gram with','rajma','chole','chhole','arhar',
             'toor dal','moong ki dal','masoor ki dal','paneer curry','paneer masala','shahi paneer',
             'methi malai paneer','urad ki dal','moth ki dal',
             'dal makhani','matar paneer',
             'paneer butter masala','palak paneer','mushroom matar','matar mushroom','dal tadka','dal fry','panchmel dal','kadhai paneer','paneer lababdar','paneer in butter','veg paneer stew',
             'paneer stuffed cheela','paneer shaslik'],
    'sabzi':['aloo gobhi','aloo methi','aloo matar','aloo baingan','aloo palak',
             'shimla mirch aloo','sookhe aloo','dum aloo','bhindi','karela','lauki',
             'tinda','parval','baingan ka bhartha','brinjal bhartha',
             'cabbage and peas','pattagobhi aur matar','carrot and fenugreek','gajar methi',
             'beans with coconut','cauliflower with coconut','sarson ka saag','mustard greens',
             'mixed vegetable curry','mix veg','tofu','pea vadi curry','lotus stem curry','creamed spinach',
             'stuffed okra','bharwa bhindi','stuffed bottle gourd','stuffed ghiya',
             'peas brinjal','matar baingan','okra fry','bhindi sabzi','bhindi subji',
             'stuffed bittergourd','bharwa karela','spinach paneer','kofta curry'
             ],
    'curd': ['curd','dahi','yogurt','raita','chaas','buttermilk','shrikhand','mishti doi',
             'cucumber raita','mint raita','peanut raita','carrot and spinach raita',
             'tomato onion raita','grapes raita','bottle gourd raita','sprouted moong raita',
             'banana raita','sweet raita'],
    'protein_nonveg': [
             # Egg items
             'boiled egg','fried egg','poached egg','scrambled egg','stuffed egg omelette',
             'baked egg','deviled egg','egg curry','egg bhujia','indian style egg bhujia',
             # Chicken
             'chicken curry','butter chicken','tandoori chicken','chicken kebab','chilli chicken',
             'afghani chicken','handi chicken','lemon chicken','roast chicken','shahi chicken',
             'tomato chicken','creamy chicken','ginger chicken','chicken korma','chicken stew',
             'chicken manchurian','cajun chicken','fried chicken','broccoli chicken',
             'chicken and tomato','chicken sweet and sour',
             # Fish
             'fish curry','fried fish','tomato fish','baked fish','fish tikka','tandoori fish',
             'hariyali fish','lemon butter fish','bengal fish curry','fish in coconut milk',
             'crispy baked fish','fish finger','fish orly',
             # Seafood / other
             'prawn curry','baked stuffed fish',
             # Mutton/keema
             'spinach mutton','mutton do piaza','mutton korma','kashmiri mutton',
             'keema kofta curry','shahi keema kofta','minced meat ball curry',
             'nargisi kofta','pea keema curry'],
    'rice': ['boiled rice','plain rice','steamed rice','biryani','biriyani','pulao',
             'fried rice','pongal','curd rice','lemon rice','tamarind rice','khichdi','khichri'],
    'snack':['sandwich','toast','dhokla','khaman','pakora','pakoda','tikki',
             'upma','cutlet','chaat','seekh kebab','kebab','roll','pin wheel'],
    'breakfast_carb': ['oats','cornflakes','porridge','daliya','sheera','vermicelli upma',
                       'poha with curd','semolina idli','instant idli','idli','dosa','uttapam','appam']
}
def assign_role(name):
    n = name.lower()
    for role in ['roti','dal','sabzi','curd','protein_nonveg','snack','breakfast_carb','rice']:
        for kw in ROLE_KW[role]:
            if kw in n:
                if role == 'dal' and any(r in n for r in ['parantha','paratha','poori','puri']):
                    return 'roti'
                if kw == 'kofta curry' and classify_diet(name) == 'nonveg':
                    return 'protein_nonveg'
                return role
    return 'other'

def assign_grain(name):
    n = name.lower()
    if any(k in n for k in ['makki','bajra','jowar','ragi','millet','sorghum','maize porridge']): return 'millet'
    if any(k in n for k in ['oats','cornflakes','oatmeal']): return 'oats'
    if any(k in n for k in ['rice','biryani','biriyani','pulao','pongal','idli','dosa','appam','uttapam','khichdi','khichri']): return 'rice'
    if any(k in n for k in ['daliya','semolina','suji','rava','vermicelli','sheera']): return 'semolina'
    if any(k in n for k in ['roti','chapati','paratha','parantha','naan','thepla','laccha','puranpoli','bhatura','phulka','kulcha']): return 'wheat'
    return 'other'

def assign_subcat(row):
    name = row['food_name'].lower(); role = row['food_role']
    if role == 'dal':
        if any(k in name for k in ['moong']): return 'moong'
        if any(k in name for k in ['urad','moti mahal']): return 'urad'
        if any(k in name for k in ['masoor']): return 'masoor'
        if any(k in name for k in ['moth']): return 'moth'
        if any(k in name for k in ['rajma','rajmah','kidney']): return 'rajma'
        if any(k in name for k in ['chole','chhole','chickpeas','black channa']): return 'chana'
        if any(k in name for k in ['lobia']): return 'lobia'
        if any(k in name for k in ['soya','soyabean']): return 'soya'
        if any(k in name for k in ['arhar','toor']): return 'arhar'
        if any(k in name for k in ['sambar']): return 'sambar'
        return 'mixed'
    if role == 'sabzi':
        if any(k in name for k in ['paneer','tofu','soya']): return 'paneer'
        if any(k in name for k in ['aloo','potato','dum']): return 'potato'
        if any(k in name for k in ['palak','spinach','sarson','saag','methi']): return 'leafy'
        if any(k in name for k in ['bhindi','karela','lauki','tinda','parval','okra']): return 'gourd'
        if any(k in name for k in ['matar','peas','beans']): return 'legume'
        if any(k in name for k in ['baingan','brinjal']): return 'brinjal'
        return 'other_veg'
    if role == 'curd':
        if any(k in name for k in ['mint','pudina','cucumber','tomato','onion']): return 'savory'
        if any(k in name for k in ['peanut','moong','vegetable','salad']): return 'protein_raita'
        if any(k in name for k in ['banana','grapes','sweet']): return 'sweet'
        if any(k in name for k in ['chaas','buttermilk']): return 'liquid'
        if any(k in name for k in ['spinach','carrot','bottle gourd','ghiya']): return 'veggie'
        return 'plain'
    if role == 'snack':
        if any(k in name for k in ['sandwich','toast']): return 'sandwich'
        if any(k in name for k in ['dhokla','khaman']): return 'steamed'
        if any(k in name for k in ['upma','poha']): return 'cooked_grain'
        if any(k in name for k in ['pakora','pakoda','tikki']): return 'fried'
        if any(k in name for k in ['kebab','cutlet']): return 'protein'
        if any(k in name for k in ['salad','sprout','chat']): return 'salad'
        return 'other'
    if role == 'protein_nonveg':
        if any(k in name for k in NONVEG_KW): return 'meat'
        if any(k in name for k in EGG_KW): return 'egg'
        return 'protein'
    return 'other'

def classify_protein_subtype(name):
    n = name.lower()
    if any(k in n for k in NONVEG_KW):
        return 'meat'
    if any(k in n for k in EGG_KW):
        return 'egg'
    return 'na'

df['diet_type']      = df['food_name'].apply(classify_diet)
df['food_role']      = df['food_name'].apply(assign_role)
df['grain_category'] = df['food_name'].apply(assign_grain)
df['food_subcat']    = df.apply(assign_subcat, axis=1)
df['protein_subtype'] = df['food_name'].apply(classify_protein_subtype)
df.loc[df['food_role'] != 'protein_nonveg', 'protein_subtype'] = 'na'

GROUP_PENALTY = {
    'refined': (['maida','white rice','refined','plain rice','boiled rice','bhatura','poori','puri','naan'], +0.8),
    'whole':   (['whole wheat','multigrain','oats','daliya','brown','whole moong','whole masoor','whole urad','whole moth','rajma','chole'], -0.5),
    'sugar':   (['sweet','meetha','meethi'], +1.0),
    'veg':     (['sabzi','bhaji','spinach','palak','gobhi','bhindi','karela','saag'], -0.4),
    'dairy':   (['curd','dahi','raita','yogurt','paneer'], -0.2),
}

def food_group_penalty(name):
    n, p = name.lower(), 0.0
    for _, (kws, val) in GROUP_PENALTY.items():
        if any(kw in n for kw in kws): p += val
    return p

df['gs_raw'] = 0.6*df['srv_carb'] + 1.8*df['srv_sugar'] - 1.2*df['srv_fibre'] - 0.8*df['srv_protein'] - 0.3*df['srv_fat']
df['gs_adj'] = df['gs_raw'] + df['food_name'].apply(food_group_penalty)
mu, sig = df['gs_adj'].mean(), df['gs_adj'].std() + 1e-9
df['gs_z']           = (df['gs_adj'] - mu) / sig
df['glycemic_score'] = 1 / (1 + np.exp(-df['gs_z']))

def norm(s): return (s - s.min()) / (s.max() - s.min() + 1e-9)

df['composite_score'] = (
    - 0.40 * norm(df['srv_carb'])
    - 0.30 * df['glycemic_score']
    + 0.20 * norm(df['srv_protein'])
    + 0.10 * norm(df['srv_fibre'])
    - 0.10 * norm(df['srv_sugar'])
)
# print(f'GI score  : {df["glycemic_score"].min():.3f}–{df["glycemic_score"].max():.3f}')
# print(f'Composite : {df["composite_score"].min():.3f}–{df["composite_score"].max():.3f}')

SLOT_MAP = {
    'roti':           ['breakfast','lunch','dinner'],
    'dal':            ['lunch','dinner'],
    'sabzi':          ['lunch','dinner'],
    'curd':           ['breakfast','lunch','dinner','snack'],  # dinner: raita valid
    'protein_nonveg': ['breakfast','lunch','dinner','snack'],
    'rice':           ['lunch','dinner'],
    'snack':          ['breakfast','snack'],
    'breakfast_carb': ['breakfast'],
    'other':          [],
}
df['valid_slots'] = df['food_role'].map(SLOT_MAP)
pool = df.explode('valid_slots').dropna(subset=['valid_slots']).rename(columns={'valid_slots':'meal_slot'}).reset_index(drop=True)
# print('Pool size per slot:'); print(pool['meal_slot'].value_counts())

def glucose_status(g):
    if g < 100:  return 'Normal'
    if g < 126:  return 'Pre-diabetic'
    if g <= 180: return 'Diabetic'
    if g <= 250: return 'High glucose'
    return 'Very high glucose'

def get_constraints(glucose_mg_dl, daily_kcal):
    splits = {'breakfast':0.25,'lunch':0.35,'dinner':0.30,'snack':0.10}
    if glucose_mg_dl < 100:    carbs={'breakfast':70,'lunch':90,'dinner':80,'snack':35}; gs_base=0.72
    elif glucose_mg_dl < 126:  carbs={'breakfast':55,'lunch':70,'dinner':60,'snack':25}; gs_base=0.65
    elif glucose_mg_dl <= 180: carbs={'breakfast':40,'lunch':55,'dinner':45,'snack':20}; gs_base=0.60
    elif glucose_mg_dl <= 250: carbs={'breakfast':35,'lunch':49,'dinner':40,'snack':18}; gs_base=0.57
    else:                      carbs={'breakfast':30,'lunch':43,'dinner':35,'snack':15}; gs_base=0.54
    return {slot: {'kcal_target':round(daily_kcal*frac,1), 'carb_cap':carbs[slot],
                   'gs_cap':gs_base+(0.10 if slot=='breakfast' else 0.0),
                   'kcal_lo':round(daily_kcal*frac*0.88,1), 'kcal_hi':round(daily_kcal*frac*1.15,1)}
            for slot,frac in splits.items()}

# print(f"{'Glucose':>6}  {'Status':<20} B   L   D   GI-cap")
# for g in [90, 115, 150, 200, 260]:
#     c = get_constraints(g, 2400)
#     print(f"{g:6d}  {glucose_status(g):<20} {c['breakfast']['carb_cap']:2g}g {c['lunch']['carb_cap']:2g}g {c['dinner']['carb_cap']:2g}g  ≤{c['lunch']['gs_cap']:.2f}")

OUTPUT_COLS = ['food_name','food_role','food_subcat','grain_category','serving_unit',
               'portions','kcal','carb_g','protein_g','fat_g','fibre_g','glycemic_score','composite_score']
MIN_SRV = {'roti':1,'dal':1,'sabzi':1,'curd':1,'protein_nonveg':1,'snack':1,'breakfast_carb':1,'rice':1,'other':1}
MAX_SRV = {'roti':3,'dal':2,'sabzi':2,'curd':1,'protein_nonveg':2,'snack':2,'breakfast_carb':3,'rice':2,'other':1}

TOP_N         = 5
FAMILY_CNT_P  = 0.15
RECENCY_P     = 0.45
GRAIN_P       = 0.20
COOLDOWN_N    = 4

VALID_RULES = {
    'breakfast': ([{'roti','rice','breakfast_carb','snack'}], 'needs carb'),
    'lunch':     ([{'roti','rice'}, {'dal','protein_nonveg'}, {'sabzi','curd','dal'}], 'carb+protein+veg'),
    'dinner':    ([{'roti','rice'}, {'dal','protein_nonveg','sabzi'}, {'sabzi','curd','dal'}], 'carb+(dal/sabzi)+veg'),
    'snack':     ([{'snack','curd','protein_nonveg'}], 'needs snack'),
}

def validate_meal(meal, slot):
    if meal.empty: return False
    roles = set(meal['food_role'])
    rules, _ = VALID_RULES.get(slot, ([set()], ''))
    return all(bool(roles & g) for g in rules)

def _make_item(row, role, portions):
    return {'food_name':row['food_name'], 'food_role':role, 'food_subcat':row.get('food_subcat','other'),
            'grain_category':row.get('grain_category','other'), 'serving_unit':row['servings_unit'],
            'portions':portions, 'kcal':round(row['srv_kcal']*portions,1), 'carb_g':round(row['srv_carb']*portions,1),
            'protein_g':round(row['srv_protein']*portions,1), 'fat_g':round(row['srv_fat']*portions,1),
            'fibre_g':round(row['srv_fibre']*portions,1), 'glycemic_score':round(row['glycemic_score'],3),
            'composite_score':round(row['composite_score'],3), '_unit_kcal':row['srv_kcal'], '_unit_carb':row['srv_carb']}

def _wu_add(week_used, role, food_name, food_subcat):
    if role not in week_used: week_used[role] = []
    if not isinstance(week_used[role], list): week_used[role] = []
    week_used[role].append((food_name, food_subcat))

def _diet_bonus(row, diet, role, slot):
    if role != 'protein_nonveg':
        return 0.0
    subtype = row.get('protein_subtype', 'na')
    if diet == 'egg':
        return 0.30 if subtype == 'egg' else -0.20
    if diet == 'nonveg':
        slot_bonus = 0.10 if slot in ('lunch', 'dinner') else 0.0
        return {'meat': 0.55 + slot_bonus, 'egg': 0.12, 'veg': -0.25}.get(subtype, 0.0)
    return 0.0

def pick_item(slot_pool, role, kcal_b, carb_b, gs_cap, day_used, week_used,
             fat_cap=None, avoid_grain=None, diet='veg', slot=None,
             required_subtype=None, banned_subtypes=None):
    role_hist      = week_used.get(role, [])
    used_names     = {t[0] for t in role_hist}
    cooldown_names = {t[0] for t in role_hist[-COOLDOWN_N:]}
    last4_subcats  = {t[1] for t in role_hist[-COOLDOWN_N:]}
    family_counts  = Counter(t[1] for t in role_hist)

    base = slot_pool[
        (slot_pool['food_role']      == role) &
        (slot_pool['glycemic_score'] <= gs_cap) &
        (slot_pool['srv_kcal']       <= kcal_b) &
        (slot_pool['srv_carb']       <= carb_b) &
        (~slot_pool['food_name'].isin(day_used))
    ].copy()

    if fat_cap is not None:
        base = base[base['srv_fat'] <= fat_cap]
    if required_subtype is not None and 'protein_subtype' in base.columns:
        base = base[base['protein_subtype'] == required_subtype]
    if banned_subtypes and 'protein_subtype' in base.columns:
        base = base[~base['protein_subtype'].isin(banned_subtypes)]
    if base.empty:
        return None

    fresh = base[~base['food_name'].isin(used_names)]
    if fresh.empty:
        fresh = base[~base['food_name'].isin(cooldown_names)]
        if fresh.empty:
            fresh = base

    fresh = fresh.copy()
    fresh['_score'] = fresh['composite_score'].copy()

    item_counts = Counter(t[0] for t in role_hist)
    if item_counts:
        fresh['_score'] -= fresh['food_name'].map(lambda n: item_counts.get(n, 0) * 0.25)

    if family_counts:
        fresh['_score'] -= fresh['food_subcat'].map(lambda s: family_counts.get(s, 0) * FAMILY_CNT_P)

    fresh.loc[fresh['food_subcat'].isin(last4_subcats), '_score'] -= RECENCY_P

    if avoid_grain:
        fresh.loc[fresh['grain_category'] == avoid_grain, '_score'] -= GRAIN_P

    fresh['_score'] += fresh.apply(lambda r: _diet_bonus(r, diet, role, slot), axis=1)

    top5 = fresh.nlargest(min(TOP_N, len(fresh)), '_score')
    return top5.sample(1).iloc[0]

def scale_portions(row, role, kcal_b, carb_b):
    max_srv = MAX_SRV.get(role, 1)
    if role == 'breakfast_carb' and row['srv_kcal'] < 200:
        max_srv = max(3, int(np.ceil(320 / row['srv_kcal'])))
    mk = int(kcal_b // row['srv_kcal'])
    mc = int(carb_b // row['srv_carb']) if row['srv_carb'] > 0 else max_srv
    p  = max(MIN_SRV.get(role,1), min(mk, mc, max_srv))
    return _make_item(row, role, max(p, 1))

def _to_df(items):
    if not items: return pd.DataFrame(columns=OUTPUT_COLS)
    return pd.DataFrame(items)[OUTPUT_COLS]

def _add(items, row, role, kcal_b, carb_b, day_used, week_used):
    it = scale_portions(row, role, kcal_b, carb_b)
    items.append(it)
    day_used.add(row['food_name'])
    _wu_add(week_used, role, row['food_name'], row.get('food_subcat','other'))
    return it['kcal'], it['carb_g']

# print('✅ Core utilities updated with diet-aware protein preference')

# def optimize_calories(items, spool, C, day_used, week_used, pad_roles=None):
#     if pad_roles is None: pad_roles = ['roti','dal','curd','snack']
#     lo = C['kcal_lo']; hi = C['kcal_hi']; gsc = C['gs_cap']
#     def total():  return sum(i['kcal']   for i in items)
#     def c_used(): return sum(i['carb_g'] for i in items)

#     for _ in range(3):  # Pass 1: trim
#         if total() <= hi: break
#         for it in items:
#             if it['food_role'] in ['roti','rice'] and it['portions'] > 1:
#                 it['portions'] -= 1; it['kcal'] -= it['_unit_kcal']; it['carb_g'] -= it['_unit_carb']; break

#     for it in items:    # Pass 2: scale up
#         if total() >= lo: break
#         if it['food_role'] in ['roti','rice']:
#             gap = lo - total(); cleft = C['carb_cap'] - c_used()
#             mx  = MAX_SRV[it['food_role']] - it['portions']
#             by_k = int(gap // it['_unit_kcal']) + 1
#             by_c = int(cleft // it['_unit_carb']) if it['_unit_carb'] > 0 else mx
#             extra = min(by_k, by_c, mx)
#             if extra > 0:
#                 it['portions'] += extra; it['kcal'] += round(it['_unit_kcal']*extra,1); it['carb_g'] += round(it['_unit_carb']*extra,1)

#     if total() < lo:    # Pass 3a: add side item
#         used_roles = {i['food_role'] for i in items}
#         for role in pad_roles:
#             if role in used_roles: continue
#             gap = lo - total(); cleft = C['carb_cap'] - c_used()
#             row = pick_item(spool, role, gap*1.8, cleft, gsc, day_used, week_used)
#             if row is not None:
#                 it = scale_portions(row, role, gap*1.8, cleft); items.append(it)
#                 day_used.add(row['food_name']); _wu_add(week_used, role, row['food_name'], row.get('food_subcat','other'))
#                 break

#     for it in items:    # Pass 3b: boost low-cal items
#         if total() >= lo: break
#         role = it['food_role']
#         if role in ['breakfast_carb','dal','sabzi']:
#             max_p = MAX_SRV.get(role,1)
#             if role == 'breakfast_carb' and it['_unit_kcal'] < 200: max_p = 5
#             if it['portions'] < max_p:
#                 it['portions'] += 1; it['kcal'] += round(it['_unit_kcal'],1); it['carb_g'] += round(it['_unit_carb'],1)

#     return items

# # print('✅ optimize_calories() defined')
def optimize_calories(items, spool, C, day_used, week_used, diet='veg', slot=None, pad_roles=None):
    if pad_roles is None:
        pad_roles = ['roti', 'dal', 'curd', 'snack']

    lo = C['kcal_lo']
    hi = C['kcal_hi']
    gsc = C['gs_cap']

    def total():
        return sum(i['kcal'] for i in items)

    def c_used():
        return sum(i['carb_g'] for i in items)

    for _ in range(3):
        if total() <= hi:
            break
        for it in items:
            if it['food_role'] in ['roti', 'rice'] and it['portions'] > 1:
                it['portions'] -= 1
                it['kcal'] -= it['_unit_kcal']
                it['carb_g'] -= it['_unit_carb']
                break

    for it in items:
        if total() >= lo:
            break
        if it['food_role'] in ['roti', 'rice']:
            gap = lo - total()
            cleft = C['carb_cap'] - c_used()
            mx = MAX_SRV[it['food_role']] - it['portions']
            by_k = int(gap // it['_unit_kcal']) + 1
            by_c = int(cleft // it['_unit_carb']) if it['_unit_carb'] > 0 else mx
            extra = min(by_k, by_c, mx)
            if extra > 0:
                it['portions'] += extra
                it['kcal'] += round(it['_unit_kcal'] * extra, 1)
                it['carb_g'] += round(it['_unit_carb'] * extra, 1)

    if total() < lo:
        used_roles = {i['food_role'] for i in items}
        for role in pad_roles:
            if role in used_roles:
                continue
            gap = lo - total()
            cleft = C['carb_cap'] - c_used()
            row = pick_item(spool, role, gap * 1.8, cleft, gsc, day_used, week_used, diet=diet, slot=slot)
            if row is not None:
                it = scale_portions(row, role, gap * 1.8, cleft)
                items.append(it)
                day_used.add(row['food_name'])
                _wu_add(week_used, role, row['food_name'], row.get('food_subcat', 'other'))
                break

    for it in items:
        if total() >= lo:
            break
        role = it['food_role']
        if role in ['breakfast_carb', 'dal', 'sabzi', 'protein_nonveg']:
            max_p = MAX_SRV.get(role, 1)
            if role == 'breakfast_carb' and it['_unit_kcal'] < 200:
                max_p = 5
            if it['portions'] < max_p:
                it['portions'] += 1
                it['kcal'] += round(it['_unit_kcal'], 1)
                it['carb_g'] += round(it['_unit_carb'], 1)

    return items

def _count_meat_items(week_used):
    return sum(1 for _, subcat in week_used.get('protein_nonveg', []) if subcat == 'meat')

def build_breakfast(pool, C, day_used, week_used, diet, day_state):
    spool = diet_filter(pool[pool['meal_slot']=='breakfast'], diet)
    Cc = C['breakfast']; gs = Cc['gs_cap']; items = []; ku = cu = 0.0
    for role in ['breakfast_carb','roti']:
        row = pick_item(spool, role, Cc['kcal_target']*0.72, Cc['carb_cap'], gs, day_used, week_used, diet=diet, slot='breakfast')
        if row is not None:
            dk, dc = _add(items, row, role, Cc['kcal_target']*0.72, Cc['carb_cap'], day_used, week_used)
            ku += dk; cu += dc; day_state['last_grain'] = row.get('grain_category','other'); break
    if ku < Cc['kcal_target']*0.40:
        fill_kcal = Cc['kcal_target']*0.72 - ku; fill_carb = Cc['carb_cap'] - cu
        for r2 in ['snack','roti','breakfast_carb']:
            row2 = pick_item(spool, r2, fill_kcal, fill_carb, gs, day_used, week_used, diet=diet, slot='breakfast')
            if row2 is not None:
                dk, dc = _add(items, row2, r2, fill_kcal, fill_carb, day_used, week_used)
                ku += dk; cu += dc; break
    if diet in ['egg','nonveg']:
        subtype = 'egg' if diet == 'egg' else None
        row = pick_item(spool, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, gs, day_used, week_used,
                        diet=diet, slot='breakfast', required_subtype=subtype)
        if row is not None:
            dk, dc = _add(items, row, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, day_used, week_used)
            ku += dk; cu += dc
    ck = Cc['kcal_target']-ku; cc = Cc['carb_cap']-cu
    if ck > 60:
        row = pick_item(spool, 'curd', ck, cc, gs, day_used, week_used, diet=diet, slot='breakfast')
        if row is not None: _add(items, row, 'curd', ck, cc, day_used, week_used)
    items = optimize_calories(items, spool, Cc, day_used, week_used, diet=diet, slot='breakfast',
                              pad_roles=['roti','breakfast_carb','snack','curd'])
    return _to_df(items)


def build_thali(pool, slot, C, day_used, week_used, diet, lighter=False, avoid_grain=None, force_meat=False):
    spool = diet_filter(pool[pool['meal_slot']==slot], diet)
    Cc = C[slot]; gs = Cc['gs_cap']; items = []; ku = cu = 0.0
    roti_min = Cc['kcal_target'] * 0.25
    dal_b    = Cc['kcal_target'] * (0.32 if diet == 'nonveg' else 0.40)
    sabzi_b  = Cc['kcal_target'] * 0.18
    protein_b = Cc['kcal_target'] * (0.34 if diet == 'nonveg' else 0.22)
    cd = Cc['carb_cap'] * (0.40 if diet == 'nonveg' else 0.65)
    cs = Cc['carb_cap'] * 0.22
    cp = Cc['carb_cap'] * 0.30

    dal_placed = False
    protein_placed = False

    if diet in ['egg', 'nonveg']:
        subtype = 'meat' if (diet == 'nonveg' and force_meat) else ('egg' if diet == 'egg' else None)
        banned = ['egg'] if (diet == 'nonveg' and force_meat) else None
        for km in [1.0, 1.25, 1.5]:
            row = pick_item(spool, 'protein_nonveg', protein_b*km, cp, gs, day_used, week_used,
                            diet=diet, slot=slot, required_subtype=subtype, banned_subtypes=banned)
            if row is not None:
                dk, dc = _add(items, row, 'protein_nonveg', protein_b*km, cp, day_used, week_used)
                ku += dk; cu += dc; protein_placed = True; break

    should_add_dal = True
    if diet == 'nonveg' and protein_placed:
        kcal_left = Cc['kcal_target'] - ku
        carb_left = Cc['carb_cap'] - cu
        should_add_dal = (slot == 'lunch' and kcal_left >= Cc['kcal_target'] * 0.22 and carb_left >= Cc['carb_cap'] * 0.18)

    if should_add_dal:
        for cm in [1.0, 1.6, 2.0]:
            row = pick_item(spool, 'dal', dal_b, cd*cm, gs, day_used, week_used, diet=diet, slot=slot)
            if row is not None:
                dk, dc = _add(items, row, 'dal', dal_b, cd*cm, day_used, week_used)
                ku += dk; cu += dc; dal_placed = True; break

    for cm in [1.0, 1.5, 2.0]:
        row = pick_item(spool, 'sabzi', sabzi_b, cs*cm, gs, day_used, week_used, diet=diet, slot=slot)
        if row is not None:
            dk, dc = _add(items, row, 'sabzi', sabzi_b, cs*cm, day_used, week_used)
            ku += dk; cu += dc; break

    roti_b = max(Cc['kcal_target']-ku-Cc['kcal_target']*0.06, roti_min)
    carb_r = Cc['carb_cap'] - cu
    row = pick_item(spool, 'roti', roti_b, carb_r, gs, day_used, week_used, avoid_grain=avoid_grain, diet=diet, slot=slot)
    if row is not None:
        dk, dc = _add(items, row, 'roti', roti_b, carb_r, day_used, week_used)
        ku += dk; cu += dc

    ck = Cc['kcal_target']-ku; cc = Cc['carb_cap']-cu
    if diet != 'nonveg' or not protein_placed:
        row = pick_item(spool, 'curd', ck, cc, gs, day_used, week_used, diet=diet, slot=slot)
        if row is not None:
            dk, dc = _add(items, row, 'curd', ck, cc, day_used, week_used)
            ku += dk; cu += dc

    if diet == 'nonveg' and not protein_placed:
        row = pick_item(spool, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, gs, day_used, week_used,
                        diet=diet, slot=slot, required_subtype='meat' if force_meat else None)
        if row is not None:
            dk, dc = _add(items, row, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, day_used, week_used)
            ku += dk; cu += dc

    allow_protein = (not lighter) or (lighter and not dal_placed and not protein_placed)
    if allow_protein and diet == 'egg' and not protein_placed:
        row = pick_item(spool, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, gs, day_used, week_used,
                        diet=diet, slot=slot, required_subtype='egg')
        if row is not None:
            dk, dc = _add(items, row, 'protein_nonveg', Cc['kcal_target']-ku, Cc['carb_cap']-cu, day_used, week_used)
            ku += dk; cu += dc

    pad_roles = ['roti','sabzi','protein_nonveg'] if diet == 'nonveg' else ['roti','dal','sabzi','curd']
    items = optimize_calories(items, spool, Cc, day_used, week_used, diet=diet, slot=slot, pad_roles=pad_roles)
    return _to_df(items)


def build_snack(pool, C, day_used, week_used, diet):
    spool = diet_filter(pool[pool['meal_slot']=='snack'], diet)
    Cc = C['snack']; gs = Cc['gs_cap']; budget = min(Cc['kcal_target'], 300); items = []; ku = 0.0
    for _ in range(2):
        if ku >= budget*0.85: break
        roles = ['snack', 'curd']
        if diet == 'egg':
            roles.append('protein_nonveg')
        elif diet == 'nonveg':
            roles = ['protein_nonveg', 'snack', 'curd']
        for role in roles:
            req = 'egg' if (diet == 'egg' and role == 'protein_nonveg') else None
            row = pick_item(spool, role, budget-ku, Cc['carb_cap'], gs, day_used, week_used,
                            fat_cap=12.0, diet=diet, slot='snack', required_subtype=req)
            if row is not None:
                dk, _ = _add(items, row, role, budget-ku, Cc['carb_cap'], day_used, week_used)
                ku += dk; break
    return _to_df(items)

# print('✅ Meal builders updated for stronger non-veg allocation')

def generate_daily_plan(glucose_mg_dl=130, daily_kcal=2400, diet='veg', seed=None, week_used=None):
    """
    Generate one day's meal plan.
    Pass week_used back into every subsequent call for multi-day variety.
    week_used: dict[str, list[tuple[food_name, food_subcat]]]
    """
    assert diet in ('veg','egg','nonveg'), "diet must be 'veg', 'egg', or 'nonveg'"
    if seed is not None: random.seed(seed); np.random.seed(seed)
    if week_used is None: week_used = {}
    C = get_constraints(glucose_mg_dl, daily_kcal)
    day_used = set(); day_state = {'last_grain': None}

    meat_so_far = _count_meat_items(week_used)
    force_lunch_meat = (diet == 'nonveg' and meat_so_far < 4)
    force_dinner_meat = (diet == 'nonveg' and meat_so_far < 7)

    breakfast = build_breakfast(pool, C, day_used, week_used, diet, day_state)
    if not breakfast.empty:
        cr = breakfast[breakfast['food_role'].isin(['roti','breakfast_carb','rice'])]
        if not cr.empty: day_state['last_grain'] = cr.iloc[0]['grain_category']

    lunch = build_thali(pool, 'lunch', C, day_used, week_used, diet,
                        avoid_grain=day_state.get('last_grain'), force_meat=force_lunch_meat)
    if not lunch.empty:
        rr = lunch[lunch['food_role']=='roti']
        if not rr.empty: day_state['last_grain'] = rr.iloc[0]['grain_category']

    dinner = build_thali(pool, 'dinner', C, day_used, week_used, diet,
                         lighter=True, avoid_grain=day_state.get('last_grain'),
                         force_meat=force_dinner_meat)
    snack  = build_snack(pool, C, day_used, week_used, diet)

    all_items = pd.concat([breakfast, lunch, dinner, snack])
    meal_kcal = {s: round(m['kcal'].sum(),1) if not m.empty else 0.0
                 for s,m in zip(['breakfast','lunch','dinner','snack'],[breakfast,lunch,dinner,snack])}
    summary = {
        'glucose_mg_dl':glucose_mg_dl, 'status':glucose_status(glucose_mg_dl), 'diet':diet,
        'daily_kcal_target':daily_kcal, 'total_kcal':round(all_items['kcal'].sum(),1),
        'total_carb_g':round(all_items['carb_g'].sum(),1), 'total_protein_g':round(all_items['protein_g'].sum(),1),
        'total_fat_g':round(all_items['fat_g'].sum(),1), 'total_fibre_g':round(all_items['fibre_g'].sum(),1),
        'meal_kcal':meal_kcal, 'kcal_targets':{s:C[s]['kcal_target'] for s in C},
        'pct_achieved':round(all_items['kcal'].sum()/daily_kcal*100, 1),
        'meat_items_week': _count_meat_items(week_used),
    }
    return dict(breakfast=breakfast, lunch=lunch, dinner=dinner, snack=snack, summary=summary, week_used=week_used)

# print('✅ generate_daily_plan() updated with weekly meat quota support')

FMT = {'portions':'{:.0f}','kcal':'{:.0f}','carb_g':'{:.1f}','protein_g':'{:.1f}',
       'fat_g':'{:.1f}','fibre_g':'{:.1f}','glycemic_score':'{:.3f}','composite_score':'{:.3f}'}

def display_plan(plan, show_scores=True):
    s = plan['summary']; pct = s['pct_achieved']
    bar = '█'*int(pct//5)+'░'*(20-int(pct//5))
    print('='*72); print('  HealthSYNQ-D v8  ·  FINAL')
    print(f"  Glucose : {s['glucose_mg_dl']} mg/dL  [{s['status']}]")
    print(f"  Diet    : {s['diet'].upper()}")
    print(f"  Target  : {s['daily_kcal_target']:.0f} kcal  Generated: {s['total_kcal']:.0f} kcal  ({pct:.1f}%)")
    print(f"  [{bar}]")
    print('='*72)
    show_cols = OUTPUT_COLS if show_scores else [c for c in OUTPUT_COLS if c not in ('glycemic_score','composite_score')]
    for slot in ['breakfast','lunch','dinner','snack']:
        meal = plan[slot]; got = s['meal_kcal'][slot]; tgt = s['kcal_targets'][slot]
        valid = validate_meal(meal, slot)
        print(f"\n{'─'*72}")
        
        print(f"  Target {tgt:.0f} kcal → {got:.0f} kcal ({got/tgt*100:.0f}%)  {'✅ VALID' if valid else '⚠️ INCOMPLETE'}")
        print(f"{'─'*72}")
        if meal.empty: print('  ⚠️  No items')
        else: display(meal[show_cols].style.format({k:v for k,v in FMT.items() if k in show_cols}).set_properties(**{'text-align':'left'}).hide(axis='index'))
    print(f"\n{'='*72}"); print('  📊 DAILY TOTALS')
    print(f"  Energy: {s['total_kcal']:.0f}/{s['daily_kcal_target']:.0f} kcal ({pct:.1f}%)  |  Carbs: {s['total_carb_g']:.1f}g  |  Protein: {s['total_protein_g']:.1f}g  |  Fat: {s['total_fat_g']:.1f}g")
    print('='*72)

# print('✅ display_plan() defined')

