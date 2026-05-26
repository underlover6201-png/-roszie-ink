"""
開發用假資料（執行一次即可）
用法：py scripts/seed_data.py
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.artist import Artist, Style
from app.models.course import Course, CourseStatus
from app.models.flash import FlashDesign
from app.models.setting import Setting
from app.models.work import WorkCategory


def seed():
    app = create_app("development")
    with app.app_context():
        db.create_all()

        # ── 風格標籤 ──────────────────────────────────────
        styles_data = [
            ("黑灰寫實", "blackgray-realism"),
            ("傳統美式", "traditional"),
            ("幾何線條", "geometric"),
            ("日式和風", "japanese"),
            ("水彩風格", "watercolor"),
            ("極簡線條", "fineline"),
            ("新傳統", "neo-traditional"),
            ("暗黑哥德", "dark-gothic"),
            ("小清新", "minimalist"),
            ("彩色卡通", "illustrative"),
        ]
        styles = {}
        for name, slug in styles_data:
            s = Style.query.filter_by(slug=slug).first()
            if not s:
                s = Style(name=name, slug=slug)
                db.session.add(s)
            styles[slug] = s

        # ── 作品分類 ──────────────────────────────────────
        cats_data = [
            ("手臂", "arm"), ("腿部", "leg"), ("背部", "back"),
            ("胸口", "chest"), ("手腕", "wrist"), ("腳踝", "ankle"),
        ]
        for name, slug in cats_data:
            if not WorkCategory.query.filter_by(slug=slug).first():
                db.session.add(WorkCategory(name=name, slug=slug))

        db.session.flush()

        # ── 10 位刺青師傅 ─────────────────────────────────
        artists_data = [
            {
                "name": "Roszie",
                "slug": "roszie",
                "bio": "工作室創辦人，擅長黑灰寫實與幾何線條。作品以細膩的光影層次和乾淨的構圖著稱，曾受邀參加台北、東京刺青展。",
                "instagram_url": "https://www.instagram.com/roszie.ink/",
                "sort_order": 1,
                "style_slugs": ["blackgray-realism", "geometric"],
            },
            {
                "name": "Kai Chen",
                "slug": "kai-chen",
                "bio": "擅長傳統美式與新傳統風格，色彩飽和、線條粗獷有力。熱愛老派圖騰與現代詮釋的結合。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 2,
                "style_slugs": ["traditional", "neo-traditional"],
            },
            {
                "name": "Mika Hsu",
                "slug": "mika-hsu",
                "bio": "水彩風格專家，作品宛如畫布上的流動色彩。擅長花卉、動物、夢幻場景，深受女性顧客喜愛。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 3,
                "style_slugs": ["watercolor", "minimalist"],
            },
            {
                "name": "Jin Wu",
                "slug": "jin-wu",
                "bio": "日式和風的忠實傳承者，擅長傳統日式神獸、浮世繪圖騰，作品充滿故事性與文化底蘊。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 4,
                "style_slugs": ["japanese"],
            },
            {
                "name": "Sora Lin",
                "slug": "sora-lin",
                "bio": "極簡線條美學的代表，用最少的線條說最多的故事。善用負空間，作品簡潔而有力量。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 5,
                "style_slugs": ["fineline", "minimalist"],
            },
            {
                "name": "Rex Huang",
                "slug": "rex-huang",
                "bio": "暗黑哥德美學愛好者，作品充滿神秘氛圍與戲劇張力。擅長骷髏、玫瑰、暗黑人物肖像。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 6,
                "style_slugs": ["dark-gothic", "blackgray-realism"],
            },
            {
                "name": "Amy Cheng",
                "slug": "amy-cheng",
                "bio": "插畫風格刺青師，把日本動漫與台灣在地文化融合成獨特的彩色插畫刺青，充滿童趣與創意。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 7,
                "style_slugs": ["illustrative"],
            },
            {
                "name": "Tomo Saito",
                "slug": "tomo-saito",
                "bio": "來自大阪的刺青師，帶著正統日式技法落腳台北。融合現代審美與傳統工藝，每件作品都是限定創作。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 8,
                "style_slugs": ["japanese", "neo-traditional"],
            },
            {
                "name": "Luna Tsai",
                "slug": "luna-tsai",
                "bio": "幾何數學美學愛好者，以圓、三角、對稱圖形構建精密的視覺秩序。作品乾淨、準確、充滿數理美感。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 9,
                "style_slugs": ["geometric", "fineline"],
            },
            {
                "name": "Owen Ko",
                "slug": "owen-ko",
                "bio": "黑灰寫實肖像專家，能將照片重現於皮膚之上。人物、動物、建築皆是拿手題材，細節精確令人驚豔。",
                "instagram_url": "https://www.instagram.com/",
                "sort_order": 10,
                "style_slugs": ["blackgray-realism"],
            },
        ]

        artist_objs = {}
        for a in artists_data:
            obj = Artist.query.filter_by(slug=a["slug"]).first()
            if not obj:
                obj = Artist(
                    name=a["name"],
                    slug=a["slug"],
                    bio=a["bio"],
                    instagram_url=a.get("instagram_url"),
                    is_active=True,
                    sort_order=a["sort_order"],
                )
                for sslug in a.get("style_slugs", []):
                    if sslug in styles:
                        obj.styles.append(styles[sslug])
                db.session.add(obj)
            artist_objs[a["slug"]] = obj

        db.session.flush()

        # ── 認領圖商城（Flash Designs） ────────────────────
        flash_data = [
            {
                "artist_slug": "roszie",
                "title": "蛇與玫瑰",
                "slug": "snake-and-rose",
                "description": "盤繞在玫瑰上的細長蛇，黑灰寫實風格，細節豐富，適合手臂或大腿外側。",
                "image_url": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600",
                "price": 8000,
                "placement": "手臂、大腿",
                "size_note": "約 12×15 cm",
                "style_slugs": ["blackgray-realism"],
            },
            {
                "artist_slug": "roszie",
                "title": "幾何狼頭",
                "slug": "geometric-wolf",
                "description": "以幾何線條構成的狼頭側臉，精密對稱，適合胸口或肩胛。",
                "image_url": "https://images.unsplash.com/photo-1567225557594-88d73398014a?w=600",
                "price": 6500,
                "placement": "胸口、肩胛",
                "size_note": "約 10×10 cm",
                "style_slugs": ["geometric"],
            },
            {
                "artist_slug": "kai-chen",
                "title": "傳統美式老虎",
                "slug": "traditional-tiger",
                "description": "飽和色彩的傳統美式老虎，粗獷線條勾勒出霸氣神態，適合手臂或腿部。",
                "image_url": "https://images.unsplash.com/photo-1562088287-bde35a1ea917?w=600",
                "price": 9000,
                "placement": "手臂、腿部",
                "size_note": "約 15×18 cm",
                "style_slugs": ["traditional"],
            },
            {
                "artist_slug": "mika-hsu",
                "title": "水彩牡丹",
                "slug": "watercolor-peony",
                "description": "流動的水彩暈染配上精細的牡丹花瓣，色彩夢幻浪漫，適合肩膀或大腿。",
                "image_url": "https://images.unsplash.com/photo-1588392382834-a891154bca4d?w=600",
                "price": 7500,
                "placement": "肩膀、大腿",
                "size_note": "約 12×12 cm",
                "style_slugs": ["watercolor"],
            },
            {
                "artist_slug": "jin-wu",
                "title": "日式錦鯉",
                "slug": "japanese-koi",
                "description": "傳統日式錦鯉搭配浪花與牡丹，充滿祥瑞寓意，適合背部或腿部大面積施作。",
                "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600",
                "price": 15000,
                "placement": "背部、腿部",
                "size_note": "約 20×30 cm",
                "style_slugs": ["japanese"],
            },
            {
                "artist_slug": "sora-lin",
                "title": "極簡山脈",
                "slug": "minimal-mountain",
                "description": "一筆勾勒的山脈輪廓，乾淨俐落，帶著登山者的靈魂。適合手腕或腳踝。",
                "image_url": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=600",
                "price": 3000,
                "placement": "手腕、腳踝",
                "size_note": "約 5×3 cm",
                "style_slugs": ["fineline", "minimalist"],
            },
            {
                "artist_slug": "rex-huang",
                "title": "哥德玫瑰骷髏",
                "slug": "gothic-skull-rose",
                "description": "骷髏與黑玫瑰的暗黑組合，充滿戲劇性張力，適合胸口或上臂。",
                "image_url": "https://images.unsplash.com/photo-1596178060810-72f53ce9a65c?w=600",
                "price": 8500,
                "placement": "胸口、上臂",
                "size_note": "約 10×14 cm",
                "style_slugs": ["dark-gothic"],
            },
            {
                "artist_slug": "luna-tsai",
                "title": "神聖幾何曼陀羅",
                "slug": "sacred-geometry-mandala",
                "description": "以尺規精密繪製的曼陀羅幾何圖案，每個節點都對稱完美，適合背部或胸口中央。",
                "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600",
                "price": 10000,
                "placement": "背部中央、胸口",
                "size_note": "約 15×15 cm",
                "style_slugs": ["geometric"],
            },
            {
                "artist_slug": "amy-cheng",
                "title": "貓耳少女",
                "slug": "cat-girl-illus",
                "description": "Q版插畫風格的貓耳少女，色彩繽紛可愛，適合手臂或腳踝。",
                "image_url": "https://images.unsplash.com/photo-1574169208507-84376144848b?w=600",
                "price": 5000,
                "placement": "手臂、腳踝",
                "size_note": "約 6×8 cm",
                "style_slugs": ["illustrative"],
            },
            {
                "artist_slug": "owen-ko",
                "title": "寫實老虎肖像",
                "slug": "realism-tiger-portrait",
                "description": "超寫實老虎眼神特寫，毛髮根根分明，彷彿呼之欲出。適合大腿或背部。",
                "image_url": "https://images.unsplash.com/photo-1561037404-61cd46aa615b?w=600",
                "price": 18000,
                "placement": "大腿、背部",
                "size_note": "約 18×22 cm",
                "style_slugs": ["blackgray-realism"],
            },
            {
                "artist_slug": "tomo-saito",
                "title": "浮世繪富士山",
                "slug": "ukiyo-e-fuji",
                "description": "以浮世繪技法重現葛飾北齋的富士山神韻，融入現代刺青審美，限量一份。",
                "image_url": "https://images.unsplash.com/photo-1480796927426-f609979314bd?w=600",
                "price": 12000,
                "placement": "背部、腿部",
                "size_note": "約 16×20 cm",
                "style_slugs": ["japanese"],
            },
            {
                "artist_slug": "sora-lin",
                "title": "貓咪細線",
                "slug": "fineline-cat",
                "description": "極簡線條勾勒的蜷縮貓咪，一筆流暢，生動可愛，適合手腕或耳後。",
                "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600",
                "price": 2500,
                "placement": "手腕、耳後",
                "size_note": "約 4×4 cm",
                "style_slugs": ["fineline"],
            },
        ]

        for fd in flash_data:
            if not FlashDesign.query.filter_by(slug=fd["slug"]).first():
                artist = artist_objs.get(fd["artist_slug"])
                if not artist:
                    continue
                design = FlashDesign(
                    artist_id=artist.id,
                    title=fd["title"],
                    slug=fd["slug"],
                    description=fd["description"],
                    image_url=fd["image_url"],
                    thumb_url=fd["image_url"],
                    price=fd["price"],
                    placement=fd.get("placement"),
                    size_note=fd.get("size_note"),
                    is_published=True,
                    is_claimed=False,
                )
                for sslug in fd.get("style_slugs", []):
                    if sslug in styles:
                        design.styles.append(styles[sslug])
                db.session.add(design)

        db.session.flush()

        # ── 課程 ──────────────────────────────────────────
        today = date.today()
        courses_data = [
            {
                "instructor_slug": "roszie",
                "title": "刺青入門工作坊",
                "slug": "tattoo-beginner-workshop",
                "description": "專為零基礎學員設計的一日體驗課。從器材認識、線條練習到實際施作（假皮），完整體驗刺青的世界。",
                "content": """## 課程大綱

