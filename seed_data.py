import requests

BASE = "http://localhost"
AUTH_URL = f"{BASE}:8012/auth"
BOOK_URL = f"{BASE}:8002/books"

def seed():
    # ─── 1. TẠO USERS ───────────────────────────────────────────
    print("📝 Tạo users...")
    users = [
        {"username": "admin",     "email": "admin@bookstore.com",     "password": "admin123",  "role": "manager"},
        {"username": "staff1",    "email": "staff1@bookstore.com",    "password": "staff123",  "role": "staff"},
        {"username": "staff2",    "email": "staff2@bookstore.com",    "password": "staff123",  "role": "staff"},
        {"username": "customer1", "email": "customer1@bookstore.com", "password": "pass123",   "role": "customer"},
        {"username": "customer2", "email": "customer2@bookstore.com", "password": "pass123",   "role": "customer"},
        {"username": "customer3", "email": "customer3@bookstore.com", "password": "pass123",   "role": "customer"},
    ]
    for u in users:
        r = requests.post(f"{AUTH_URL}/register/", json=u)
        if r.status_code == 201:
            print(f"  ✅ Created: {u['username']} ({u['role']})")
        else:
            print(f"  ⚠️  Skip: {u['username']} — {r.text[:60]}")

    # ─── 2. LẤY TOKEN STAFF ─────────────────────────────────────
    print("\n🔑 Lấy token staff...")
    r = requests.post(f"{AUTH_URL}/login/", json={"username": "staff1", "password": "staff123"})
    if r.status_code != 200:
        print(f"  ❌ Login thất bại: {r.text}")
        return
    token = r.json().get("token") or r.json().get("access")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  ✅ Token OK")

    # ─── 3. TẠO CATEGORIES ──────────────────────────────────────
    print("\n📂 Tạo categories...")
    category_names = ["Kỹ năng sống", "Văn học", "Công nghệ", "Khoa học", "Viễn tưởng"]
    category_ids = {}

    for name in category_names:
        r = requests.post(f"{BOOK_URL}/categories/", json={"name": name, "slug": name.lower().replace(" ", "-")}, headers=headers)
        if r.status_code in (200, 201):
            cid = r.json().get("id")
            category_ids[name] = cid
            print(f"  ✅ Category: {name} (id={cid})")
        else:
            # Thử GET nếu đã tồn tại
            r2 = requests.get(f"{BOOK_URL}/categories/", headers=headers)
            if r2.status_code == 200:
                cats = r2.json() if isinstance(r2.json(), list) else r2.json().get("results", [])
                for c in cats:
                    if c["name"] == name:
                        category_ids[name] = c["id"]
                        print(f"  ♻️  Exists: {name} (id={c['id']})")
                        break
            else:
                print(f"  ⚠️  Skip category: {name}")

    # ─── 4. TẠO SÁCH ────────────────────────────────────────────
    print("\n📚 Tạo sách mẫu...")

    # Lấy id category (fallback = None nếu không có)
    ky_nang   = category_ids.get("Kỹ năng sống")
    van_hoc   = category_ids.get("Văn học")
    cong_nghe = category_ids.get("Công nghệ")
    khoa_hoc  = category_ids.get("Khoa học")
    vien_tuong = category_ids.get("Viễn tưởng")

    books = [
        {
            "title": "Đắc Nhân Tâm",
            "slug": "dac-nhan-tam",
            "author": "Dale Carnegie",
            "publisher": "NXB Tổng hợp TP.HCM",
            "price": 88000,
            "original_price": 110000,
            "stock": 50,
            "category": ky_nang,
            "language": "Vietnamese",
            "description": "Cuốn sách kinh điển về nghệ thuật giao tiếp và ứng xử.",
            "cover_image": "https://salt.tikicdn.com/ts/product/5a/cb/41/4927e4d8dc574c9b3f238898a5771d4e.jpg",
            "is_featured": True,
        },
        {
            "title": "Nhà Giả Kim",
            "slug": "nha-gia-kim",
            "author": "Paulo Coelho",
            "publisher": "NXB Hội Nhà Văn",
            "price": 79000,
            "original_price": 99000,
            "stock": 40,
            "category": van_hoc,
            "language": "Vietnamese",
            "description": "Hành trình theo đuổi giấc mơ của chàng trai trẻ Santiago.",
            "cover_image": "https://salt.tikicdn.com/ts/product/45/3b/fc/4528c46109c2252d3af1b285e2e759d7.jpg",
            "is_featured": True,
        },
        {
            "title": "Clean Code",
            "slug": "clean-code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "price": 320000,
            "original_price": 380000,
            "stock": 25,
            "category": cong_nghe,
            "language": "English",
            "description": "Hướng dẫn viết code sạch và dễ bảo trì.",
            "cover_image": "https://m.media-amazon.com/images/I/41xShlnTZTL._SX376_BO1,204,203,200_.jpg",
            "is_featured": False,
        },
        {
            "title": "Tư Duy Nhanh Và Chậm",
            "slug": "tu-duy-nhanh-va-cham",
            "author": "Daniel Kahneman",
            "publisher": "NXB Thế Giới",
            "price": 135000,
            "original_price": 169000,
            "stock": 30,
            "category": khoa_hoc,
            "language": "Vietnamese",
            "description": "Khám phá hai hệ thống tư duy điều khiển cách chúng ta suy nghĩ.",
            "cover_image": "https://salt.tikicdn.com/ts/product/df/7d/da/3d647d4aa67b9c8e3756811f0ed8c2b2.jpg",
            "is_featured": True,
        },
        {
            "title": "Design Patterns",
            "slug": "design-patterns",
            "author": "Gang of Four",
            "publisher": "Addison-Wesley",
            "price": 450000,
            "original_price": 520000,
            "stock": 15,
            "category": cong_nghe,
            "language": "English",
            "description": "23 mẫu thiết kế phần mềm kinh điển.",
            "cover_image": "https://m.media-amazon.com/images/I/51szD9HC9pL._SX395_BO1,204,203,200_.jpg",
            "is_featured": False,
        },
        {
            "title": "Sapiens: Lược Sử Loài Người",
            "slug": "sapiens-luoc-su-loai-nguoi",
            "author": "Yuval Noah Harari",
            "publisher": "NXB Tri Thức",
            "price": 189000,
            "original_price": 229000,
            "stock": 35,
            "category": khoa_hoc,
            "language": "Vietnamese",
            "description": "Lịch sử loài người từ thời tiền sử đến hiện đại.",
            "cover_image": "https://salt.tikicdn.com/ts/product/f0/a4/6c/7f3479b7437da81ac8e4ede873b41e23.jpg",
            "is_featured": True,
        },
        {
            "title": "The Pragmatic Programmer",
            "slug": "the-pragmatic-programmer",
            "author": "Andrew Hunt",
            "publisher": "Addison-Wesley",
            "price": 380000,
            "original_price": 450000,
            "stock": 20,
            "category": cong_nghe,
            "language": "English",
            "description": "Cẩm nang thực tế cho lập trình viên chuyên nghiệp.",
            "cover_image": "https://m.media-amazon.com/images/I/51W1sBPO7tL._SX380_BO1,204,203,200_.jpg",
            "is_featured": False,
        },
        {
            "title": "Atomic Habits",
            "slug": "atomic-habits",
            "author": "James Clear",
            "publisher": "NXB Lao Động",
            "price": 118000,
            "original_price": 149000,
            "stock": 60,
            "category": ky_nang,
            "language": "Vietnamese",
            "description": "Thay đổi thói quen nhỏ, tạo kết quả lớn.",
            "cover_image": "https://salt.tikicdn.com/ts/product/03/f5/b7/7e5a3b56ad3e75c33b5ad3e47a5e73cf.jpg",
            "is_featured": True,
        },
        {
            "title": "Python Crash Course",
            "slug": "python-crash-course",
            "author": "Eric Matthes",
            "publisher": "No Starch Press",
            "price": 290000,
            "original_price": 350000,
            "stock": 45,
            "category": cong_nghe,
            "language": "English",
            "description": "Học Python nhanh chóng qua các dự án thực tế.",
            "cover_image": "https://m.media-amazon.com/images/I/51dqJ8AgDPL._SX376_BO1,204,203,200_.jpg",
            "is_featured": False,
        },
        {
            "title": "Dune - Xứ Cát",
            "slug": "dune-xu-cat",
            "author": "Frank Herbert",
            "publisher": "NXB Hội Nhà Văn",
            "price": 220000,
            "original_price": 269000,
            "stock": 28,
            "category": vien_tuong,
            "language": "Vietnamese",
            "description": "Sử thi khoa học viễn tưởng vĩ đại nhất mọi thời đại.",
            "cover_image": "https://salt.tikicdn.com/ts/product/5f/0e/ea/6e6b5271df0f4e7da9d4e7d9e0e3a4b5.jpg",
            "is_featured": True,
        },
    ]

    success = 0
    for book in books:
        # Bỏ category nếu None
        if book.get("category") is None:
            book.pop("category")

        r = requests.post(f"{BOOK_URL}/", json=book, headers=headers)
        if r.status_code in (200, 201):
            print(f"  ✅ Created: {book['title']}")
            success += 1
        else:
            print(f"  ❌ Failed: {book['title']} — {r.text[:80]}")

    # ─── KẾT QUẢ ────────────────────────────────────────────────
    print(f"\n✅ Seed data hoàn tất!")
    print(f"   👤 {len(users)} users")
    print(f"   📂 {len(category_ids)} categories")
    print(f"   📚 {success}/{len(books)} books created")
    print(f"\n🔑 Login credentials:")
    print(f"   Admin:    admin / admin123")
    print(f"   Staff:    staff1 / staff123")
    print(f"   Customer: customer1 / pass123")

if __name__ == "__main__":
    seed()