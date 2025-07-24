import pandas as pd
import nycflights13 as flights


df_airlines = flights.airlines
df_airports = flights.airports
df_planes = flights.planes
df_weather = flights.weather

df_airports = pd.read_csv(
    r"C:\Users\an100\OneDrive\바탕 화면\airports_data.csv",
    usecols=['faa','name']
)

df_flights = pd.read_csv(
    r"C:\Users\an100\OneDrive\바탕 화면\flights_data.csv",
    usecols=['origin','dest','distance','air_time']
)


print(df_flights['origin'].unique()) #3개
print(df_flights['dest'].unique()) #105개

#비행시간이 짧은 노선, 항공사 추천

df_flights = flights.flights
df_flights.info()
# -------------------------------------------
###1 실제 비행시간이 짧았던 항공편 추출
# 결측값 제거 (air_time이 없는 항공편 제거)
df_clean = df_flights.dropna(subset=['air_time'])
# (336776->327346)

# 1. 비행시간 기준 하위 10% 커트라인 구하기
short_time_cutoff = df_clean['air_time'].quantile(0.1)
#비행시간이 가장 짧은 하위 10%구간이 47분 이내
# 데이터의 분위수(quantile)를 계산합니다. 
# 쉽게 말해 “위에서부터 몇 % 지점에 해당하는 값”을 구하는 함수예요.
# 0.1을 넣으면 하위 10퍼센트 값을 구할 수 있음.

# 2. 실제 비행시간이 짧았던 항공편 선별
short_flights = df_clean[df_clean['air_time'] <= short_time_cutoff]
# 아까 만들었던 short_time_cutoff를통해
# df_clean['air_time'] <= short_time_cutoff
# air_time(비행시간)이 47분인지를 True/False값으로 출력
# 그 결과 값을 새 데이터 프레임에 저장


# 3. 비행시간 기준 오름차순 정렬
short_flights_sorted = short_flights.sort_values('air_time')

# 4. 결과 확인
print("총 항공편 수:", len(df_clean))
print("비행시간이 짧은 하위 10% 항공편 수:", len(short_flights))
print(short_flights.sort_values('air_time').head(10))

#짧은 비행시간을 바탕으로 왜 짧을지
#--------------------------------------------------------------
###1) 거리때문일 것이다?
# 전체 평균 거리
overall_avg_distance = df_clean['distance'].mean()

# 짧은 비행시간 그룹 평균 거리
short_avg_distance = short_flights['distance'].mean()

# 출력
print(f"전체 평균 거리: {overall_avg_distance:.2f} 마일")
print(f"비행시간 짧은 그룹 평균 거리: {short_avg_distance:.2f} 마일")

# 차이 확인
if short_avg_distance < overall_avg_distance:
    print("✅ 비행시간이 짧은 이유 중 하나는 '거리 자체가 짧기 때문'일 가능성이 높습니다.")
else:
    print("❌ 거리 차이가 없거나 오히려 더 깁니다. 다른 원인을 의심해야 합니다.")

import matplotlib.pyplot as plt
##############################################################
################################################################3
###############################################################3
#################################################################3
###########################################################3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 한글 폰트 설정 (다양한 환경 대응)
import platform
import matplotlib.font_manager as fm

# 운영체제별 한글 폰트 설정
if platform.system() == 'Windows':
    # Windows에서 사용 가능한 한글 폰트들을 순서대로 시도
    font_list = ['Malgun Gothic', 'AppleGothic', 'Gulim', 'Dotum', 'NanumGothic']
    for font in font_list:
        try:
            plt.rcParams['font.family'] = font
            break
        except:
            continue
    else:
        # 모든 폰트가 실패하면 시스템 기본 폰트 사용
        plt.rcParams['font.family'] = 'DejaVu Sans'
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

# 전체 그래프 스타일 설정
sns.set_style("whitegrid")
plt.style.use('default')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 한글 폰트 설정 (다양한 환경 대응)
import platform
import matplotlib.font_manager as fm

# 운영체제별 한글 폰트 설정
if platform.system() == 'Windows':
    # Windows에서 사용 가능한 한글 폰트들을 순서대로 시도
    font_list = ['Malgun Gothic', 'AppleGothic', 'Gulim', 'Dotum', 'NanumGothic']
    for font in font_list:
        try:
            plt.rcParams['font.family'] = font
            break
        except:
            continue
    else:
        # 모든 폰트가 실패하면 시스템 기본 폰트 사용
        plt.rcParams['font.family'] = 'DejaVu Sans'
elif platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:  # Linux
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

# 전체 그래프 스타일 설정
sns.set_style("whitegrid")
plt.style.use('default')