### 上午（3小時）
- 刺青機器認識與保養
- 針頭種類與墨水選用
- 衛生安全觀念
- 線條基礎練習（假皮）

### 下午（3小時）
- 填色技法入門
- 圖案設計與轉印
- 完成第一件作品（假皮）
- Q&A 與個別指導

## 學員需自備
無需自備任何器材，材料費已含於學費。

## 適合對象
對刺青有興趣的零基礎學員。""",
                "price": 4800,
                "max_students": 4,
                "start_date": today + timedelta(days=14),
                "end_date": today + timedelta(days=14),
                "location": "ROSZIE INK 工作室，台北市大安區",
                "status": CourseStatus.open,
            },
            {
                "instructor_slug": "roszie",
                "title": "黑灰寫實進階班",
                "slug": "blackgray-realism-advanced",
                "description": "針對有基礎刺青技術的學員，深入學習黑灰寫實的光影層次、霧化技法與皮膚呈現。",
                "content": """## 課程大綱

### 第一天
- 寫實刺青的光影理論
- 針壓控制與深度調整
- 漸層霧化專項練習

### 第二天
- 參考照片分析與構圖
- 在假皮上完成寫實作品
- 導師批評與個別指導

## 先修條件
需有至少 6 個月刺青實操經驗。""",
                "price": 12000,
                "max_students": 3,
                "start_date": today + timedelta(days=21),
                "end_date": today + timedelta(days=22),
                "location": "ROSZIE INK 工作室，台北市大安區",
                "status": CourseStatus.open,
            },
            {
                "instructor_slug": "jin-wu",
                "title": "日式和風刺青系統班",
                "slug": "japanese-tattoo-system",
                "description": "由來自大阪的 Tomo 聯合 Jin 開設，系統性學習日式刺青的傳統圖騰、配色規則與構圖美學。",
                "content": """## 課程大綱

