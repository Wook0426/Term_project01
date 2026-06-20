import duckdb
import flet as ft

# ✅ read_only=False 명시, 잠금 충돌 방지
#con = duckdb.connect("data/tour_planner_term.db", read_only=False)
con = duckdb.connect()
# db연결은 항상 main밖에서 초회실행
# auto_increment 표현을 위한 시퀀스 생성
con.execute("CREATE SEQUENCE IF NOT EXISTS place_seq")
con.execute("CREATE SEQUENCE IF NOT EXISTS recommend_seq")
con.execute("CREATE SEQUENCE IF NOT EXISTS schedule_seq")
con.execute("CREATE SEQUENCE IF NOT EXISTS review_seq")
con.execute("CREATE SEQUENCE IF NOT EXISTS bookmark_seq")
con.execute("CREATE SEQUENCE IF NOT EXISTS tour_seq")

# 메모리 내부에 데이터베이스 만듦
    # 1. Users table
con.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id VARCHAR PRIMARY KEY,
        password VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        email VARCHAR 
        )
""")
# 2. Recommend table
con.execute("""
    CREATE TABLE IF NOT EXISTS Recommend (
        recommend_id BIGINT DEFAULT nextval('recommend_seq') PRIMARY KEY,
        theme VARCHAR NOT NULL
    )
""")
# 3. Tour table
con.execute("""
    CREATE TABLE IF NOT EXISTS Tour (
        tour_id BIGINT DEFAULT nextval('tour_seq') PRIMARY KEY,
        user_id VARCHAR NOT NULL,
        how_many INTEGER NOT NULL,
        tour_name VARCHAR,
                
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
""")
# 4. Schedule table
con.execute("""
    CREATE TABLE IF NOT EXISTS Schedule (
        schedule_id BIGINT DEFAULT nextval ('schedule_seq') PRIMARY KEY,
        tour_id BIGINT NOT NULL,
        visit_time VARCHAR NOT NULL,
        visit_date INTEGER NOT NULL,
                
        FOREIGN KEY (tour_id) REFERENCES Tour(tour_id)
    )
""")
# 6. Place table
con.execute("""
    CREATE TABLE IF NOT EXISTS Place (
        place_id BIGINT DEFAULT nextval('place_seq') PRIMARY KEY,
        schedule_id BIGINT NOT NULL,
        recommend_id BIGINT NOT NULL,
        place_name VARCHAR NOT NULL,
        place_address VARCHAR NOT NULL,
        place_description VARCHAR,
        image_url VARCHAR,
            
        FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id),
        FOREIGN KEY (recommend_id) REFERENCES Recommend(recommend_id)
    )
""")
# 6. Bookmark table
con.execute("""
    CREATE TABLE IF NOT EXISTS Bookmark (
        bookmark_id BIGINT DEFAULT nextval ('bookmark_seq') PRIMARY KEY,
        user_id VARCHAR NOT NULL,
        place_id BIGINT NOT NULL,
            
        FOREIGN KEY (user_id) REFERENCES Users(user_id),                                 
        FOREIGN KEY (place_id) REFERENCES Place(place_id)
    )
""")
# 7. Review table
con.execute("""
    CREATE TABLE IF NOT EXISTS  Review (
        review_id BIGINT DEFAULT nextval ('review_seq') PRIMARY KEY,
        user_id VARCHAR NOT NULL,
        place_id BIGINT NOT NULL,
        rating INTEGER,
        content VARCHAR NOT NULL,
                        
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (place_id) REFERENCES Place(place_id)
    )
""")
# 중복시 무시하고, 테이블마냥 읽어서 insert - fk 때문에 참조당하는 테이블 우선 데이터 삽입
con.execute("""         
     INSERT OR IGNORE INTO Users
     SELECT *FROM read_csv_auto('data/Users.csv') 
 """) 
con.execute("""
    INSERT OR IGNORE INTO Recommend VALUES
    (1, '산'),
    (2, '바다'),
    (3, '문화'),
    (4, '체험')
""")
con.execute("""
    INSERT OR IGNORE INTO Tour VALUES
    (1, 20230815, 20, '수학여행'),
    (2, 20231234, 1, '혼행')
""")
con.execute("""
    INSERT OR IGNORE INTO Schedule VALUES
    (1, 1, '12:30', 20260612),
    (2, 2, '15:46', 200260613)
""")
con.execute("""         
     INSERT OR IGNORE INTO Place
     SELECT *FROM read_csv_auto('data/Place.csv') 
 """)
con.execute("""
    INSERT OR IGNORE INTO Bookmark VALUES
    (1, 20230815, 1)
