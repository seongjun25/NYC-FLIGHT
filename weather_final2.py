import pandas as pd
import nycflights13 as flights

# 항공편 데이터 (main dataset)
df_flights = flights.flights
df_airlines = flights.airlines
df_airports = flights.airports
df_planes = flights.planes
df_weather = flights.weather

df_flights.head()
df_flights.info()
print("flights:", df_flights.columns)

df_weather.head()
df_weather.info()
print("weather:", df_weather.columns)


########### 날씨 평가 변수 선정 ###########
df_weather.isna().sum()
# origin            0
# year              0
# month             0
# day               0
# hour              0
# temp              1
# dewp              1
# humid             1
# wind_dir        460   제거
# wind_speed        4
# wind_gust     20778   제거
# precip            0
# pressure       2729   제거
# visib             0
# time_hour         0


# 'wind_speed', 'dewp', 'humid', 'visib', 'precip' 분위수 계산 (20%, 40%, 60%, 80%)
# 사용할 변수
weather_test = ['wind_speed', 'dewp', 'humid', 'visib', 'precip']
# 1. 결측치 제거
df_weather_clean = df_weather.dropna(subset=weather_test).copy()
# 2. 분위수 계산 (20%, 40%, 60%, 80%)
quantiles = df_weather_clean[weather_test].quantile([0.2, 0.4, 0.6, 0.8])
print(quantiles)

#      wind_speed   dewp  humid  visib  precip
# 0.2     5.75390  23.00  44.16   10.0     0.0
# 0.4     8.05546  35.06  55.56   10.0     0.0
# 0.6    11.50780  48.92  67.92   10.0     0.0
# 0.8    14.96014  60.98  82.45   10.0     0.0

# visib, precip 제거

# 최종 날씨 평가 변수 : wind_speed, dewp, humid
weather_vars = ['wind_speed', 'dewp', 'humid']

# 1. 결측치 제거
df_weather_clean = df_weather.dropna(subset=weather_vars).copy()

# 2. 분위수 계산 (20%, 40%, 60%, 80%)
quantiles = df_weather_clean[weather_vars].quantile([0.2, 0.4, 0.6, 0.8])
print(quantiles)

### 점수 계산 함수 정의 ###
# 단일 값에 대해 점수 계산
def get_score(value, var):
    if value <= quantiles.loc[0.2, var]:
        return 0    # 0~20% 구간 : 0점
    elif value <= quantiles.loc[0.4, var]:
        return 1    # 20~40% 구간 : 1점
    elif value <= quantiles.loc[0.6, var]:
        return 2    # 40~60% 구간 : 2점
    elif value <= quantiles.loc[0.8, var]:
        return 3    # 60~80% 구간 : 3점
    else:
        return 4    # 80~100% 구간 : 4점

# 한 행(row)에 대해 세 변수 점수를 합산
def calc_total_score(row):
    total = 0
    for var in weather_vars:
        total += get_score(row[var], var)
    return total

### 전체 데이터에 날씨 점수 및 등급 부여 ###
# 점수 계산
df_weather_clean['weather_score'] = df_weather_clean.apply(calc_total_score, axis=1)
df_weather_clean['weather_score']
df_weather_clean['weather_score'].value_counts().sort_index()   # 0+0+0 ~ 4+4+4

# 점수를 기준으로 등급 매기기 (총점: 0~12점)
def score_to_grade(score):
    if score >= 9:         # 9~12
        return '하'
    elif score >= 7:       # 7~8
        return '중하'
    elif score >= 5:       # 5~6
        return '중'
    elif score >= 3:       # 3~4
        return '중상'
    else:                  # 0~2
        return '상'

df_weather_clean['weather_grade'] = df_weather_clean['weather_score'].apply(score_to_grade)
df_weather_clean['weather_grade']
df_weather_clean['weather_grade'].value_counts().sort_index()