### 理論模組（2小時）
- 日式刺青歷史與圖騰意涵
- 傳統配色規則
- 構圖佈局美學

### 實作模組（6小時）
- 日式圖騰臨摹與變化
- 手毛彫（Tebori）基礎示範
- 個人創作習作

## 課程特色
含親筆簽名結業証書。""",
                "price": 18000,
                "max_students": 5,
                "start_date": today + timedelta(days=35),
                "end_date": today + timedelta(days=36),
                "location": "ROSZIE INK 工作室，台北市大安區",
                "status": CourseStatus.open,
            },
            {
                "instructor_slug": "sora-lin",
                "title": "極簡線條美學課",
                "slug": "fineline-minimalist-course",
                "description": "Sora 的招牌課程，教你用最少的線條傳遞最強的視覺衝擊。適合想學習細線風格的刺青師。",
                "content": """## 課程內容

- 細針使用技巧（0.35mm 以下）
- 線條張力與間距美學
- 負空間運用
- 從草圖到成品的完整流程

一天密集課，含材料費。""",
                "price": 6800,
                "max_students": 4,
                "start_date": today + timedelta(days=28),
                "end_date": today + timedelta(days=28),
                "location": "ROSZIE INK 工作室，台北市大安區",
                "status": CourseStatus.open,
            },
            {
                "instructor_slug": "roszie",
                "title": "創業預備班：開設個人工作室",
                "slug": "studio-setup-business",
                "description": "為想自己創業的刺青師量身打造。從法規申請、設備採購、定價策略到 IG 經營，手把手帶你建立自己的品牌。",
                "content": """## 課程模組