# 2개 그래프만 표시
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 1. 거리 vs 비행시간 산점도
axes[0].scatter(df_clean['distance'], df_clean['air_time'], alpha=0.3, s=1, color='gray', label='All')
axes[0].scatter(short_flights['distance'], short_flights['air_time'], 
                alpha=0.7, s=3, color='red', label='Short Flights')
axes[0].set_title('Distance vs Flight Time Relationship', fontsize=14, fontweight='bold')
axes[0].set_xlabel('Distance (miles)')
axes[0].set_ylabel('Flight Time (minutes)')
axes[0].legend()

# 2. 평균 거리 비교 막대그래프
categories = ['Overall Average', 'Short Flights\nAverage']
distances = [overall_avg_distance, short_avg_distance]
colors = ['lightblue', 'orange']

bars = axes[1].bar(categories, distances, color=colors, edgecolor='black', linewidth=1)
axes[1].set_title('Average Distance Comparison', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Average Distance (miles)')

# 막대 위에 값 표시
for bar, distance in zip(bars, distances):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                 f'{distance:.0f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.show()

# 요약 통계 출력
print("="*60)
print("📊 Distance vs Flight Time Analysis")
print("="*60)
print(f"• Overall average distance: {overall_avg_distance:.0f} miles")
print(f"• Short flights average distance: {short_avg_distance:.0f} miles")
print(f"• Distance difference: {overall_avg_distance - short_avg_distance:.0f} miles ({(1-short_avg_distance/overall_avg_distance)*100:.1f}% shorter)")
print("\n📈 Key Insight: Short flight times are primarily due to shorter distances!")



#################################################################
#--------------------------------------------------------------
#################################################################
#################################################################
#################################################################
#################################################################
#################################################################
#################################################################
###2 비행기 속도 때문일 것이다?
# 2) 비행 속도(mile per minute) 계산
df_clean = df_clean.copy()
#안전하게 사본을 만들자
df_clean['speed_mpm'] = df_clean['distance'] / df_clean['air_time']
#속도를 구하기 위해 거리 나누기 시간

# 3) 짧은 비행시간 그룹(air_time 하위 10%) 추출 ───────────────
cutoff = df_clean['air_time'].quantile(0.10)
#비행시간이 가장 짧은 10%가 끝나는 지점이 몇 분인지 구하자
short_group  = df_clean[df_clean['air_time'] <= cutoff]
#방금 구한 기준 보다 짧거나 같은 거리를 데이터 프레임에 저장
other_group  = df_clean[df_clean['air_time'] >  cutoff]
#비행 시간이 47분보다 큰  거리 데이터 프레임에 저장

# 4) 평균 속도 비교 ───────────────────────────────────────────
overall_mean_speed = df_clean['speed_mpm'].mean()
#모든 항공편의 평균 속도가 얼마인지 구해서 
#overall_mean_speed에 저장

short_mean_speed   = short_group['speed_mpm'].mean()
# 비행시간이 아주 짧은 그룹의 평균 속도를 따로 구해서 
# short_mean_speed에 저장

df_clean = df_flights.dropna(subset=['air_time'])
# (336776->327346)

# 1. 비행시간 기준 하위 10% 커트라인 구하기
short_time_cutoff = df_clean['air_time'].quantile(0.1)
#비행시간이 가장 짧은 하위 10%구간이 47분 이내
# 데이터의 분위수(quantile)를 계산합니다. 
# 쉽게 말해 “위에서부터 몇 % 지점에 해당하는 값”을 구하는 함수예요.
# 0.1을 넣으면 하위 10퍼센트 값을 구할 수 있음.

# 2. 실제 비행시간이 짧았던 항공편 선별
short_flights = df_clean[df_clean['air_time'] <= short_time_cutoff]
# 아까 만들었던 short_time_cutoff를통해
# df_clean['air_time'] <= short_time_cutoff
# air_time(비행시간)이 47분인지를 True/False값으로 출력
# 그 결과 값을 새 데이터 프레임에 저장

print(f'전체 평균 속도    : {overall_mean_speed:.2f} mile/min')
print(f'짧은 그룹 평균 속도: {short_mean_speed:.2f} mile/min')

if short_mean_speed > overall_mean_speed:
    print('✅ 짧은 비행시간 그룹이 실제로 더 빠른 속도로 운항한 경향이 있습니다.')
else:
    print('❌ 짧은 그룹이 특별히 더 빠른 속도를 보이지 않습니다. 다른 요인을 더 살펴보세요.')

#시각화
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 한글 폰트 설정
import platform
import matplotlib.font_manager as fm

if platform.system() == 'Windows':
    font_list = ['Malgun Gothic', 'AppleGothic', 'Gulim', 'Dotum', 'NanumGothic']
    for font in font_list:
        try:
            plt.rcParams['font.family'] = font
            break
        except:
            continue
    else:
        plt.rcParams['font.family'] = 'DejaVu Sans'
elif platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

# 속도 계산 (시간당 마일)
df_clean_copy = df_clean.copy()
df_clean_copy['speed'] = df_clean_copy['distance'] / (df_clean_copy['air_time'] / 60)

short_flights_copy = short_flights.copy()
short_flights_copy['speed'] = short_flights_copy['distance'] / (short_flights_copy['air_time'] / 60)

# Speed Distribution Comparison 히스토그램 (실제 개수)
plt.figure(figsize=(10, 6))

plt.hist(df_clean_copy['speed'], bins=50, alpha=0.6, color='lightblue', 
         label='All Flights', density=False)
plt.hist(short_flights_copy['speed'], bins=30, alpha=0.8, color='red', 
         label='Short Flights', density=False)
plt.title('Speed Distribution Comparison', fontsize=14, fontweight='bold')
plt.xlabel('Speed (mph)')
plt.ylabel('Number of Flights')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 기본 통계 출력
avg_speed_all = df_clean_copy['speed'].mean()
avg_speed_short = short_flights_copy['speed'].mean()

print("="*50)
print("🚀 Speed Distribution Analysis")
print("="*50)
print(f"• Average speed (All flights): {avg_speed_all:.1f} mph")
print(f"• Average speed (Short flights): {avg_speed_short:.1f} mph")
print(f"• Speed difference: {avg_speed_short - avg_speed_all:.1f} mph")

# 평균 속도가 거의 동일 → 속도 차이로 인한 시간 단축 효과 없음
# 오히려 짧은 항공편들이 평균적으로 더 느리네
# 짧은 항공편은 순항시간이 짧아서 최고 속도를 충분히 활용하지 못한다.
#--------------------------------------------------------------
###3 비행기 지연 때문일 것이다?
df_flights = pd.read_csv(
    r"C:\Users\an100\OneDrive\바탕 화면\flights_data.csv",
    usecols=['distance', 'air_time', 'dep_delay', 'arr_delay']
    )
# 1) 결측치 제거 + 복사본 확보
df_clean = df_flights.dropna().copy()

# 2) 비행시간 하위 10 % 그룹 추출
cutoff = df_clean['air_time'].quantile(0.10)
short_grp = df_clean[df_clean['air_time'] <= cutoff]
other_grp = df_clean[df_clean['air_time'] >  cutoff]

# 3) 평균 지연 비교 (출발·도착)
for col in ['dep_delay', 'arr_delay']:
    all_avg   = df_clean[col].mean()
    short_avg = short_grp[col].mean()
    
    print(f'\n[{col}]')
    print(f'  전체 평균   : {all_avg:6.2f}  min')
    print(f'  짧은 그룹 평균 : {short_avg:6.2f}  min')
    if short_avg < all_avg:
        print('  ✅ 짧은 그룹 지연이 더 적음')
    else:
        print('  ❌ 지연 차이 명확하지 않음')

#짧은 그룹의 지연이 더 적더라
#결론 비행 이동시간이 짧을 것을 선호한다면
# 거리가 짧거나 지연이 짧은 것을 선택해야한다
# 00노선 top5
# 00항공사 top5
#  ----------------------------------------------
# 알고리즘
import pandas as pd

# ───────────── 0. CSV 불러오기 ───────────────────────────────
CSV_PATH = r"C:\Users\an100\OneDrive\바탕 화면\flights_data.csv"
usecols = ['origin','dest','carrier','distance','air_time',
           'dep_delay','arr_delay']
df = pd.read_csv(CSV_PATH, usecols=usecols).dropna()

# ───────────── 1. 노선별 평균 거리 + 지연 집계 ────────────────
route_dist = (
    df.groupby(['origin','dest'])['distance']
      .mean().reset_index(name='avg_distance')
)

# 각 항공사·노선별 평균 지연(출발+도착)
df['total_delay'] = df['dep_delay'] + df['arr_delay']
route_airline_delay = (
    df.groupby(['origin','dest','carrier'])['total_delay']
      .mean().reset_index(name='avg_delay')
)

# ───────────── 2. 짧은 노선 TOP‑K 선택 ─────────────────────
K = 15                # 노선 추천 개수
SHORT_THRESHOLD = 400 # “짧은 노선” 기준 (mile)

short_routes = (
    route_dist[route_dist['avg_distance'] <= SHORT_THRESHOLD]
    .sort_values('avg_distance')
    .head(K)
)

# ───────────── 3. 각 노선에 지연 최소 항공사 매칭 ───────────
merged = short_routes.merge(route_airline_delay,
                            on=['origin','dest'],
                            how='left')

# 노선별 지연이 가장 작은 항공사 1위만 선택
idx = merged.groupby(['origin','dest'])['avg_delay'].idxmin()
best_pairs = merged.loc[idx].reset_index(drop=True)

# ───────────── 4. 점수 및 최종 정렬 ─────────────────────────
# 거리/지연을 0~1 사이로 정규화 후 가중합
dist_norm = (best_pairs['avg_distance'] - best_pairs['avg_distance'].min()) \
          / (best_pairs['avg_distance'].max() - best_pairs['avg_distance'].min())
delay_norm = (best_pairs['avg_delay'] - best_pairs['avg_delay'].min()) \
           / (best_pairs['avg_delay'].max() - best_pairs['avg_delay'].min())

# 가중치 (거리 60 %, 지연 40 %)
best_pairs['score'] = 0.6 * (1 - dist_norm) + 0.4 * (1 - delay_norm)

final = best_pairs.sort_values('score', ascending=False)

# ───────────── 5. 결과 출력 ────────────────────────────────
print('\n🔝  추천 노선 + 항공사 (거리 짧고 지연 최저)')
print(final[['origin','dest','carrier','avg_distance','avg_delay','score']]
      .to_string(index=False, formatters={
          'avg_distance': '{:.0f}'.format,
          'avg_delay':    '{:.1f}'.format,
          'score':        '{:.2f}'.format
      }))



###########################################
############################################
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(12, 8))

