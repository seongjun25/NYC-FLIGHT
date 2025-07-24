import pandas as pd
import nycflights13 as flights

df_planes = flights.planes
flights.planes.shape #(3322, 9)
df_planes.info()

# 엔진 수 & 엔진 종류별 여객기 수 세기
grouped_tailnums = (
    df_planes
    .groupby(['engines', 'engine'], as_index=False)['tailnum']
    .count()
    .rename(columns={'tailnum': 'tailnum_count'})
    .sort_values(['engines', 'engine'])
)

print(grouped_tailnums)

# 좌석 수에 따라 분류
print(df_planes['seats']
      .sort_values()
      .drop_duplicates()
      .reset_index(drop=True)
      .head())

print(df_planes['seats']
      .sort_values()
      .drop_duplicates()
      .reset_index(drop=True)
      .tail())

# 좌석 수에 따라 분류 후 해당 좌석을 가진 여객기의 수가 100대가 넘는 경우만 필터링
seat_counts = (
    df_planes
    .groupby('seats')['tailnum']
    .nunique()                          # 고유한 tailnum 개수
    .reset_index(name='plane_count')    # 결과를 DataFrame으로 변환
    .sort_values('seats')               # seats 오름차순 정렬
)

print(seat_counts[seat_counts['plane_count'] > 100])

# 100종이 넘는 여객기의 좌석 수의 종류
# [55, 95, 100, 140, 142, 149, 178, 179, 182, 200, 330]

selected_seats = [55, 95, 100, 140, 142, 149, 178, 179, 182, 200, 330]

# 조건에 맞는 행만 추출 → tailnum 고유 개수 계산
count = (
    df_planes[
        df_planes['seats'].isin(selected_seats) &           # 지정된 좌석 수
        (df_planes['engines'] == 2) &                       # 엔진 수가 2
        df_planes['engine'].isin(['Turbo-fan', 'Turbo-jet'])# 엔진 종류
    ]['tailnum']
    .nunique()
)

print(f"조건에 맞는 여객기 수: {count}")

result_by_seat = (
    df_planes[
        df_planes['seats'].isin(selected_seats) &
        (df_planes['engines'] == 2) &
        df_planes['engine'].isin(['Turbo-fan', 'Turbo-jet'])
    ]
    .groupby('seats')['tailnum']
    .nunique()
    .reset_index(name='plane_count')
    .sort_values('seats')
)

result_by_seat

# 위 좌석을 가지는 여객기들은 모두 엔진 2개, Turbo-fan or Turbo-jet

## 스케일링
import numpy as np

# 위 필터링을 거친 여객기 정보를 년도 구간에 따라 분류
# 이 때 결측치 생략 (2582 -> 2537)
seat_list = [55, 95, 100, 140, 142, 149, 178, 179, 182, 200, 330]

filtered = df_planes[
    (df_planes['engines'] == 2) &
    (df_planes['engine'].isin(['Turbo-fan', 'Turbo-jet'])) &
    (df_planes['seats'].isin(seat_list))
].copy()

bins = [-np.inf, 1993, 2003, 2013]
labels = ['before_1994', '1994~2003', '2004~2013']

filtered['period'] = pd.cut(
    filtered['year'],
    bins=bins,
    labels=labels,
    right=True
)

filtered = filtered.dropna(subset=['period'])

period_counts = filtered.groupby('period')['tailnum'] \
                         .nunique() \
                         .sort_index()

print(period_counts)

#    설정한 조건에 따른 여객기의 수
#    필터링: 
#    - 엔진수 2개 
#    - 엔진 종류 Turbo‑fan 또는 Turbo‑jet 
#    - 관심 좌석 수 
#    - 제작년도(year) 결측치 제외
mask = (
    (df_planes['engines'] == 2) &
    (df_planes['engine'].isin(['Turbo-fan', 'Turbo-jet'])) &
    (df_planes['seats'].isin(seat_list)) &
    df_planes['year'].notnull()
)
df_f = df_planes.loc[mask].copy()

