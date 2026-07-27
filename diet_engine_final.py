import os
import pandas as pd
import numpy as np
import random
import warnings
from collections import Counter
# from IPython.display import display
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
# DATASET_PATH = 'Anuvaad_INDB_2024.xlsx'  
# Replace with your actual Render external DB URL
PER100G = ['food_code','food_name','servings_unit','energy_kcal','carb_g','protein_g','fat_g','freesugar_g','fibre_g']
PER_SRV = ['unit_serving_energy_kcal','unit_serving_carb_g','unit_serving_protein_g',
           'unit_serving_fat_g','unit_serving_freesugar_g','unit_serving_fibre_g']
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
HARD_REMOVE = [
   r'\bcooler\b',r'lem-o',r'\biced tea\b',r'\bgin\b',r'\bvodka\b',
    r'whiskey',r'\brum\b',r'\bbeer\b',r'\bwine\b',r'\bpunch\b',r'\bnog\b',r'smoothie',
    r'\bsoup\b',r'\bstock\b',r'\bbroth\b',r'\bconsomm[eÃ©]\b',
    r'\bbaby\b',r'\binfant\b',r'shishu',r'amylase',r'\bpowder\b',r'\bformula\b',r'\bsupplement\b',
    r'\bburfi\b',r'\bbarfi\b',r'\bladoo\b',r'\bpeda\b',r'\bmodak\b',r'\bchikki\b',
    r'peanut brittle',r'\bice cream\b',r'\bcake\b',r'\bpastry\b',r'\bpudding\b',
    r'\bbiscuit\b',r'\bcookie\b',r'\bpickle\b',r'\baachar\b',r'\bketchup\b',r'pickled mustard',
    r'\bjam\b',r'\bjelly\b',r'\bicing\b',r'\bgravy for\b',r'\bchips\b',r'\bpremix\b',
    r'\bspaghetti\b',r'\blasagne\b',r'\bpasta\b',r'\bnoodles\b',r'\bchowmein\b',r'\bpancake\b',
    r'\byakhni\b',r'\bwater\b',r'egg halwa',
    r'\bsouffle\b',r'\bpie\b',r'\bdrop\b',r'\bmathri\b',r'\bpuff\b',r'\bchop\b',
    r'buttermilk biscuit',
    r'lemon curd filling', r'chocolate swiss roll', r'swiss roll',
    r'\bicing\b', r'\bfilling\b', r'\bdip\b',
    r'\bchutney\b', r'\bcookies\b', r'\bladoos\b',
]
mask = df['food_name'].str.lower().str.contains('|'.join(HARD_REMOVE), regex=True)
df = df[~mask].reset_index(drop=True)
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
    'veg_protein': ['paneer curry','paneer masala','shahi paneer','methi malai paneer',
             'matar paneer','paneer butter masala','palak paneer','kadhai paneer',
             'paneer lababdar','paneer in butter','veg paneer stew','paneer shaslik',
             'paneer cutlet','paneer pakora','paneer tikka','paneer',
             'soyabean curry','soya bean','soya chunks','nutrinugget','soya seekh',
             'soya roti','soya','tofu','peanut cutlet'],
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
    # Curd/raita must be checked before sabzi, otherwise items like
    # "Bottle gourd raita" get caught by lauki/ghiya vegetable keywords.
    for role in ['roti','curd','veg_protein','dal','sabzi','protein_nonveg','snack','breakfast_carb','rice']:
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
    if role == 'veg_protein':
        if any(k in name for k in ['paneer']): return 'paneer'
        if any(k in name for k in ['soya','soyabean','tofu']): return 'soya'
        if any(k in name for k in ['peanut','moongfali','mungfali']): return 'peanut'
        if any(k in name for k in ['almond','badam']): return 'almond'
        if any(k in name for k in ['cashew','kaju']): return 'cashew'
        return 'veg_protein'
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

SLOT_MAP = {
    'roti':           ['breakfast','lunch','dinner'],
    'dal':            ['lunch','dinner'],
    'sabzi':          ['lunch','dinner'],
    'curd':           ['breakfast','lunch','dinner','snack'],  # dinner: raita valid
    'veg_protein':    ['breakfast','lunch','dinner','snack'],
    'protein_nonveg': ['breakfast','lunch','dinner','snack'],
    'rice':           ['lunch','dinner'],
    'snack':          ['breakfast','snack'],
    'breakfast_carb': ['breakfast'],
    'other':          [],
}
df['valid_slots'] = df['food_role'].map(SLOT_MAP)
pool = df.explode('valid_slots').dropna(subset=['valid_slots']).rename(columns={'valid_slots':'meal_slot'}).reset_index(drop=True)

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

def tune_constraints_for_diet(C, glucose_mg_dl, daily_kcal, diet):
    C = _copy_constraints(C)
    if diet != 'veg':
        return C

    # A high-calorie vegetarian diabetic plan cannot reliably reach 85-95%
    # calories with the very low default carb caps. This keeps carbs controlled
    # but gives dal/roti/idli/veg meals enough room to become realistic.
    if glucose_mg_dl <= 180 and daily_kcal >= 2000:
        multipliers = {'breakfast': 1.25, 'lunch': 1.35, 'dinner': 1.35, 'snack': 1.15}
    elif glucose_mg_dl <= 250 and daily_kcal >= 2000:
        multipliers = {'breakfast': 1.15, 'lunch': 1.20, 'dinner': 1.20, 'snack': 1.10}
    elif daily_kcal >= 1600:
        multipliers = {'breakfast': 1.08, 'lunch': 1.12, 'dinner': 1.12, 'snack': 1.05}
    else:
        multipliers = {'breakfast': 1.0, 'lunch': 1.0, 'dinner': 1.0, 'snack': 1.0}

    for slot, mult in multipliers.items():
        C[slot]['carb_cap'] = round(C[slot]['carb_cap'] * mult, 1)
    return C

# for g in [90, 115, 150, 200, 260]:
#     c = get_constraints(g, 2400)

OUTPUT_COLS = ['food_code','food_name','food_role','food_subcat','grain_category','serving_unit',
               'portions','kcal','carb_g','protein_g','fat_g','fibre_g','glycemic_score','composite_score']