""")
# main 밖에는 db 접근로직 - 초회한정
def main(page: ft.Page):
    # main 아래는 일반 로직 - 호출시마다

    # 규격/표준: SQL 사용, 테이블 3개 이상 사용, Join 연산 사용
     
    # 1. 사용자가 후기를 남긴 장소 조회 : User -> Review -> Place
    def on_click_reviewingPlace(e):
        review_place = e.control.text
        # e는 이벤트 객체 - 버튼 클릭시 flet이 정보를 넘겨줌
        # control.text - 버튼과 버튼 이름
        df = con.execute("""
            SELECT u.name, p.place_name, r.content
            FROM Users u
            JOIN Review r ON u.user_id = r.user_id
            JOIN Place p ON r.place_id = p.place_id
            WHERE p.place_name = ? 
        """, [review_place]).df()

        # ?는 자리표시자 - 옆에 있는 []값이 들어감 - sql injection 방어
        page.update()
        print(df)
    # 2. 사용자가 즐겨찾기 한 장소 조회 : User -> Bookmark -> Place
    def on_click_bookmarkingPlace(e):
        bookmark_place = e.control.text

        df = con.execute("""
            SELECT u.name, p.place_name, b.bookmark_id
            FROM Users u
            JOIN Bookmark b ON u.user_id = b.user_id
            JOIN Place p ON b.place_id = p.place_id
            WHERE p.place_name = ?
        """, [bookmark_place]).df()
        page.update()
        print(df)

    # 3. 여행일정 전체 조회 : User -> Tour -> Schedule -> Place
    def on_click_viewAlltour(e):
        view_all = e.control.text

        df = con.execute("""
            SELECT u.name, t.tour_name, s.visit_date, p.place_name
            FROM Users u
            JOIN Tour t ON u.user_id = t.user_id
            JOIN Schedule s ON t.tour_id = s.tour_id
            JOIN Place p ON s.schedule_id = p.schedule_id
            WHERE u.user_id = ?
        """, [view_all]).df()
        page.update()
        print(df)   

    #첫 번째 UI 화면 : 테마 선택
    
    print("1. main 진입")
    page.title = "나의 여행플래너"
    page.padding = 16
    page.window.width = 600
    page.window.height = 500
    page.horizontal_alignment=ft.CrossAxisAlignment.CENTER   #위아래 기준 가운데
    
    def home_screen(): #홈 화면
        page.clean()                                        # 화면 비우기

        def on_theme_click(e):
            selected_theme = e.control.data                # 클릭한 버튼의 text가져옴
            place_list(selected_theme)                     # 선택된 테마를 넣어 화면 전환

    # 화면에 요소 추가
        page.add(   # 새 컨트롤 추가
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.ElevatedButton("산", on_click=on_theme_click, data="산"),  # 텍스트를 표시가능한 버튼
                ft.ElevatedButton("바다", on_click=on_theme_click, data="바다"),
                ft.ElevatedButton("문화", on_click=on_theme_click, data="문화"),
                ft.ElevatedButton("체험", on_click=on_theme_click, data="체험"),
            ]
        )
    )
    #테마에 의한 관광지 목록을 보여주는 화면 : (Recommend-Place)사용
    def place_list(theme: str):
        page.clean()
        df = con.execute("""
            SELECT p.place_id,
                   p.place_name,
                   p.place_address,
                   p.place_description,
                   p.image_url
            FROM   Recommend r
            JOIN   Place     p ON r.recommend_id = p.recommend_id
            WHERE  r.theme = ?
        """, [theme]).df()   

        place_cards = []
        for _, row in df.iterrows():
            place_id = row['place_id']
            name = row['place_name']
            address = row['place_address']
            description = row['place_description']
            img_url = row['image_url']

            if img_url:
                image_check = ft.Image(  #이미지 url이 있을 때만 표시
                    src=img_url,
                    width = 200,
                    height = 150,
                    fit=ft.BoxFit.COVER,  #이미지를 박스크기에 맞게 채우고 남는 부분은 자르기
                )
            else:          # 이미지가 안넘어오면
                image_check = ft.Container(  
                    content=ft.Text("이미지  없음")
                )

            card = ft.Card(             #카드 형태로 만듦
                content=ft.Container(   #내부 요소배치
                    padding=10,         #안쪽 여백은 10
                    content=ft.Row(     #내용(content) = 행(row) : 행의 내용
                        controls=[      #내부요소
                            image_check,
                            ft.Container(width=10), #간격은 10
                            ft.Column(              #열
                                expand=True,        #부모와 크기맞춤
                                controls=[          #내부요소
                                    ft.Text(name, size=15, weight=ft.FontWeight.BOLD), #제목은 굵은글씨
                                    ft.Text(address, size=12, color=ft.Colors.GREY_700), #주소는 회색글씨
                                    ft.Text(description or "", size=8),
                                    ft.ElevatedButton(                                   #각 관광지 카드들마다 일정추가 버튼 생성
                                        "일정에 추가",
                                        data={"place_id": place_id, "place_name": name},
                                        on_click=on_select_place                        # 일정추가 시도시 이 함수가 발동함
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
            place_cards.append(card)    #카드를 추가
        page.add(
            ft.Column(
                scroll=ft.ScrollMode.AUTO,  #카드가 많아도 스크롤 가능하다.
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: home_screen()), #기본 사용시 입실행 즉시 실행되므로 가상함수로 선언하여 클릭시 - 반환값이 아닌 함수자체를 받게한다.
                        # arrow_back은 뒤로가기 아이콘
                        ft.Text(f"[{theme}]")
                    ]),
                    ft.Divider(),
                    *place_cards, # 카드화 된 관광지를 controls가 인식하도록 리스트로 언패킹하는 연산자
                ]
            )
        )
    def on_select_place(e):
        place_id = e.control.data["place_id"] #place_id를 control의 요소화 객체로 만듦
        place_name = e.control.data["place_name"] # "
        show_schedule_input(place_id, place_name) # 이 두개를 show_schedule_input의 매개변수로 넘김

    def show_schedule_input(place_id: int, place_name: str): # 일정 입력사항 입력 화면
        page.clean()

        date_field = ft.TextField(label="방문 날짜 (ex: 20260620)", width = 200)
        time_field = ft.TextField(label="방문 시간 (ex: 12:33)", width=150)

        def on_next(e): # 날짜/시간 입력 후 여행생성
            if not date_field.value or not time_field.value: # 입력검증
                # snack_bar 사용
                snack_bar = ft.SnackBar(content=ft.Text("날짜와 시간을 입력해주세요."))
                page.overlay.append(snack_bar)
                snack_bar.open=True
                page.update()
                return 
            show_tour_input(place_id, place_name, visit_date=int(date_field.value), visit_time=time_field.value)

        page.add(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(controls=[
                        ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: place_list("")),
                        ft.Text("일정 입력", size=15, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Divider(),
                    ft.Text(f"관광지 : {place_name}", size=10),
                    ft.Container(height=8),
                    date_field,
                    time_field,
                    ft.Container(height=12),
                    ft.ElevatedButton("다음", on_click=on_next, width=150),
                ]
            )
        )
    
    def show_tour_input(place_id: int, place_name: str, visit_date:int, visit_time: str):
        # 여행정보 기입 후 전체 정보 db저장
        page.clean()

        tour_name_field = ft.TextField(label="여행 이름",     width=280)
        how_many_field  = ft.TextField(label="인원 수",       width=280)
        user_id_field   = ft.TextField(label="사용자 ID",     width=280)

        def on_save(e):
            user_id = user_id_field.value
            tour_name = tour_name_field.value
            how_many = int(how_many_field.value)

            #sql injection방어 - 입력값 3개를 ?로 받고, 문자열로만 처리
            con.execute("""
                INSERT OR IGNORE INTO Tour (user_id, how_many, tour_name)
                VALUES (?, ?, ?)
            """, [user_id, how_many, tour_name])

            tour_id = int (con.execute(     #duckdb에서 인식할 수 있는 python int 값으로 꺼냄
                "SELECT currval('tour_seq')"
            ).df().iloc[0, 0])   # 2차원 배열로 저장된 dataframe에서 값 꺼내기

            con.execute("""
                INSERT OR IGNORE INTO Schedule (tour_id, visit_time, visit_date)
                VALUES (?, ?, ?)
            """, [tour_id, visit_time, visit_date])

            schedule_id = int (con.execute(
                "SELECT currval('schedule_seq')"
            ).df().iloc[0, 0])   # (0,0) 값 꺼내기

            complete_screen(tour_name, place_name, schedule_id) # 완료 화면

        page.add(
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK,
                                          on_click=lambda e: complete_screen()),
                            ft.Text("여행 정보 입력", size=20, weight=ft.FontWeight.BOLD)
                        ]),
                        ft.Divider(),
                        ft.Text(f"관광지 : {place_name} | 방문 : {visit_date} {visit_time}", size=12),
                        ft.Container(height=10),
                        user_id_field,
                        tour_name_field,
                        how_many_field,
                        ft.Container(height=12),
                        ft.ElevatedButton("저장", on_click=on_save, width=150),
                    ]
                )
            )
    def complete_screen(tour_name: str, place_name: str, schedule_id: int):
        #일정 저장 완료 및 홈버튼
        page.clean()
        page.add(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN),
                    ft.Text("일정이 저장되었습니다!", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    ft.Text(f"여행: {tour_name}", size=14),
                    ft.Text(f"관광지: {place_name}", size=14),
                    ft.Text(f"Schedule ID: {schedule_id}", size=12,
                            color=ft.Colors.GREY_600),
                    ft.Container(height=24),
                    ft.ElevatedButton("처음으로", on_click=lambda e: home_screen(), width=150),
                ]
            )
        )
    home_screen()
ft.run(main)