# 2) 제작년도(period) 구간화
bins_year   = [-np.inf, 1993, 2003, 2013]
labels_year = ['1994년 이전', '1994~2003', '2004~2013']
df_f['period'] = pd.cut(df_f['year'], bins=bins_year, labels=labels_year, right=True)
df_f = df_f[df_f['period'].notnull()].copy()  # 2014년 이후 제거
df_f['period'] = df_f['period'].astype(str)

# 3) 좌석수(size) 구간화
bins_seat   = [-np.inf, 150, 300, np.inf]
labels_seat = ['소형', '중형', '대형']
df_f['size'] = pd.cut(df_f['seats'], bins=bins_seat, labels=labels_seat, right=True).astype(str)

# 4) 그룹화: seats → period → engine 순으로 고유 tailnum 개수 집계
grouped = (
    df_f
    .groupby(['seats', 'size', 'period', 'engine'], as_index=False)
    .agg(tailnum_count=('tailnum', 'nunique'))
    .sort_values(['seats', 'size', 'period', 'engine'])
)

grouped

# 구간에 따른 점수 설정 후 각 항공기마다 점수 부여
import numpy as np

size_weights = {
    '소형': 1,
    '중형': 2,
    '대형': 3
}
period_weights = {
    '1994년 이전': 1,
    '1994~2003':    2,
    '2004~2013':    3
}
engine_weights = {
    'Turbo-jet':  1,
    'Turbo-fan':  2
}

# 1) 점수 계산 (합산 후 제곱근)
df_f['score'] = np.sqrt(
    df_f['size'].map(size_weights) +
    df_f['period'].map(period_weights) +
    df_f['engine'].map(engine_weights)
)

# 2) 소수점 셋째 자리에서 절삭(truncate)
df_f['score'] = np.trunc(df_f['score'] * 1000) / 1000

result  = df_f[['tailnum', 'size', 'period', 'engine', 'score']]
result1 = df_f[['tailnum', 'score']]

print(result)
print(result1)

# 가산치 적용 점수 부여 알고리즘 

import math                  

size_weights   = {'소형': 1, '중형': 2, '대형': 3}
period_weights = {'1994년 이전': 1, '1994~2003': 2, '2004~2013': 3}
engine_weights = {'Turbo-jet': 1, 'Turbo-fan': 2}

plane_info = df_f.set_index('tailnum')[['size','period','engine']].to_dict(orient='index'
                                                                           )
def compute_score_by_tailnum(
    tailnum: str,
    importance: dict[str, float] | None = None
) -> float:
    """
    size, period, engine 항목별 (가중치 ** 중요도) 값을 더한 뒤
    그 합의 제곱근을 최종 점수로 반환합니다.

        total  = (sw ** imp_size) + (pw ** imp_period) + (ew ** imp_engine)
        score  = sqrt(total)
    """
    info = plane_info.get(tailnum)
    if info is None:
        raise ValueError(f"'{tailnum}' 정보를 찾을 수 없습니다.")

    sw = size_weights.get(info['size'])
    pw = period_weights.get(info['period'])
    ew = engine_weights.get(info['engine'])
    if sw is None or pw is None or ew is None:
        raise ValueError(f"'{tailnum}'의 정보({info})에 매핑되지 않은 값이 있습니다.")

    if importance is None:
        importance = {'size': 1.0, 'period': 1.0, 'engine': 1.0}

    imp_size   = importance.get('size',   1.0)
    imp_period = importance.get('period', 1.0)
    imp_engine = importance.get('engine', 1.0)

    total = (sw ** imp_size) + (pw ** imp_period) + (ew ** imp_engine)
    score = math.sqrt(total)

    return score

# 사용 툴 ─────────────────────────────────────────
importance = {'size': 1.0, 'period': 1.0, 'engine': 1.0}  
for tail in ['N10156']:
    try:
        sc = compute_score_by_tailnum(tail, importance=importance)
        print(f"{tail} 의 가중치 적용 최종 점수(√합): {sc:.3f}")
    except ValueError as e:
        print(e)
#───────────────────────────────────────────────────

# 각 기준치에 따른 여객기의 수 (막대그래프)