##############################################################################################
########################## 날씨 등급별 평균 지연 시간 시각화 ##################################
import pandas as pd
import matplotlib.pyplot as plt

# 한글 폰트 및 마이너스 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 등급 순서 및 색상 정의
grade_order = ['상', '중상', '중', '중하', '하']
grade_colors = {
    '상': '#3498db',   # 파랑
    '중상': '#2ecc71', # 초록
    '중': '#f1c40f',    # 노랑
    '중하': '#e67e22',  # 주황
    '하': '#e74c3c'     # 빨강
}

# 관측 수 (weather 데이터 기준)
weather_counts = df_weather_clean['weather_grade'].value_counts().reindex(grade_order)

# 평균 지연 시간 (15분 이상 지연만 포함)
df_merged = pd.merge(
    df_flights,
    df_weather_clean[['origin', 'time_hour', 'weather_grade']],
    how='left',
    on=['origin', 'time_hour']
)
df_filtered = df_merged.dropna(subset=['dep_delay', 'weather_grade'])
df_filtered = df_filtered[df_filtered['dep_delay'] >= 15]
avg_delay = df_filtered.groupby('weather_grade')['dep_delay'].mean().reindex(grade_order)

# ──────────────────────────────
# ▶ 이중축 그래프 생성
fig, ax1 = plt.subplots(figsize=(8, 5))

# 막대 그래프: 관측 수
bars = ax1.bar(
    grade_order,
    weather_counts,
    color=[grade_colors[g] for g in grade_order],
    alpha=0.8,
    label='관측 수'
)
ax1.set_ylabel('관측 수 (건)', fontsize=12)
ax1.set_xlabel('날씨 등급', fontsize=12)
ax1.tick_params(axis='y', labelcolor='black')

# 막대 위 수치
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, height + 100,
             f'{int(height):,}건', ha='center', fontsize=9)

# 선 그래프: 평균 지연 시간 (점선 + 빨간색)
ax2 = ax1.twinx()
ax2.plot(
    grade_order,
    avg_delay,
    color='red',          # ▶ 빨간색
    marker='o',
    linestyle='--',       # ▶ 점선 스타일
    linewidth=2.5,
    label='평균 지연 시간'
)
ax2.set_ylabel('평균 지연 시간 (분)', fontsize=12)
ax2.tick_params(axis='y', labelcolor='black')

# 선 위/아래 수치 표시
for i, value in enumerate(avg_delay):
    grade = grade_order[i]
    if grade in [ '하']:
        va = 'top'
        offset = -1.5
    else:
        va = 'bottom'
        offset = 1.5
    ax2.text(i, value + offset, f'{value:.1f}분',
             color='red', ha='center', va=va, fontsize=9, fontweight='bold')

# 제목 및 범례
plt.title('날씨 등급별 관측 수 및 평균 지연 시간 (15분 이상)', fontsize=14, weight='bold')
fig.legend(loc='upper left', bbox_to_anchor=(0.02, 0.95), bbox_transform=ax1.transAxes)

plt.tight_layout()
plt.show()


###############################################################################################
################################### 날씨 등급별 정시/지연 비율 #################################

# 결측치 제거 (dep_delay, weather_grade 기준)
df_dep_delay_by_grade = df_merged.dropna(subset=['dep_delay', 'weather_grade'])
# 지연 여부 플래그 추가 (에러 방지 위해 dropna 후 처리)
df_dep_delay_by_grade['delay_flag'] = df_dep_delay_by_grade['dep_delay'].apply(lambda x: '지연' if x >= 15 else '정시')

# 시각화
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8, 5))
ax = sns.countplot(
    data=df_dep_delay_by_grade,
    x='weather_grade',
    hue='delay_flag',
    order=['상', '중상', '중', '중하', '하'],
    palette={'정시': '#2ecc71', '지연': '#e74c3c'}
)

# ③ 각 막대 위에 항공편 수(카운트) 표시
for container in ax.containers:
    ax.bar_label(container, fmt='%d', label_type='edge', fontsize=9, padding=3)