### 法規與執照
- 衛生局規範與申請流程
- 消費者保護注意事項

### 空間與設備
- 工作室選址與裝潢建議
- 設備採購清單與預算規劃

### 品牌與行銷
- 作品集拍攝技巧
- IG 演算法與貼文策略
- 定價心理學與套餐設計

### 客戶關係
- 諮詢流程標準化
- 售後追蹤與口碑建立

共 8 小時，分兩個半天上課。""",
                "price": 9800,
                "max_students": 8,
                "start_date": today + timedelta(days=42),
                "end_date": today + timedelta(days=43),
                "location": "ROSZIE INK 工作室，台北市大安區",
                "status": CourseStatus.open,
            },
        ]

        for c in courses_data:
            if not Course.query.filter_by(slug=c["slug"]).first():
                instructor = artist_objs.get(c["instructor_slug"])
                course = Course(
                    instructor_id=instructor.id if instructor else None,
                    title=c["title"],
                    slug=c["slug"],
                    description=c["description"],
                    content=c.get("content"),
                    price=c["price"],
                    currency="TWD",
                    max_students=c.get("max_students"),
                    start_date=c.get("start_date"),
                    end_date=c.get("end_date"),
                    location=c.get("location"),
                    status=c["status"],
                )
                db.session.add(course)

        # ── 基本設定 ──────────────────────────────────────
        Setting.set("site_name", "ROSZIE INK", "網站名稱")
        Setting.set("site_tagline", "Make it permanent.", "標語")
        Setting.set("studio_address", "台北市大安區忠孝東路四段", "地址")
        Setting.set(
            "business_hours",
            {
                "tuesday":   {"open": True,  "from": "13:00", "to": "21:00"},
                "wednesday": {"open": True,  "from": "13:00", "to": "21:00"},
                "thursday":  {"open": True,  "from": "13:00", "to": "21:00"},
                "friday":    {"open": True,  "from": "13:00", "to": "21:00"},
                "saturday":  {"open": True,  "from": "12:00", "to": "20:00"},
                "sunday":    {"open": False},
                "monday":    {"open": False},
            },
            "營業時間",
        )

        db.session.commit()
        print("✓ 假資料建立完成：10 位師傅、12 件認領圖、5 門課程")


if __name__ == "__main__":
    seed()