INTERNAL_COLS = ['_unit_kcal','_unit_carb','_unit_protein','_unit_fat','_unit_fibre']
MIN_SRV = {'roti':1,'dal':1,'sabzi':1,'curd':1,'veg_protein':1,'protein_nonveg':1,'snack':1,'breakfast_carb':1,'rice':1,'other':1}
MAX_SRV = {'roti':4,'dal':3,'sabzi':2,'curd':2,'veg_protein':3,'protein_nonveg':2,'snack':3,'breakfast_carb':4,'rice':2,'other':1}
DYNAMIC_SLOT_MAX_RATIO = {'breakfast':1.15,'lunch':1.30,'snack':1.50,'dinner':1.55}

TOP_N         = 8
FAMILY_CNT_P  = 0.30
RECENCY_P     = 0.75
GRAIN_P       = 0.20
COOLDOWN_N    = 10

VALID_RULES = {
    'breakfast': ([{'roti','rice','breakfast_carb','snack'}], 'needs carb'),
    'lunch':     ([{'roti','rice'}, {'dal','veg_protein','protein_nonveg'}, {'sabzi','curd','dal','veg_protein'}], 'carb+protein+veg'),
    'dinner':    ([{'roti','rice'}, {'dal','veg_protein','protein_nonveg','sabzi'}, {'sabzi','curd','dal','veg_protein'}], 'carb+(dal/sabzi)+veg'),
    'snack':     ([{'snack','curd','veg_protein','protein_nonveg'}], 'needs snack'),
}

def validate_meal(meal, slot):
    if meal.empty: return False
    roles = set(meal['food_role'])
    if slot in ('lunch', 'dinner') and not (roles & {'roti', 'rice'}):
        has_protein = bool(roles & {'dal', 'veg_protein', 'protein_nonveg'})
        has_veg = bool(roles & {'sabzi', 'curd', 'dal', 'veg_protein'})
        carb_g = float(meal['carb_g'].sum()) if 'carb_g' in meal else 0.0
        fibre_g = float(meal['fibre_g'].sum()) if 'fibre_g' in meal else 0.0
        if has_protein and has_veg and carb_g >= 30 and fibre_g >= 8:
            return True
    rules, _ = VALID_RULES.get(slot, ([set()], ''))
    return all(bool(roles & g) for g in rules)