# ④ 그래프 꾸미기
plt.title('날씨 등급별 정시/지연 항공편 수', fontsize=14, weight='bold')
plt.xlabel('날씨 등급', fontsize=12)
plt.ylabel('항공편 수', fontsize=12)
plt.legend(title='운항 상태')
plt.tight_layout()
plt.show()


#############################################################################################
######################## 날씨 등급별 정시/지연 비율 막대 그래프 ##############################
# 1. 정시/지연 레이블 생성
df_delay_flag = df_merged.dropna(subset=['dep_delay', 'weather_grade']).copy()
df_delay_flag['delay_flag'] = df_delay_flag['dep_delay'].apply(lambda x: '지연' if x >= 15 else '정시')

# 2. 날씨 등급 + 운항상태별 count
count_data = df_delay_flag.groupby(['weather_grade', 'delay_flag']).size().reset_index(name='count')

# 3. 날씨 등급별 전체 항공편 수 → 비율 계산
total_per_grade = count_data.groupby('weather_grade')['count'].transform('sum')
count_data['ratio'] = count_data['count'] / total_per_grade * 100

# 등급 순서 강제 지정
grade_order = ['상', '중상', '중', '중하', '하']
delay_order = ['정시', '지연']
count_data['weather_grade'] = pd.Categorical(count_data['weather_grade'], categories=grade_order, ordered=True)
count_data['delay_flag'] = pd.Categorical(count_data['delay_flag'], categories=delay_order, ordered=True)
count_data = count_data.sort_values(['weather_grade', 'delay_flag'])

# 4. 시각화
plt.figure(figsize=(8, 5))
ax = sns.barplot(
    data=count_data,
    x='weather_grade',
    y='ratio',
    hue='delay_flag',
    palette={'정시': '#2ecc71', '지연': '#e74c3c'}
)

# 5. 막대 위에 비율 텍스트 표시
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f%%', label_type='edge', fontsize=9, padding=3)

# 6. 꾸미기
plt.title('날씨 등급별 정시/지연 비율 (%)', fontsize=14, weight='bold')
plt.xlabel('날씨 등급')
plt.ylabel('비율 (%)')
plt.ylim(0, 100)
plt.legend(title='운항 상태')
plt.tight_layout()
plt.show()


############################################################################################
#################################### 이중 막대 병합 ########################################
import matplotlib.pyplot as plt
# 사전 작업: weather_grade 기준으로 정시/지연 카운트 생성
df_clean = df_merged.dropna(subset=['dep_delay', 'weather_grade'])
df_clean['delay_flag'] = df_clean['dep_delay'].apply(lambda x: '지연' if x >= 15 else '정시')

# 항공편 수 (날씨 등급별 정시/지연 수 카운트)
count_data = df_clean.groupby(['weather_grade', 'delay_flag']).size().unstack().fillna(0)
count_data = count_data.reindex(['상', '중상', '중', '중하', '하'])  # 순서 정렬

# 비율 데이터 계산 (%로 환산)
ratio_data = count_data.divide(count_data.sum(axis=1), axis=0) * 100

# 색상 정의
bar_color_on_time = '#4e79a7'    # 정시 항공편 막대 (파랑)
bar_color_delayed = '#f28e2b'    # 지연 항공편 막대 (주황)
line_color_on_time = '#59a14f'   # 정시 선/텍스트 (녹색)
line_color_delayed = '#e15759'   # 지연 선/텍스트 (빨강)

fig, ax1 = plt.subplots(figsize=(9, 5))
bar_width = 0.4
x = range(len(count_data))

# 막대그래프 (정시/지연 항공편 수)
bar1 = ax1.bar([i - bar_width/2 for i in x], count_data['정시'], width=bar_width,
               label='정시 항공편 수', color=bar_color_on_time)
bar2 = ax1.bar([i + bar_width/2 for i in x], count_data['지연'], width=bar_width,
               label='지연 항공편 수', color=bar_color_delayed)

