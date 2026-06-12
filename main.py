import duckdb
import flet as ft
#import os

# # ---------------------------------------------------------
# # [PART 1 기반] DB 연결 및 테이블 생성 (DDL)
# # ---------------------------------------------------------
# con = duckdb.connect("travel_planner.db")

# # 1. 테이블 3개 생성 (교수님 필수 조건 1)
# con.execute("""
#     CREATE TABLE IF NOT EXISTS Place (
#         place_id BIGINT PRIMARY KEY,
#         place_name VARCHAR,
#         place_address VARCHAR,
#         place_image VARCHAR, -- 이미지 경로를 저장할 컬럼
#         theme VARCHAR,
#         city VARCHAR
#     )
# """)

# con.execute("""
#     CREATE TABLE IF NOT EXISTS Tour (
#         tour_id BIGINT PRIMARY KEY,
#         tour_name VARCHAR,
#         user_id BIGINT
#     )
# """)

# con.execute("""
#     CREATE TABLE IF NOT EXISTS Schedule (
#         schedule_id BIGINT PRIMARY KEY,
#         tour_id BIGINT,
#         place_id BIGINT,
#         visit_time VARCHAR,
#         date VARCHAR
#     )
# """)

# # 테스트용 샘플 데이터 삽입 (기본값 대신 DML로 삽입)
# con.execute("INSERT OR IGNORE INTO Place VALUES (1, '금오산', '경북 구미시 금오산길', 'assets/geumosan.jpg', '자연', '구미')")
# con.execute("INSERT OR IGNORE INTO Place VALUES (2, '낙동강 체육공원', '경북 구미시 낙동강변로', 'assets/park.jpg', '액티비티', '구미')")
# con.execute("INSERT OR IGNORE INTO Tour VALUES (101, '대학생 구미 답사여행', 20230815)")
# con.execute("INSERT OR IGNORE INTO Schedule VALUES (1, 101, 1, '14:35', '2026-05-23')")
# con.execute("INSERT OR IGNORE INTO Schedule VALUES (2, 101, 2, '16:00', '2026-05-23')")


# # ---------------------------------------------------------
# # [PART 2 & 5 기반] Flet GUI 및 비즈니스 로직
# # ---------------------------------------------------------
# def main(page: ft.Page):
#     page.title = "나만의 여행 플래너"
#     page.window_width = 800
#     page.window_height = 700
    
#     # 결과가 표시될 컨테이너들
#     recommend_area = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
#     join_table_area = ft.Column()

#     # --- 기능 1: [PART 5 기반] 테마별 관광지 검색 및 이미지 출력 ---
#     def on_search_click(e):
#         theme_keyword = theme_input.value
        
#         # [PART 6 기반] Parameter Binding으로 안전하게 검색
#         query = "SELECT * FROM Place WHERE theme ILIKE ?"
#         df = con.execute(query, [f"%{theme_keyword}%"]).df()
        
#         # 화면 갱신을 위해 이전 결과 클리어
#         recommend_area.controls.clear()
        
#         # [PART 3 기반] iterrows()로 데이터 동적 추가 + 이미지 출력 (교수님 필수 조건 4)
#         for _, row in df.iterrows():
#             recommend_area.controls.append(
#                 ft.Container(
#                     content=ft.Row([
#                         # 실제 프로젝트 폴더 내 assets/이미지파일명.jpg 형태로 준비해야 합니다.
#                         # 만약 이미지가 없다면 익숙한 아이콘으로 대체되도록 error 스크립트 지정 가능
#                         ft.Image(src=row['place_image'], width=100, height=100, fit=ft.ImageFit.COVER),
#                         ft.Column([
#                             ft.Text(row['place_name'], size=18, weight=ft.FontWeight.BOLD),
#                             ft.Text(f"주소: {row['place_address']}"),
#                             ft.Text(f"분류: {row['city']} | {row['theme']}", color=ft.Colors.BLUE_GREY),
#                         ], expand=True)
#                     ]),
#                     padding=10,
#                     border=ft.border.all(1, ft.Colors.GREY_300),
#                     border_radius=8
#                 )
#             )
#         page.update() # [PART 2 기반] 화면 갱신 필수!

#     # --- 기능 2: 3개 테이블 JOIN 조회 기능 (교수님 필수 조건 2) ---
#     def on_show_schedule_click(e):
#         # Tour, Schedule, Place 3개 테이블 JOIN 쿼리
#         join_query = """
#             SELECT t.tour_name, s.date, s.visit_time, p.place_name, p.place_address
#             FROM Schedule s
#             JOIN Tour t ON s.tour_id = t.tour_id
#             JOIN Place p ON s.place_id = p.place_id
#             ORDER BY s.date, s.visit_time
#         """
#         df_join = con.execute(join_query).df()
        
#         join_table_area.controls.clear()
        
#         # [PART 3 방식 ② 기반] DataTable 자동 생성
#         dt = ft.DataTable(
#             columns=[ft.DataColumn(ft.Text(col.upper())) for col in df_join.columns],
#             rows=[
#                 ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for val in row])
#                 for row in df_join.values
#             ]
#         )
#         join_table_area.controls.append(dt)
#         page.update()

#     # --- UI 레이아웃 배치 ---
#     theme_input = ft.TextField(label="추천받고 싶은 테마 입력 (예: 자연, 액티비티)", expand=True)
#     search_button = ft.ElevatedButton("관광지 추천받기", on_click=on_search_click)
#     schedule_button = ft.FilledButton("내 전체 여행 일정 확인 (3개 테이블 JOIN)", on_click=on_show_schedule_click)

#     # [PART 2 기반] 레이아웃 주축/교차축 구성 및 최종 add
#     page.add(
#         ft.Text("📍 맞춤형 관광지 추천 기능", size=22, weight=ft.FontWeight.BOLD),
#         ft.Row([theme_input, search_button]),
#         ft.Container(content=recommend_area, height=250, border=ft.border.all(1, ft.Colors.BLUE_200), padding=10),
#         ft.Divider(),
#         ft.Text("📅 나의 통합 스케줄러", size=22, weight=ft.FontWeight.BOLD),
#         schedule_button,
#         ft.Container(content=join_table_area, padding=10)
#     )

# ft.run(main)
# ctrl + / = 전체 주석 처리


# main 위에는 db 접근로직
def main(page: ft.Page):
    con = duckdb.connect()
    # 내부에 데이터베이스 만듦
    con.execute("""         
        CREATE TABLE IF NOT EXISTS Users 
        AS SELECT * FROM read_csv_auto('data/Users.csv')
    """)

    df = con.execute("SELECT *FROM Users").df()
    # main 아래는 일반 로직
    # data_table = 사용자에게 보여지는 db
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text(col.upper()))
            for col in df.columns
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(val))) for cal in row])
            for row in df.values
        ],
    )
ft.run(main)