def _make_item(row, role, portions):
    return {'food_code':row.get('food_code'), 'food_name':row['food_name'], 'food_role':role, 'food_subcat':row.get('food_subcat','other'),
            'grain_category':row.get('grain_category','other'), 'serving_unit':row['servings_unit'],
            'portions':portions, 'kcal':round(row['srv_kcal']*portions,1), 'carb_g':round(row['srv_carb']*portions,1),
            'protein_g':round(row['srv_protein']*portions,1), 'fat_g':round(row['srv_fat']*portions,1),
            'fibre_g':round(row['srv_fibre']*portions,1), 'glycemic_score':round(row['glycemic_score'],3),
            'composite_score':round(row['composite_score'],3), '_unit_kcal':row['srv_kcal'], '_unit_carb':row['srv_carb'],
            '_unit_protein':row['srv_protein'], '_unit_fat':row['srv_fat'], '_unit_fibre':row['srv_fibre']}

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
    item_counts    = Counter(t[0] for t in role_hist)

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

    exact_cap = {
        'sabzi': 2,
        'veg_protein': 2,
        'protein_nonveg': 2,
        'curd': 2,
    }.get(role)
    if exact_cap is not None:
        under_cap = base[~base['food_name'].map(lambda n: item_counts.get(n, 0) >= exact_cap)]
        if not under_cap.empty:
            base = under_cap
        elif role in ['sabzi', 'curd']:
            return None

    if role in ['veg_protein', 'sabzi']:
        fresh = base[~base['food_name'].isin(cooldown_names)]
    else:
        fresh = base[~base['food_name'].isin(used_names)]
    if fresh.empty:
        fresh = base[~base['food_name'].isin(cooldown_names)]
        if fresh.empty:
            fresh = base

    fresh = fresh.copy()
    fresh['_score'] = fresh['composite_score'].copy()

    if item_counts:
        role_repeat_penalty = {
            'sabzi': 2.25,
            'curd': 1.10,
            'veg_protein': 1.65,
            'protein_nonveg': 0.95,
        }.get(role, 0.80)
        fresh['_score'] -= fresh['food_name'].map(lambda n: item_counts.get(n, 0) * role_repeat_penalty)

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
        max_srv = min(6, max(3, int(np.ceil(320 / row['srv_kcal']))))
    mk = int(kcal_b // row['srv_kcal'])
    mc = int(carb_b // row['srv_carb']) if row['srv_carb'] > 0 else max_srv
    p  = max(MIN_SRV.get(role,1), min(mk, mc, max_srv))
    return _make_item(row, role, max(p, 1))

def _to_df(items):
    if not items: return pd.DataFrame(columns=OUTPUT_COLS + INTERNAL_COLS)
    return pd.DataFrame(items)[OUTPUT_COLS + INTERNAL_COLS]

def _public_meal(meal):
    if meal is None or meal.empty:
        return pd.DataFrame(columns=OUTPUT_COLS)
    keep = [c for c in OUTPUT_COLS if c in meal.columns]
    return meal[keep].copy()

def _add(items, row, role, kcal_b, carb_b, day_used, week_used):
    it = scale_portions(row, role, kcal_b, carb_b)
    items.append(it)
    day_used.add(row['food_name'])
    _wu_add(week_used, role, row['food_name'], row.get('food_subcat','other'))
    return it['kcal'], it['carb_g']


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

def _bump_item(it, extra=1):
    it['portions'] += extra
    it['kcal'] = round(it['kcal'] + it['_unit_kcal'] * extra, 1)
    it['carb_g'] = round(it['carb_g'] + it['_unit_carb'] * extra, 1)
    it['protein_g'] = round(it['protein_g'] + it.get('_unit_protein', 0.0) * extra, 1)
    it['fat_g'] = round(it['fat_g'] + it.get('_unit_fat', 0.0) * extra, 1)
    it['fibre_g'] = round(it['fibre_g'] + it.get('_unit_fibre', 0.0) * extra, 1)


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
                _bump_item(it, -1)
                break

    boost_order_by_slot = {
        'breakfast': ['breakfast_carb', 'veg_protein', 'snack', 'curd', 'roti'],
        'lunch': ['protein_nonveg', 'veg_protein', 'dal', 'curd', 'roti', 'rice', 'sabzi'],
        'dinner': ['protein_nonveg', 'veg_protein', 'dal', 'curd', 'roti', 'rice', 'sabzi'],
        'snack': ['snack', 'veg_protein', 'curd', 'protein_nonveg'],
    }
    boost_order = boost_order_by_slot.get(slot, ['veg_protein', 'dal', 'curd', 'sabzi', 'roti', 'snack', 'protein_nonveg'])

    for _ in range(10):
        if total() >= lo:
            break
        made_progress = False
        for role in boost_order:
            if total() >= lo:
                break
            candidates = [it for it in items if it['food_role'] == role]
            candidates.sort(key=lambda it: (it['_unit_carb'], -it['_unit_kcal']))
            for it in candidates:
                max_p = MAX_SRV.get(role, 1)
                if role == 'breakfast_carb' and it['_unit_kcal'] < 220:
                    max_p = max(max_p, int(np.ceil(420 / max(it['_unit_kcal'], 1))))
                if it['portions'] >= max_p:
                    continue
                if it['_unit_carb'] > max(0.0, C['carb_cap'] - c_used()):
                    continue
                if total() + it['_unit_kcal'] > hi:
                    continue
                _bump_item(it, 1)
                made_progress = True
                break
        if not made_progress:
            break

    for _ in range(2):
        if total() >= lo:
            break
        used_roles = {i['food_role'] for i in items}
        for role in pad_roles:
            if role in used_roles and role not in ['curd', 'snack']:
                continue
            gap = lo - total()
            cleft = C['carb_cap'] - c_used()
            if gap <= 40 or cleft <= 0:
                continue
            row = pick_item(spool, role, min(gap * 1.8, hi - total()), cleft, gsc, day_used, week_used, diet=diet, slot=slot)
            if row is not None:
                it = scale_portions(row, role, min(gap * 1.8, hi - total()), cleft)
                items.append(it)
                day_used.add(row['food_name'])
                _wu_add(week_used, role, row['food_name'], row.get('food_subcat', 'other'))
                break

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
    elif diet == 'veg' and ku < Cc['kcal_target'] * 0.70:
        row = pick_item(spool, 'veg_protein', Cc['kcal_target']-ku, Cc['carb_cap']-cu, gs, day_used, week_used,
                        fat_cap=18.0, diet=diet, slot='breakfast')
        if row is not None:
            dk, dc = _add(items, row, 'veg_protein', Cc['kcal_target']-ku, Cc['carb_cap']-cu, day_used, week_used)
            ku += dk; cu += dc
    ck = Cc['kcal_target']-ku; cc = Cc['carb_cap']-cu
    if ck > 60:
        row = pick_item(spool, 'curd', ck, cc, gs, day_used, week_used, diet=diet, slot='breakfast')
        if row is not None: _add(items, row, 'curd', ck, cc, day_used, week_used)
    items = optimize_calories(items, spool, Cc, day_used, week_used, diet=diet, slot='breakfast',
                              pad_roles=['snack','veg_protein','curd','roti','breakfast_carb'])

    if diet == 'veg' and sum(i['kcal'] for i in items) < Cc['kcal_target'] * 0.80:
        used_roles = {i['food_role'] for i in items}
        for role in ['snack', 'curd', 'veg_protein']:
            if role in used_roles and role != 'curd':
                continue
            gap = Cc['kcal_hi'] - sum(i['kcal'] for i in items)
            cleft = Cc['carb_cap'] - sum(i['carb_g'] for i in items)
            if gap <= 70 or cleft <= 3:
                continue
            row = pick_item(spool, role, gap, cleft, gs, day_used, week_used,
                            fat_cap=16.0, diet=diet, slot='breakfast')
            if row is not None:
                _add(items, row, role, gap, cleft, day_used, week_used)
                break
    elif diet in ['egg', 'nonveg'] and sum(i['kcal'] for i in items) < Cc['kcal_target'] * 0.80:
        subtype = 'egg' if diet == 'egg' else None
        for role in ['protein_nonveg', 'snack', 'curd']:
            gap = Cc['kcal_hi'] - sum(i['kcal'] for i in items)
            cleft = Cc['carb_cap'] - sum(i['carb_g'] for i in items)
            if gap <= 70:
                continue
            row = pick_item(spool, role, gap, max(cleft, 2.0), gs, day_used, week_used,
                            fat_cap=18.0, diet=diet, slot='breakfast',
                            required_subtype=subtype if role == 'protein_nonveg' else None)
            if row is not None:
                _add(items, row, role, gap, max(cleft, 2.0), day_used, week_used)
                break
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
    veg_protein_placed = False
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

    if diet == 'veg':
        veg_protein_b = Cc['kcal_target'] * (0.42 if slot == 'lunch' else 0.38)
        veg_protein_c = Cc['carb_cap'] * 0.45
        for km in [1.0, 1.25, 1.5]:
            row = pick_item(spool, 'veg_protein', veg_protein_b * km, veg_protein_c, gs,
                            day_used, week_used, fat_cap=24.0, diet=diet, slot=slot)
            if row is not None:
                dk, dc = _add(items, row, 'veg_protein', veg_protein_b * km, veg_protein_c, day_used, week_used)
                ku += dk; cu += dc; veg_protein_placed = True; break

    should_add_dal = True
    if diet == 'nonveg' and protein_placed:
        kcal_left = Cc['kcal_target'] - ku
        carb_left = Cc['carb_cap'] - cu
        should_add_dal = (slot == 'lunch' and kcal_left >= Cc['kcal_target'] * 0.22 and carb_left >= Cc['carb_cap'] * 0.18)
    elif diet == 'veg' and veg_protein_placed:
        kcal_left = Cc['kcal_target'] - ku
        carb_left = Cc['carb_cap'] - cu
        should_add_dal = kcal_left >= Cc['kcal_target'] * 0.18 and carb_left >= Cc['carb_cap'] * 0.18

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

    pad_roles = ['protein_nonveg','roti','dal','curd','sabzi'] if diet == 'nonveg' else ['veg_protein','roti','dal','curd','sabzi']
    items = optimize_calories(items, spool, Cc, day_used, week_used, diet=diet, slot=slot, pad_roles=pad_roles)
    return _to_df(items)


def build_snack(pool, C, day_used, week_used, diet):
    spool = diet_filter(pool[pool['meal_slot']=='snack'], diet)
    Cc = C['snack']; gs = Cc['gs_cap']; budget = min(Cc['kcal_target'], 300); items = []; ku = 0.0
    for _ in range(2):
        if ku >= budget*0.85: break
        roles = ['snack', 'veg_protein', 'curd'] if diet == 'veg' else ['snack', 'curd']
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


def _boost_df_row(meal, idx, extra=1):
    meal.at[idx, 'portions'] += extra
    meal.at[idx, 'kcal'] = round(meal.at[idx, 'kcal'] + meal.at[idx, '_unit_kcal'] * extra, 1)
    meal.at[idx, 'carb_g'] = round(meal.at[idx, 'carb_g'] + meal.at[idx, '_unit_carb'] * extra, 1)
    meal.at[idx, 'protein_g'] = round(meal.at[idx, 'protein_g'] + meal.at[idx, '_unit_protein'] * extra, 1)
    meal.at[idx, 'fat_g'] = round(meal.at[idx, 'fat_g'] + meal.at[idx, '_unit_fat'] * extra, 1)
    meal.at[idx, 'fibre_g'] = round(meal.at[idx, 'fibre_g'] + meal.at[idx, '_unit_fibre'] * extra, 1)

def _day_total(meals, col):
    return sum(float(meal[col].sum()) for meal in meals.values() if not meal.empty)

def rescue_day_calories(meals, C, daily_kcal, diet):
    target_floor = daily_kcal * (0.90 if diet == 'veg' else 0.88)
    daily_carb_cap = sum(C[s]['carb_cap'] for s in C)
    role_order = ['veg_protein', 'protein_nonveg', 'dal', 'roti', 'curd', 'breakfast_carb', 'snack']

    for _ in range(10):
        if _day_total(meals, 'kcal') >= target_floor:
            break
        boosted = False

        for role in role_order:
            if boosted:
                break
            candidates = []
            for slot, meal in meals.items():
                if meal.empty:
                    continue
                meal_hi = C[slot]['kcal_hi']
                for idx, row in meal.iterrows():
                    if row['food_role'] != role:
                        continue
                    max_p = MAX_SRV.get(role, 1)
                    if row['portions'] >= max_p:
                        continue
                    if float(meal['kcal'].sum()) + row['_unit_kcal'] > meal_hi:
                        continue
                    if _day_total(meals, 'carb_g') + row['_unit_carb'] > daily_carb_cap:
                        continue
                    candidates.append((row['_unit_carb'], -row['_unit_kcal'], slot, idx))

            if not candidates:
                continue

            _, _, slot, idx = sorted(candidates)[0]
            _boost_df_row(meals[slot], idx, 1)
            boosted = True

        if not boosted:
            break

    return meals

MEAL_ORDER = ['breakfast', 'lunch', 'dinner', 'snack']
APP_MEAL_ORDER = ['breakfast', 'lunch', 'snack', 'dinner']

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _remaining_slots_from(current_slot):
    if current_slot not in APP_MEAL_ORDER:
        raise ValueError(f"current_slot must be one of {APP_MEAL_ORDER}")
    i = APP_MEAL_ORDER.index(current_slot)
    return APP_MEAL_ORDER[i:]

def _copy_constraints(C):
    return {k: dict(v) for k, v in C.items()}

def _reallocate_constraints_for_remaining(C, remaining_slots, remaining_kcal):
    C_dyn = _copy_constraints(C)
    if not remaining_slots:
        return C_dyn

    base_remaining = sum(C[s]['kcal_target'] for s in remaining_slots) + 1e-9
    slot_targets = {}
    for slot in remaining_slots:
        weight = C[slot]['kcal_target'] / base_remaining
        new_kcal = round(remaining_kcal * weight, 1)
        max_kcal = C[slot]['kcal_target'] * DYNAMIC_SLOT_MAX_RATIO.get(slot, 1.35)
        slot_targets[slot] = min(new_kcal, max_kcal)

    leftover = max(0.0, remaining_kcal - sum(slot_targets.values()))
    for _ in range(4):
        if leftover <= 1:
            break
        available = [
            s for s in remaining_slots
            if slot_targets[s] < C[s]['kcal_target'] * DYNAMIC_SLOT_MAX_RATIO.get(s, 1.35) - 1
        ]
        if not available:
            break
        per_slot = leftover / len(available)
        used = 0.0
        for slot in available:
            max_kcal = C[slot]['kcal_target'] * DYNAMIC_SLOT_MAX_RATIO.get(slot, 1.35)
            add = min(per_slot, max_kcal - slot_targets[slot])
            slot_targets[slot] += add
            used += add
        leftover -= used

    for slot in remaining_slots:
        new_kcal = round(slot_targets[slot], 1)
        scale = new_kcal / (C[slot]['kcal_target'] + 1e-9)
        carb_scale = _clamp(scale, 0.80, 1.30)

        C_dyn[slot]['kcal_target'] = new_kcal
        C_dyn[slot]['kcal_lo'] = round(new_kcal * 0.88, 1)
        C_dyn[slot]['kcal_hi'] = round(new_kcal * 1.15, 1)
        C_dyn[slot]['carb_cap'] = round(C[slot]['carb_cap'] * carb_scale, 1)
    return C_dyn

def _build_dynamic_constraints(
    glucose_mg_dl,
    daily_kcal,
    current_slot,
    consumed_kcal_so_far,
    burned_kcal_so_far,
    burn_compensation_ratio,
    max_extra_kcal_ratio,
):
    C_base = get_constraints(glucose_mg_dl, daily_kcal)
    remaining_slots = _remaining_slots_from(current_slot)
    base_remaining_kcal = sum(C_base[s]['kcal_target'] for s in remaining_slots)

    burn_ratio = _clamp(float(burn_compensation_ratio), 0.0, 1.2)
    extra_cap = daily_kcal * _clamp(float(max_extra_kcal_ratio), 0.0, 1.5)
    burn_credit = min(max(0.0, float(burned_kcal_so_far)) * burn_ratio, extra_cap)

    remaining_kcal_raw = float(daily_kcal) - max(0.0, float(consumed_kcal_so_far)) + burn_credit
    min_remaining_floor = base_remaining_kcal * 0.10
    remaining_kcal = _clamp(remaining_kcal_raw, min_remaining_floor, base_remaining_kcal + extra_cap)
    C_dyn = _reallocate_constraints_for_remaining(C_base, remaining_slots, remaining_kcal)
    return C_base, C_dyn, remaining_slots, burn_ratio, burn_credit

def _infer_last_grain(already_used_foods):
    if not already_used_foods:
        return None
    for name in reversed(already_used_foods):
        g = assign_grain(str(name))
        if g in ('wheat', 'rice', 'millet', 'oats', 'semolina'):
            return g
    return None

def _meal_kcal(meal):
    if meal is None or meal.empty:
        return 0.0
    return float(meal['kcal'].sum())

def _meal_status_text(meal, slot, summary):
    completed = set(summary.get('completed_slots', []))
    if slot in completed:
        if meal.empty:
            return 'SKIPPED'
        return 'ACTUAL' if validate_meal(meal, slot) else 'ACTUAL PARTIAL'
    return 'VALID' if validate_meal(meal, slot) else 'INCOMPLETE'

def _normalize_food_key(name):
    return str(name or '').strip().lower()

def summarize_actual_intake_from_plan(
    plan,
    actual_intake=None,
    not_eaten=None,
    completed_slots=None,
    previous_week_used=None,
):
    """
    Convert a generated plan plus user feedback into consumed calories and used foods.

    Parameters
    ----------
    plan:
        A dict returned by generate_daily_plan/generate_dynamic_plan.
    actual_intake:
        Optional dict like:
        {
          "breakfast": {
            "Semolina idli (Suji/Rava idli)": 0.5,  # ate half of planned portions
            "Soya seekh kebab": 0.0                # skipped this food
          },
          "lunch": {"__default__": 1.0}
        }
        Missing foods inside completed slots default to eaten fully unless listed in
        not_eaten. Values are fractions of the planned item, clamped 0..1.
    not_eaten:
        Optional dict like {"lunch": ["Chapati/Roti", "Curd mint dip"]}.
    completed_slots:
        Slots already passed. If None, inferred from keys in actual_intake/not_eaten.
    previous_week_used:
        Existing week_used from earlier confirmed meals/days.
    """
    actual_intake = actual_intake or {}
    not_eaten = not_eaten or {}
    if completed_slots is None:
        completed_slots = sorted(
            set(actual_intake.keys()) | set(not_eaten.keys()),
            key=lambda s: APP_MEAL_ORDER.index(s) if s in APP_MEAL_ORDER else 99,
        )

    week_used = _copy_week_used(previous_week_used or {})
    already_used_foods = []
    consumed_kcal = 0.0
    consumed_by_slot = {}
    skipped_foods = {}

    for slot in completed_slots:
        if slot not in APP_MEAL_ORDER:
            raise ValueError(f"completed slot must be one of {APP_MEAL_ORDER}: {slot}")
        meal = plan.get(slot)
        if meal is None or meal.empty:
            consumed_by_slot[slot] = 0.0
            skipped_foods[slot] = []
            continue

        slot_feedback = actual_intake.get(slot, {})
        default_fraction = float(slot_feedback.get('__default__', 1.0))
        skipped = {_normalize_food_key(n) for n in not_eaten.get(slot, [])}
        slot_kcal = 0.0
        skipped_names = []

        for _, row in meal.iterrows():
            food_name = row['food_name']
            key = _normalize_food_key(food_name)
            fraction = 0.0 if key in skipped else float(slot_feedback.get(food_name, slot_feedback.get(key, default_fraction)))
            fraction = _clamp(fraction, 0.0, 1.0)
            if fraction <= 0:
                skipped_names.append(food_name)
                continue

            slot_kcal += float(row['kcal']) * fraction
            if fraction >= 0.25:
                role = row.get('food_role', 'other')
                subcat = row.get('food_subcat', 'other')
                already_used_foods.append(food_name)
                _wu_add(week_used, role, food_name, subcat)

        consumed_by_slot[slot] = round(slot_kcal, 1)
        skipped_foods[slot] = skipped_names
        consumed_kcal += slot_kcal

    return {
        'consumed_kcal_so_far': round(consumed_kcal, 1),
        'consumed_by_slot': consumed_by_slot,
        'already_used_foods': already_used_foods,
        'week_used': week_used,
        'skipped_foods': skipped_foods,
        'completed_slots': completed_slots,
    }

def _copy_week_used(week_used):
    return {role: list(items) for role, items in (week_used or {}).items()}

def _next_slot_after(completed_slots):
    if not completed_slots:
        return 'breakfast'
    last_i = max(APP_MEAL_ORDER.index(s) for s in completed_slots if s in APP_MEAL_ORDER)
    if last_i + 1 >= len(APP_MEAL_ORDER):
        return None
    return APP_MEAL_ORDER[last_i + 1]

def generate_dynamic_plan(
    glucose_mg_dl=130,
    daily_kcal=2400,
    diet='veg',
    current_slot='breakfast',
    consumed_kcal_so_far=0.0,
    burned_kcal_so_far=0.0,
    burn_compensation_ratio=0.65,
    max_extra_kcal_ratio=0.50,
    seed=None,
    week_used=None,
    already_used_foods=None,
):
    """
    Generate a dynamic plan for the remaining day, starting from current_slot.
    This keeps the existing food scoring and meal builders unchanged.
    """
    assert diet in ('veg', 'egg', 'nonveg'), "diet must be 'veg', 'egg', or 'nonveg'"
    if seed is not None:
        random.seed(seed); np.random.seed(seed)
    if week_used is None:
        week_used = {}
    if already_used_foods is None:
        already_used_foods = []

    C_base, C_dyn, remaining_slots, burn_ratio, burn_credit = _build_dynamic_constraints(
        glucose_mg_dl=glucose_mg_dl,
        daily_kcal=daily_kcal,
        current_slot=current_slot,
        consumed_kcal_so_far=consumed_kcal_so_far,
        burned_kcal_so_far=burned_kcal_so_far,
        burn_compensation_ratio=burn_compensation_ratio,
        max_extra_kcal_ratio=max_extra_kcal_ratio,
    )
    C_base = tune_constraints_for_diet(C_base, glucose_mg_dl, daily_kcal, diet)
    C_dyn = tune_constraints_for_diet(C_dyn, glucose_mg_dl, daily_kcal, diet)
    day_used = set(already_used_foods)
    day_state = {'last_grain': _infer_last_grain(already_used_foods)}
    meals = {k: pd.DataFrame(columns=OUTPUT_COLS) for k in MEAL_ORDER}

    meat_so_far = _count_meat_items(week_used)
    force_lunch_meat = (diet == 'nonveg' and meat_so_far < 4)
    force_dinner_meat = (diet == 'nonveg' and meat_so_far < 7)

    for slot in remaining_slots:
        if slot == 'breakfast':
            meal = build_breakfast(pool, C_dyn, day_used, week_used, diet, day_state)
            meals['breakfast'] = meal
            if not meal.empty:
                cr = meal[meal['food_role'].isin(['roti','breakfast_carb','rice'])]
                if not cr.empty:
                    day_state['last_grain'] = cr.iloc[0]['grain_category']
        elif slot == 'lunch':
            meal = build_thali(
                pool, 'lunch', C_dyn, day_used, week_used, diet,
                avoid_grain=day_state.get('last_grain'),
                force_meat=force_lunch_meat
            )
            meals['lunch'] = meal
            if not meal.empty:
                rr = meal[meal['food_role'] == 'roti']
                if not rr.empty:
                    day_state['last_grain'] = rr.iloc[0]['grain_category']
        elif slot == 'dinner':
            meal = build_thali(
                pool, 'dinner', C_dyn, day_used, week_used, diet,
                lighter=True,
                avoid_grain=day_state.get('last_grain'),
                force_meat=force_dinner_meat
            )
            meals['dinner'] = meal
        elif slot == 'snack':
            meals['snack'] = build_snack(pool, C_dyn, day_used, week_used, diet)

    remaining_target = sum(C_dyn[s]['kcal_target'] for s in remaining_slots)
    remaining_meals = {s: meals[s] for s in remaining_slots}
    boosted_remaining = rescue_day_calories(remaining_meals, C_dyn, remaining_target, diet)
    for slot, meal in boosted_remaining.items():
        meals[slot] = meal

    non_empty = [m for m in meals.values() if not m.empty]
    all_items = pd.concat(non_empty) if non_empty else pd.DataFrame(columns=OUTPUT_COLS)
    meal_kcal = {s: round(meals[s]['kcal'].sum(), 1) if not meals[s].empty else 0.0 for s in MEAL_ORDER}

    target_with_activity = round(float(daily_kcal) + burn_credit, 1)
    projected_total = round(float(consumed_kcal_so_far) + float(all_items['kcal'].sum()), 1)

    summary = {
        'glucose_mg_dl': glucose_mg_dl,
        'status': glucose_status(glucose_mg_dl),
        'diet': diet,
        'current_slot': current_slot,
        'remaining_slots': remaining_slots,
        'daily_kcal_target': float(daily_kcal),
        'consumed_kcal_so_far': round(float(consumed_kcal_so_far), 1),
        'burned_kcal_so_far': round(float(burned_kcal_so_far), 1),
        'burn_compensation_ratio': burn_ratio,
        'burn_credit_applied': round(burn_credit, 1),
        'target_with_activity': target_with_activity,
        'planned_remaining_kcal_target': round(sum(C_dyn[s]['kcal_target'] for s in remaining_slots), 1),
        'generated_remaining_kcal': round(float(all_items['kcal'].sum()), 1),
        'projected_day_kcal': projected_total,
        'projected_pct_of_target': round((projected_total / (target_with_activity + 1e-9)) * 100, 1),
        'total_carb_g': round(float(all_items['carb_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_protein_g': round(float(all_items['protein_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_fat_g': round(float(all_items['fat_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_fibre_g': round(float(all_items['fibre_g'].sum()), 1) if not all_items.empty else 0.0,
        'meal_kcal': meal_kcal,
        'kcal_targets': {s: C_dyn[s]['kcal_target'] for s in C_dyn},
        'meat_items_week': _count_meat_items(week_used),
    }

    return dict(
        breakfast=_public_meal(meals['breakfast']),
        lunch=_public_meal(meals['lunch']),
        dinner=_public_meal(meals['dinner']),
        snack=_public_meal(meals['snack']),
        summary=summary,
        week_used=week_used,
    )

def _actual_meal_from_feedback(meal, slot_feedback=None, skipped_names=None):
    if meal is None or meal.empty:
        return pd.DataFrame(columns=meal.columns if meal is not None else OUTPUT_COLS + INTERNAL_COLS)

    slot_feedback = slot_feedback or {}
    skipped = {_normalize_food_key(n) for n in (skipped_names or [])}
    default_fraction = float(slot_feedback.get('__default__', 1.0))
    rows = []

    for _, row in meal.iterrows():
        food_name = row['food_name']
        key = _normalize_food_key(food_name)
        fraction = 0.0 if key in skipped else float(slot_feedback.get(food_name, slot_feedback.get(key, default_fraction)))
        fraction = _clamp(fraction, 0.0, 1.0)
        if fraction <= 0:
            continue

        new_row = row.copy()
        new_row['portions'] = round(float(row['portions']) * fraction, 2)
        for col in ['kcal', 'carb_g', 'protein_g', 'fat_g', 'fibre_g']:
            new_row[col] = round(float(row[col]) * fraction, 1)
        rows.append(new_row)

    if not rows:
        return pd.DataFrame(columns=meal.columns)
    return pd.DataFrame(rows)[meal.columns]

def regenerate_day_after_feedback(
    original_plan,
    glucose_mg_dl=None,
    daily_kcal=None,
    diet=None,
    actual_intake=None,
    not_eaten=None,
    completed_slots=None,
    burned_kcal_so_far=0.0,
    burn_compensation_ratio=0.50,
    max_extra_kcal_ratio=0.35,
    seed=None,
    previous_week_used=None,
):
    """
    Recalculate the rest of today's diet after the user reports not eating
    some foods or eating partial portions.

    Typical app use after lunch:
        updated = regenerate_day_after_feedback(
            original_plan=morning_plan,
            actual_intake={
                "breakfast": {"__default__": 1.0},
                "lunch": {"__default__": 1.0}
            },
            not_eaten={"lunch": ["Chapati/Roti", "Cucumber raita"]},
            completed_slots=["breakfast", "lunch"],
        )

    If lunch is skipped fully:
        updated = regenerate_day_after_feedback(
            original_plan=plan,
            actual_intake={"breakfast": {"__default__": 1.0}, "lunch": {"__default__": 0.0}},
            completed_slots=["breakfast", "lunch"],
        )
    """
    base_summary = original_plan.get('summary', {})
    glucose_mg_dl = glucose_mg_dl if glucose_mg_dl is not None else base_summary.get('glucose_mg_dl', 130)
    daily_kcal = daily_kcal if daily_kcal is not None else base_summary.get('daily_kcal_target', 2200)
    diet = diet if diet is not None else base_summary.get('diet', 'veg')

    intake = summarize_actual_intake_from_plan(
        original_plan,
        actual_intake=actual_intake,
        not_eaten=not_eaten,
        completed_slots=completed_slots,
        previous_week_used=previous_week_used,
    )
    next_slot = _next_slot_after(intake['completed_slots'])

    meals = {}
    for slot in APP_MEAL_ORDER:
        if slot in intake['completed_slots']:
            meals[slot] = _actual_meal_from_feedback(
                original_plan.get(slot),
                slot_feedback=(actual_intake or {}).get(slot, {}),
                skipped_names=(not_eaten or {}).get(slot, []),
            )
        else:
            meals[slot] = pd.DataFrame(columns=OUTPUT_COLS + INTERNAL_COLS)

    if next_slot is not None:
        replanned = generate_dynamic_plan(
            glucose_mg_dl=glucose_mg_dl,
            daily_kcal=daily_kcal,
            diet=diet,
            current_slot=next_slot,
            consumed_kcal_so_far=intake['consumed_kcal_so_far'],
            burned_kcal_so_far=burned_kcal_so_far,
            burn_compensation_ratio=burn_compensation_ratio,
            max_extra_kcal_ratio=max_extra_kcal_ratio,
            seed=seed,
            week_used=intake['week_used'],
            already_used_foods=intake['already_used_foods'],
        )
        for slot in replanned['summary']['remaining_slots']:
            meals[slot] = replanned[slot]
        week_used = replanned['week_used']
        dynamic_summary = replanned['summary']
    else:
        week_used = intake['week_used']
        dynamic_summary = {}

    non_empty = [m for m in meals.values() if not m.empty]
    all_items = pd.concat(non_empty) if non_empty else pd.DataFrame(columns=OUTPUT_COLS + INTERNAL_COLS)
    meal_kcal = {s: round(_meal_kcal(meals[s]), 1) for s in APP_MEAL_ORDER}
    total_kcal = round(float(all_items['kcal'].sum()), 1) if not all_items.empty else 0.0

    summary = {
        'glucose_mg_dl': glucose_mg_dl,
        'status': glucose_status(glucose_mg_dl),
        'diet': diet,
        'daily_kcal_target': float(daily_kcal),
        'completed_slots': intake['completed_slots'],
        'next_slot': next_slot,
        'remaining_slots': [] if next_slot is None else dynamic_summary.get('remaining_slots', []),
        'consumed_kcal_so_far': intake['consumed_kcal_so_far'],
        'consumed_by_slot': intake['consumed_by_slot'],
        'skipped_foods': intake['skipped_foods'],
        'total_kcal': total_kcal,
        'pct_achieved': round((total_kcal / (float(daily_kcal) + 1e-9)) * 100, 1),
        'meal_kcal': meal_kcal,
        'total_carb_g': round(float(all_items['carb_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_protein_g': round(float(all_items['protein_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_fat_g': round(float(all_items['fat_g'].sum()), 1) if not all_items.empty else 0.0,
        'total_fibre_g': round(float(all_items['fibre_g'].sum()), 1) if not all_items.empty else 0.0,
        'dynamic': dynamic_summary,
        'meat_items_week': _count_meat_items(week_used),
    }

    return {
        'breakfast': _public_meal(meals['breakfast']),
        'lunch': _public_meal(meals['lunch']),
        'snack': _public_meal(meals['snack']),
        'dinner': _public_meal(meals['dinner']),
        'summary': summary,
        'week_used': week_used,
        'confirmed_week_used': intake['week_used'],
    }

def generate_dynamic_meal(
    glucose_mg_dl=130,
    daily_kcal=2400,
    diet='veg',
    meal_slot='breakfast',
    consumed_kcal_so_far=0.0,
    burned_kcal_so_far=0.0,
    burn_compensation_ratio=0.65,
    max_extra_kcal_ratio=0.50,
    seed=None,
    week_used=None,
    already_used_foods=None,
):
    """
    Generate only one meal slot dynamically using current intake/activity values.
    """
    assert diet in ('veg', 'egg', 'nonveg'), "diet must be 'veg', 'egg', or 'nonveg'"
    if meal_slot not in MEAL_ORDER:
        raise ValueError(f"meal_slot must be one of {MEAL_ORDER}")
    if seed is not None:
        random.seed(seed); np.random.seed(seed)
    if week_used is None:
        week_used = {}
    if already_used_foods is None:
        already_used_foods = []

    C_base, C_dyn, remaining_slots, burn_ratio, burn_credit = _build_dynamic_constraints(
        glucose_mg_dl=glucose_mg_dl,
        daily_kcal=daily_kcal,
        current_slot=meal_slot,
        consumed_kcal_so_far=consumed_kcal_so_far,
        burned_kcal_so_far=burned_kcal_so_far,
        burn_compensation_ratio=burn_compensation_ratio,
        max_extra_kcal_ratio=max_extra_kcal_ratio,
    )
    C_base = tune_constraints_for_diet(C_base, glucose_mg_dl, daily_kcal, diet)
    C_dyn = tune_constraints_for_diet(C_dyn, glucose_mg_dl, daily_kcal, diet)

    day_used = set(already_used_foods)
    day_state = {'last_grain': _infer_last_grain(already_used_foods)}
    meat_so_far = _count_meat_items(week_used)
    force_lunch_meat = (diet == 'nonveg' and meat_so_far < 4)
    force_dinner_meat = (diet == 'nonveg' and meat_so_far < 7)

    if meal_slot == 'breakfast':
        meal = build_breakfast(pool, C_dyn, day_used, week_used, diet, day_state)
    elif meal_slot == 'lunch':
        meal = build_thali(
            pool, 'lunch', C_dyn, day_used, week_used, diet,
            avoid_grain=day_state.get('last_grain'),
            force_meat=force_lunch_meat
        )
    elif meal_slot == 'dinner':
        meal = build_thali(
            pool, 'dinner', C_dyn, day_used, week_used, diet,
            lighter=True,
            avoid_grain=day_state.get('last_grain'),
            force_meat=force_dinner_meat
        )
    else:
        meal = build_snack(pool, C_dyn, day_used, week_used, diet)

    generated_kcal = round(float(meal['kcal'].sum()), 1) if not meal.empty else 0.0
    target_with_activity = round(float(daily_kcal) + burn_credit, 1)
    projected_day_kcal = round(float(consumed_kcal_so_far) + generated_kcal, 1)

    summary = {
        'glucose_mg_dl': glucose_mg_dl,
        'status': glucose_status(glucose_mg_dl),
        'diet': diet,
        'meal_slot': meal_slot,
        'remaining_slots': remaining_slots,
        'daily_kcal_target': float(daily_kcal),
        'consumed_kcal_so_far': round(float(consumed_kcal_so_far), 1),
        'burned_kcal_so_far': round(float(burned_kcal_so_far), 1),
        'burn_compensation_ratio': burn_ratio,
        'burn_credit_applied': round(burn_credit, 1),
        'target_with_activity': target_with_activity,
        'meal_kcal_target': round(C_dyn[meal_slot]['kcal_target'], 1),
        'meal_kcal_generated': generated_kcal,
        'projected_day_kcal_after_meal': projected_day_kcal,
        'projected_pct_of_target': round((projected_day_kcal / (target_with_activity + 1e-9)) * 100, 1),
        'meal_carb_g': round(float(meal['carb_g'].sum()), 1) if not meal.empty else 0.0,
        'meal_protein_g': round(float(meal['protein_g'].sum()), 1) if not meal.empty else 0.0,
        'meal_fat_g': round(float(meal['fat_g'].sum()), 1) if not meal.empty else 0.0,
        'meal_fibre_g': round(float(meal['fibre_g'].sum()), 1) if not meal.empty else 0.0,
        'kcal_targets': {s: C_dyn[s]['kcal_target'] for s in C_dyn},
        'meat_items_week': _count_meat_items(week_used),
    }

    return {'meal': _public_meal(meal), 'summary': summary, 'week_used': week_used}

def generate_daily_plan(glucose_mg_dl=130, daily_kcal=2400, diet='veg', seed=None, week_used=None):
    """
    Generate one day's meal plan.
    Pass week_used back into every subsequent call for multi-day variety.
    week_used: dict[str, list[tuple[food_name, food_subcat]]]
    """
    assert diet in ('veg','egg','nonveg'), "diet must be 'veg', 'egg', or 'nonveg'"
    if seed is not None: random.seed(seed); np.random.seed(seed)
    if week_used is None: week_used = {}
    C = tune_constraints_for_diet(get_constraints(glucose_mg_dl, daily_kcal), glucose_mg_dl, daily_kcal, diet)
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

    meals = rescue_day_calories(
        {'breakfast': breakfast, 'lunch': lunch, 'dinner': dinner, 'snack': snack},
        C,
        daily_kcal,
        diet,
    )
    breakfast, lunch, dinner, snack = meals['breakfast'], meals['lunch'], meals['dinner'], meals['snack']

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
    return dict(
        breakfast=_public_meal(breakfast),
        lunch=_public_meal(lunch),
        dinner=_public_meal(dinner),
        snack=_public_meal(snack),
        summary=summary,
        week_used=week_used,
    )


FMT = {'portions':'{:.2g}','kcal':'{:.0f}','carb_g':'{:.1f}','protein_g':'{:.1f}',
       'fat_g':'{:.1f}','fibre_g':'{:.1f}','glycemic_score':'{:.3f}','composite_score':'{:.3f}'}

def display_plan(plan, title='HealthSYNQ Diet Plan', show_scores=True):
    s = plan['summary']
    pct = s.get('pct_achieved', 0)
    filled = max(0, min(20, int(pct // 5)))
    bar = '#' * filled + '-' * (20 - filled)
    slots = ['breakfast', 'lunch', 'snack', 'dinner']
    show_cols = [
        'food_code', 'food_name', 'food_role', 'food_subcat', 'serving_unit',
        'portions', 'kcal', 'carb_g', 'protein_g', 'fat_g', 'fibre_g',
    ]
    if show_scores:
        show_cols += ['glycemic_score', 'composite_score']

    print('=' * 100)
    print(f'  {title}')
    print('=' * 100)
    print(f"  Glucose : {s['glucose_mg_dl']} mg/dL [{s['status']}]")
    print(f"  Diet    : {s['diet'].upper()}")
    print(f"  Target  : {s['daily_kcal_target']:.0f} kcal | Generated: {s['total_kcal']:.0f} kcal ({pct:.1f}%)")
    if 'completed_slots' in s:
        print(f"  Completed: {s['completed_slots']} | Remaining: {s['remaining_slots']} | Consumed: {s['consumed_kcal_so_far']:.0f} kcal")
    print(f'  [{bar}]')

    for slot in slots:
        meal = plan[slot]
        got = s['meal_kcal'].get(slot, 0.0)
        tgt = s.get('kcal_targets', {}).get(slot)
        if tgt:
            target_text = f'Target {tgt:.0f} kcal -> {got:.0f} kcal ({got / (tgt + 1e-9) * 100:.0f}%)'
        else:
            target_text = f'Generated {got:.0f} kcal'
        valid_text = _meal_status_text(meal, slot, s)

        print('\n' + '-' * 100)
        print(f'  {slot.upper()} | {target_text} | {valid_text}')
        print('-' * 100)
        if meal.empty:
            print('  No items')
            continue
        cols = [c for c in show_cols if c in meal.columns]
        formatted = meal[cols].copy()
        for col, fmt in FMT.items():
            if col in formatted.columns:
                formatted[col] = formatted[col].map(lambda v, f=fmt: f.format(float(v)))
        print(formatted.to_string(index=False))

    print('\n' + '=' * 100)
    print('  DAILY TOTALS')
    print(f"  Energy : {s['total_kcal']:.0f}/{s['daily_kcal_target']:.0f} kcal ({pct:.1f}%)")
    print(f"  Carbs  : {s['total_carb_g']:.1f} g")
    print(f"  Protein: {s['total_protein_g']:.1f} g")
    print(f"  Fat    : {s['total_fat_g']:.1f} g")
    print(f"  Fibre  : {s['total_fibre_g']:.1f} g")
    print('=' * 100)