ax1.set_xlabel('날씨 등급', fontsize=12)
ax1.set_ylabel('항공편 수', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(count_data.index, fontsize=11)

# 이중축 선그래프 (정시/지연 비율)
ax2 = ax1.twinx()
line1, = ax2.plot(x, ratio_data['정시'], color=line_color_on_time,
                  marker='o', linewidth=2.5, label='정시 비율')
line2, = ax2.plot(x, ratio_data['지연'], color=line_color_delayed,
                  marker='o', linewidth=2.5, label='지연 비율')
ax2.set_ylabel('비율 (%)', fontsize=12)
ax2.set_ylim(0, 100)

# 비율 텍스트 (막대 위, 선 색과 동일하게)
for i in x:
    ax2.text(i, ratio_data['정시'].iloc[i] + 3,
             f"{ratio_data['정시'].iloc[i]:.1f}%", color=line_color_on_time,
             ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax2.text(i, ratio_data['지연'].iloc[i] + 3,
             f"{ratio_data['지연'].iloc[i]:.1f}%", color=line_color_delayed,
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# 제목 및 범례 (병합)
plt.title('날씨 등급별 정시/지연 항공편 수 및 비율', fontsize=14, weight='bold')
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(handles1 + handles2, labels1 + labels2, loc='upper right')

plt.tight_layout()
plt.show()


################################################################################################
######################### 풍속, 이슬점, 습도 vs 지연시간 분포 ###################################

# 기존 merge 코드에 날씨 변수들도 포함시켜서 병합
weather_cols = ['origin', 'time_hour', 'weather_grade', 'weather_score', 'wind_speed', 'dewp', 'humid']

df_merged = pd.merge(
    df_flights,
    df_weather_clean[weather_cols],
    how='left',
    on=['origin', 'time_hour']
)

import matplotlib.pyplot as plt
import seaborn as sns

# 필요한 컬럼만 추출하고 NaN 제거
cols = ['wind_speed', 'dewp', 'humid', 'dep_delay', 'weather_grade']
df_plot = df_merged[cols].dropna()

# 등급 순서와 색상 정의
grade_order = ['상', '중상', '중', '중하', '하']
grade_palette = {
    '상': '#3498db',   # 파랑
    '중상': '#2ecc71', # 초록
    '중': '#f1c40f',   # 노랑
    '중하': '#e67e22', # 주황
    '하': '#e74c3c'    # 빨강
}

plt.figure(figsize=(18, 5))

# wind_speed vs dep_delay
plt.subplot(1, 3, 1)
sns.scatterplot(data=df_plot, x='wind_speed', y='dep_delay', hue='weather_grade',
                palette=grade_palette, hue_order=grade_order, alpha=0.5)
plt.title('풍속 vs 출발 지연 시간')
plt.xlabel('풍속 (m/s)')
plt.ylabel('지연 시간 (분)')
plt.legend().remove()

# dewp vs dep_delay
plt.subplot(1, 3, 2)
sns.scatterplot(data=df_plot, x='dewp', y='dep_delay', hue='weather_grade',
                palette=grade_palette, hue_order=grade_order, alpha=0.5)
plt.title('이슬점 vs 출발 지연 시간')
plt.xlabel('이슬점 (°C)')
plt.ylabel('')
plt.legend().remove()

# humid vs dep_delay
plt.subplot(1, 3, 3)
sns.scatterplot(data=df_plot, x='humid', y='dep_delay', hue='weather_grade',
                palette=grade_palette, hue_order=grade_order, alpha=0.5)
plt.title('습도 vs 출발 지연 시간')
plt.xlabel('습도 (%)')
plt.ylabel('')
plt.legend().remove()

plt.tight_layout()
plt.legend(title='날씨 등급', loc='center left', bbox_to_anchor=(1, 0.5))  # 범례를 우측에 통합 배치
plt.show()