import matplotlib.pyplot as plt
import matplotlib as mpl

# 한글 폰트 설정 (맑은 고딕)
mpl.rcParams['font.family'] = 'Malgun Gothic'
mpl.rcParams['axes.unicode_minus'] = False

# 1) 각 항목별 고유 tailnum 개수 계산
size_counts   = df_f.groupby('size')['tailnum'].nunique().sort_index()
period_counts = df_f.groupby('period')['tailnum'].nunique().sort_index()
engine_counts = df_f.groupby('engine')['tailnum'].nunique().sort_index()

# 2) 1행 3열 서브플롯 생성
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- (1) 크기(size)별 ---
axes[0].bar(size_counts.index, size_counts.values, color='skyblue', alpha=0.7)
axes[0].set_title('크기별 항공기 수')
axes[0].set_xlabel('크기')
axes[0].set_ylabel('항공기 수')
for i, v in enumerate(size_counts.values):
    axes[0].text(i, v + max(size_counts)*0.01, str(v), ha='center', va='bottom')

# --- (2) 제작년도 구간(period)별 ---
axes[1].bar(period_counts.index.astype(str), period_counts.values, color='lightgreen', alpha=0.7)
axes[1].set_title('제작년도 구간별 항공기 수')
axes[1].set_xlabel('제작년도 구간')
axes[1].set_ylabel('항공기 수')
for i, v in enumerate(period_counts.values):
    axes[1].text(i, v + max(period_counts)*0.01, str(v), ha='center', va='bottom')

# --- (3) 엔진 종류(engine)별 ---
axes[2].bar(engine_counts.index, engine_counts.values, color='salmon', alpha=0.7)
axes[2].set_title('엔진 종류별 항공기 수')
axes[2].set_xlabel('엔진 종류')
axes[2].set_ylabel('항공기 수')
for i, v in enumerate(engine_counts.values):
    axes[2].text(i, v + max(engine_counts)*0.01, str(v), ha='center', va='bottom')

plt.tight_layout()
plt.show()

# 2013.07.25 항공편 필터링 후 항공기에 따른 점수 표기 
# 후 내림차순 정렬 (점수가 결측치인 행 생략 + 중복 생략)
# 462 
import pandas as pd

df_flights = flights.flights

filtered = df_flights[
    (df_flights['month'] == 7) &
    (df_flights['day']   == 25) &
    (df_flights['tailnum'].notnull())
][['year', 'month', 'day', 'tailnum']]

merged = (
    pd.merge(
        filtered,
        result[['tailnum', 'score']],
        on='tailnum',
        how='left'
    )
    .dropna(subset=['score'])
    .sort_values('score', ascending=False)
    .drop_duplicates(subset='tailnum', keep='first')  # ← 중복 tailnum 제거
    .reset_index(drop=True)
)

print(merged)

# 2013.07.25 비행하는 최고점 여객기 종류(73)
print(merged.loc[merged['score'] == 2.645, 'tailnum'].unique().tolist())

# 2013.07.25 비행하는 여객기 점수(막대그래프)

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams['font.family'] = 'Malgun Gothic'
mpl.rcParams['axes.unicode_minus'] = False

# Score별 고유 tailnum 수 집계
score_counts = merged.groupby('score')['tailnum'] \
                     .nunique() \
                     .sort_index()

max_score = score_counts.index.max()

# 최고 점수 막대만 빨강, 나머지는 하늘색
colors = ['red' if score == max_score else 'skyblue'
          for score in score_counts.index]

# 막대 너비 정의
bar_width = 0.6

plt.figure(figsize=(8, 5))
plt.bar(
    score_counts.index.astype(str),
    score_counts.values,
    width=bar_width,
    color=colors,
    alpha=0.7
)
plt.title('Score별 항공기 수')
plt.xlabel('Score')
plt.ylabel('항공기 수')

# 값 레이블 추가
for i, v in enumerate(score_counts.values):
    plt.text(i, v + max(score_counts)*0.01, str(v),
             ha='center', va='bottom')

plt.tight_layout()
plt.show()

#레이더 차트