# 전체 항공편: 회색 작은 점
plt.scatter(df_clean['distance'], df_clean['air_time'],
            color='lightgray', alpha=0.3, label='전체 항공편', s=10)

# 하위 10% 그룹: 빨간 큰 점
plt.scatter(short_flights['distance'], short_flights['air_time'],
            color='tomato', alpha=0.7, label='비행시간 하위 10%', s=30)

# 평균 거리 수직선
plt.axvline(overall_avg_distance, color='steelblue', linestyle='--',
            label=f'전체 평균 거리 ≈ {overall_avg_distance:.0f} mile')
plt.axvline(short_avg_distance, color='orange', linestyle='--',
            label=f'짧은 그룹 평균 거리 ≈ {short_avg_distance:.0f} mile')

# 제목과 축 라벨
plt.title('비행 거리 vs 비행 시간 (하위 10% 짧은 비행시간 강조)', fontsize=16)
plt.xlabel('거리 (mile)', fontsize=12)
plt.ylabel('비행 시간 (min)', fontsize=12)
plt.legend(loc='upper left', fontsize=10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

############################################
#############################################

import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 박스플롯
plt.figure(figsize=(10, 6))
sns.boxplot(data=[other_group['speed_mpm'], short_group['speed_mpm']],
            palette=['lightgray', 'tomato'])

plt.xticks([0, 1], ['전체 항공편 (90%)', '비행시간 하위 10%'], fontsize=11)
plt.ylabel('비행 속도 (mile/min)', fontsize=12)
plt.title('비행시간이 짧은 그룹은 실제로 더 빠르게 날았을까?', fontsize=14)

# 평균 속도 수평선
plt.axhline(overall_mean_speed, color='blue', linestyle='--',
            label=f'전체 평균 속도 ≈ {overall_mean_speed:.2f}')
plt.axhline(short_mean_speed, color='orange', linestyle='--',
            label=f'하위 10% 평균 속도 ≈ {short_mean_speed:.2f}')

plt.legend(loc='upper right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

##########################################################
##########################################################

import matplotlib.pyplot as plt
import seaborn as sns

# Seaborn 스타일 적용
sns.set(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 평균 속도 계산
short_mean_speed = short_group['speed_mpm'].mean()

# 시각화
plt.figure(figsize=(6, 6))
sns.boxplot(y=short_group['speed_mpm'], color='tomato')

# 타이틀 및 축 라벨
plt.title('비행시간 하위 10% 그룹의 비행 속도 분포', fontsize=14)
plt.ylabel('비행 속도 (mile/min)', fontsize=12)

# 평균 속도 선
plt.axhline(short_mean_speed, color='orange', linestyle='--',
            label=f'평균 속도 ≈ {short_mean_speed:.2f} mile/min')

plt.legend(loc='upper right')
plt.grid(axis='y', linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()

########################################################
import matplotlib.pyplot as plt
import seaborn as sns

# 스타일 적용
sns.set(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 산점도
plt.figure(figsize=(10, 6))
plt.scatter(
    short_group['air_time'],
    short_group['speed_mpm'],
    color='tomato', alpha=0.7, s=30
)

# 제목 및 축 라벨
plt.title('비행시간 하위 10% 그룹의 비행시간 vs 속도', fontsize=15)
plt.xlabel('비행시간 (min)', fontsize=12)
plt.ylabel('비행 속도 (mile/min)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()