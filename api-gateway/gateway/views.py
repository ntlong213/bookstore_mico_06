from django.shortcuts import render, redirect
import requests, logging, jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from .jwt_middleware import SECRET_KEY
import json

logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = "http://auth-service:8000"
SERVICES = {
    'book':      'http://book-service:8000',
    'customer':  'http://customer-service:8000',
    'cart':      'http://cart-service:8000',
    'order':     'http://order-service:8000',
    'pay':       'http://pay-service:8000',
    'ship':      'http://ship-service:8000',
    'comment':   'http://comment-rate-service:8000',
    'recommend': 'http://recommender-ai-service:8000',
    'catalog':   'http://catalog-service:8000',
    'staff':     'http://staff-service:8000',
    'auth':      'http://auth-service:8000',
}

# ─── HELPERS ──────────────────────────────────────────────────────

def _get_session_payload(request):
    """Lấy payload từ session (đã decode khi login)."""
    return request.session.get('user_payload', {})

def _get_role(request):
    return _get_session_payload(request).get('role', '')

def _get_token(request):
    return request.session.get('token', '')

def _auth_headers(request):
    token = _get_token(request)
    if token:
        return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    return {'Content-Type': 'application/json'}

def _require_login(request):
    """Trả về redirect nếu chưa login."""
    if not _get_token(request):
        return redirect('login')
    return None

def _require_role(request, allowed_roles):
    """Trả về redirect nếu không đúng role."""
    check = _require_login(request)
    if check:
        return check
    role = _get_role(request)
    if role not in allowed_roles:
        return redirect('home')
    return None


# ─── AUTH ─────────────────────────────────────────────────────────

def login_view(request):
    # Nếu đã login thì redirect theo role
    if _get_token(request):
        return _redirect_by_role(request)

    message = ''
    if request.method == 'POST':
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }
        try:
            r = requests.post(f"{AUTH_SERVICE_URL}/auth/login/", json=data, timeout=5)
            if r.status_code == 200:
                token = r.json().get('token')
                request.session['token'] = token
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                    request.session['user_payload'] = payload
                except Exception:
                    pass
                return _redirect_by_role(request)
            else:
                message = r.json().get('error', 'Sai tên đăng nhập hoặc mật khẩu')
        except Exception:
            message = 'Không thể kết nối auth service'
    return render(request, 'login.html', {'message': message})


@csrf_exempt
def api_login(request):
    """API endpoint for login - returns JSON for Postman testing."""
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return JsonResponse({"error": "Username and password required"}, status=400)
    
    try:
        r = requests.post(f"{AUTH_SERVICE_URL}/auth/login/", json={'username': username, 'password': password}, timeout=5)
        if r.status_code == 200:
            response_data = r.json()
            return JsonResponse({
                "message": "Login successful",
                "token": response_data.get('token'),
                "user": response_data.get('user')
            })
        else:
            return JsonResponse({"error": r.json().get('error', 'Login failed')}, status=r.status_code)
    except Exception as e:
        return JsonResponse({"error": "Auth service unavailable"}, status=503)


def logout_view(request):
    request.session.flush()
    return redirect('login')


def _redirect_by_role(request):
    """Redirect đến trang phù hợp theo role."""
    role = _get_role(request)
    if role == 'manager':
        return redirect('dashboard')
    elif role == 'staff':
        return redirect('staff_dashboard')
    else:
        return redirect('home')


# ─── CUSTOMER PAGES ───────────────────────────────────────────────

def home(request):
    """Root page; behaviour depends on login/role.

    - not logged in: show public list of books with login link.
    - customer: show customer home (same template but with cart/logout). 
    - staff: redirect to staff dashboard.
    - manager: redirect to admin dashboard.
    """
    token = _get_token(request)
    # guest view
    if not token:
        headers = {'Content-Type': 'application/json'}
        books = []
        try:
            r = requests.get(f"{SERVICES['book']}/books/", headers=headers, timeout=5)
            if isinstance(r.json(), list):
                books = r.json()
            else:
                books = r.json().get('results', [])
        except:
            books = []
        return render(request, 'home.html', {
            'books': books,
            'user': {},
            'role': '',
            'cart_count': 0,
        })

    # logged in – decide by role
    role = _get_role(request)
    if role == 'manager':
        return redirect('dashboard')
    if role == 'staff':
        return redirect('staff_dashboard')
    # default to customer home
    headers = _auth_headers(request)
    payload = _get_session_payload(request)
    books = []
    try:
        r = requests.get(f"{SERVICES['book']}/books/", headers=headers, timeout=5)
        if isinstance(r.json(), list):
            books = r.json()
        else:
            books = r.json().get('results', [])
    except:
        books = []
    return render(request, 'home.html', {
        'books': books,
        'user': payload,
        'role': role,
        'cart_count': sum(request.session.get('cart', {}).values()),
    })


def book_detail(request, book_id):
    """Chi tiết sách + đánh giá."""
    guard = _require_login(request)
    if guard:
        return guard
    headers = _auth_headers(request)
    book = {}
    comments = []
    try:
        r = requests.get(f"{SERVICES['book']}/books/{book_id}/", headers=headers, timeout=5)
        book = r.json()
    except:
        pass
    try:
        r = requests.get(f"{SERVICES['comment']}/comments/?book_id={book_id}", headers=headers, timeout=5)
        comments = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
    except:
        pass
    return render(request, 'book_details.html', {'book': book, 'comments': comments})
def book_edit(request, book_id):
    """Sửa thông tin sách — staff & manager."""
    guard = _require_role(request, ['staff', 'manager'])
    if guard:
        return guard
    headers = _auth_headers(request)
    message = ''
    book = {}

    if request.method == 'POST':
        data = {
            'title':          request.POST.get('title'),
            'author':         request.POST.get('author'),
            'price':          request.POST.get('price'),
            'original_price': request.POST.get('original_price') or None,
            'stock':          request.POST.get('stock'),
            'publisher':      request.POST.get('publisher') or '',
            'cover_image':    request.POST.get('cover_image') or '',
            'description':    request.POST.get('description') or '',
            'language':       request.POST.get('language') or 'Vietnamese',
        }
        try:
            r = requests.put(
                f"{SERVICES['book']}/books/{book_id}/",
                json=data, headers=headers, timeout=5
            )
            if r.status_code in (200, 201):
                return redirect('book_list')
            message = f'Lỗi: {r.text[:100]}'
        except:
            message = 'Không thể kết nối book service'

    try:
        r = requests.get(f"{SERVICES['book']}/books/{book_id}/", headers=headers, timeout=5)
        book = r.json()
    except:
        pass

    return render(request, 'edit_book.html', {
        'book': book,
        'message': message,
        'user': _get_session_payload(request),
    })


def book_delete(request, book_id):
    """Xóa sách — staff & manager."""
    guard = _require_role(request, ['staff', 'manager'])
    if guard:
        return guard
    if request.method == 'POST':
        headers = _auth_headers(request)
        try:
            requests.delete(
                f"{SERVICES['book']}/books/{book_id}/",
                headers=headers, timeout=5
            )
        except:
            pass
    return redirect('book_list')


def add_to_cart(request):
    """Thêm sách vào giỏ — chỉ customer."""
    guard = _require_login(request)
    if guard:
        return guard
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        quantity = int(request.POST.get('quantity', 1))
        headers = _auth_headers(request)
        payload = _get_session_payload(request)
        customer_id = payload.get('user_id')
        
        # Lưu vào session
        if 'cart' not in request.session:
            request.session['cart'] = {}
        if book_id:
            if book_id in request.session['cart']:
                request.session['cart'][book_id] += quantity
            else:
                request.session['cart'][book_id] = quantity
            request.session.modified = True
        
        # Đồng thời gửi tới backend
        if customer_id:
            data = {
                'book_id': book_id,
                'quantity': quantity,
            }
            try:
                requests.post(
                    f"{SERVICES['cart']}/carts/{customer_id}/items/",
                    json=data, headers=headers, timeout=5
                )
            except:
                pass
    
    # Redirect về trang chi tiết sách hoặc home
    ref = request.POST.get('referer', 'home')
    if ref.startswith('/books/'):
        return redirect(ref)
    return redirect('home')


def my_cart(request):
    """Giỏ hàng của customer đang login."""
    guard = _require_login(request)
    if guard:
        return guard
    payload = _get_session_payload(request)
    headers = _auth_headers(request)
    
    # Lấy sách từ session
    session_cart = request.session.get('cart', {})
    cart_items = []
    
    # Với mỗi sách trong giỏ, fetch thông tin từ book-service
    for book_id_str, quantity in session_cart.items():
        try:
            r = requests.get(
                f"{SERVICES['book']}/books/{book_id_str}/",
                headers=headers, timeout=5
            )
            book = r.json()
            cart_items.append({
                'book_id': book_id_str,
                'quantity': quantity,
                'title': book.get('title', f'Sách #{book_id_str}'),
                'price_at_add': book.get('price', 0),
                'cover_image': book.get('cover_image', ''),
            })
        except:
            # Nếu không lấy được từ service, vẫn hiển thị với info cơ bản
            cart_items.append({
                'book_id': book_id_str,
                'quantity': quantity,
                'title': f'Sách #{book_id_str}',
                'price_at_add': 0,
                'cover_image': '',
            })
    
    return render(request, 'cart.html', {
        'cart': {'items': cart_items},
        'customer_id': payload.get('user_id'),
        'user': payload
    })


@csrf_exempt
def remove_from_cart(request):
    """Xóa sách khỏi giỏ hàng."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=400)
    
    book_id = request.POST.get('book_id')
    if not book_id:
        return JsonResponse({'error': 'Missing book_id'}, status=400)
    
    session_cart = request.session.get('cart', {})
    if str(book_id) in session_cart:
        del session_cart[str(book_id)]
        request.session['cart'] = session_cart
        request.session.modified = True
    
    return JsonResponse({'success': True})


def view_cart(request, customer_id):
    guard = _require_login(request)
    if guard:
        return guard
    headers = _auth_headers(request)
    cart_data = {'items': []}
    try:
        r = requests.get(f"{SERVICES['cart']}/carts/{customer_id}/", headers=headers, timeout=5)
        cart_data = r.json()
    except:
        pass
    return render(request, 'cart.html', {'cart': cart_data, 'customer_id': customer_id})


def checkout(request):
    """Trang thanh toán — chỉ customer."""
    guard = _require_login(request)
    if guard:
        return guard
    payload = _get_session_payload(request)
    headers = _auth_headers(request)
    message = ''
    if request.method == 'POST':
        data = {
            'customer_id': payload.get('user_id'),
            'payment_method': request.POST.get('payment_method'),
            'shipping_address': request.POST.get('shipping_address') or
                f"{request.POST.get('address')}, {request.POST.get('city')}",
        }
        try:
            r = requests.post(f"{SERVICES['order']}/orders/", json=data, headers=headers, timeout=5)
            if r.status_code in (200, 201):
                return redirect('home')
            message = str(r.json())
        except:
            message = 'Không thể tạo đơn hàng'
    return render(request, 'checkout.html', {'user': payload, 'message': message})


def create_customer(request):
    """Đăng ký tài khoản mới — public."""
    message = ''
    if request.method == 'POST':
        data = {
            'username': request.POST.get('name', '').replace(' ', '_').lower(),
            'email':    request.POST.get('email'),
            'password': request.POST.get('password', '123456'),
            'role':     'customer',
        }
        try:
            r = requests.post(f"{AUTH_SERVICE_URL}/auth/register/", json=data, timeout=5)
            if r.status_code == 201:
                message = f"Tạo tài khoản thành công! ID: {r.json().get('user_id', '')}"
            else:
                message = f"Lỗi: {r.json()}"
        except:
            message = 'Không thể kết nối server'
    return render(request, 'create_customer.html', {'message': message})


# ─── STAFF PAGES ──────────────────────────────────────────────────

def staff_dashboard(request):
    """Dashboard riêng cho staff."""
    guard = _require_role(request, ['staff', 'manager'])
    if guard:
        return guard
    headers = _auth_headers(request)
    payload = _get_session_payload(request)

    # Lấy danh sách sách + thống kê
    books = []
    try:
        r = requests.get(f"{SERVICES['book']}/books/", headers=headers, timeout=5)
        books = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
    except:
        pass

    # Thống kê
    total_books = len(books)
    total_stock = sum(b.get('stock', 0) for b in books)
    total_sold  = sum(b.get('sold_count', 0) for b in books)
    low_stock   = [b for b in books if 0 < b.get('stock', 0) <= 5]

    return render(request, 'staff_dashboard.html', {
        'books': books,
        'user': payload,
        'stats': {
            'total_books': total_books,
            'total_stock': total_stock,
            'total_sold':  total_sold,
            'low_stock_count': len(low_stock),
            'low_stock_books': low_stock,
        }
    })


def book_list(request):
    """Quản lý sách — staff & manager."""
    guard = _require_role(request, ['staff', 'manager'])
    if guard:
        return guard
    headers = _auth_headers(request)
    books = []
    message = ''

    if request.method == 'POST':
        data = {
            'title':          request.POST.get('title'),
            'author':         request.POST.get('author'),
            'price':          request.POST.get('price'),
            'original_price': request.POST.get('original_price') or None,
            'stock':          request.POST.get('stock'),
            'publisher':      request.POST.get('publisher') or '',
            'cover_image':    request.POST.get('cover_image') or '',
            'description':    request.POST.get('description') or '',
            'language':       request.POST.get('language') or 'Vietnamese',
        }
        try:
            r = requests.post(f"{SERVICES['book']}/books/", json=data, headers=headers, timeout=5)
            if r.status_code in (200, 201):
                message = 'Thêm sách thành công!'
            else:
                message = f'Lỗi: {r.text[:100]}'
        except:
            message = 'Không thể kết nối book service'

    try:
        r = requests.get(f"{SERVICES['book']}/books/", headers=headers, timeout=5)
        books = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
    except:
        books = []

    return render(request, 'books.html', {
        'books': books,
        'message': message,
        'user': _get_session_payload(request),
    })


def staff_comments(request):
    """Xem & trả lời đánh giá — staff."""
    guard = _require_role(request, ['staff', 'manager'])
    if guard:
        return guard
    headers = _auth_headers(request)
    comments = []
    try:
        r = requests.get(f"{SERVICES['comment']}/comments/", headers=headers, timeout=5)
        comments = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
    except:
        pass
    return render(request, 'staff_comments.html', {
        'comments': comments,
        'user': _get_session_payload(request),
    })


# ─── MANAGER/ADMIN PAGES ──────────────────────────────────────────

def dashboard(request):
    """Dashboard tổng quan — chỉ manager."""
    guard = _require_role(request, ['manager'])
    if guard:
        return guard
    headers = _auth_headers(request)
    payload = _get_session_payload(request)

    # Service health
    stats = {}
    for name, url in SERVICES.items():
        try:
            r = requests.get(f"{url}/health/", timeout=2)
            stats[name] = 'online'
        except:
            stats[name] = 'offline'

    # Lấy danh sách users
    users = []
    try:
        r = requests.get(f"{AUTH_SERVICE_URL}/auth/users/", headers=headers, timeout=5)
        users = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
    except:
        pass

    return render(request, 'dashboard.html', {
        'stats': stats,
        'users': users,
        'user': payload,
        'total_users': len(users),
    })


def admin_users(request):
    """API endpoint to list all users — chỉ manager."""
    guard = _require_role(request, ['manager'])
    if guard:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    headers = _auth_headers(request)
    try:
        r = requests.get(f"{AUTH_SERVICE_URL}/auth/users/", headers=headers, timeout=5)
        if r.status_code == 200:
            users = r.json() if isinstance(r.json(), list) else r.json().get('results', [])
            return JsonResponse({"users": users})
        else:
            return JsonResponse({"error": "Failed to fetch users"}, status=500)
    except:
        return JsonResponse({"error": "Service unavailable"}, status=503)


def create_order(request):
    """Tạo đơn hàng thủ công — manager."""
    guard = _require_role(request, ['manager', 'staff'])
    if guard:
        return guard
    headers = _auth_headers(request)
    message = ''
    if request.method == 'POST':
        data = {
            'customer_id':    request.POST.get('customer_id'),
            'payment_method': request.POST.get('payment_method'),
            'shipping_address': request.POST.get('shipping_address'),
        }
        try:
            r = requests.post(f"{SERVICES['order']}/orders/", json=data, headers=headers, timeout=5)
            message = r.json()
        except:
            message = 'Lỗi kết nối'
    return render(request, 'create_order.html', {
        'message': message,
        'user': _get_session_payload(request),
    })


# ─── PROXY API ────────────────────────────────────────────────────

PUBLIC_ROUTES = ['/api/auth/login/', '/api/auth/register/', '/health/']

@csrf_exempt
def proxy(request, service, path=''):
    full_path = f"/api/{service}/{path}"
    if full_path not in PUBLIC_ROUTES:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return JsonResponse({"error": "Token required"}, status=401)
        try:
            r = requests.post(f"{AUTH_SERVICE_URL}/auth/validate/",
                json={"token": token}, timeout=3)
            result = r.json()
            if not result.get('valid'):
                return JsonResponse({"error": result.get('error', 'Invalid token')}, status=401)
        except Exception:
            return JsonResponse({"error": "Auth service unavailable"}, status=503)

    if service not in SERVICES:
        return JsonResponse({"error": "Service not found"}, status=404)

    url = f"{SERVICES[service]}/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': request.headers.get('Authorization', '')
            },
            data=request.body,
            params=request.GET,
            timeout=10
        )
        return JsonResponse(resp.json(), status=resp.status_code, safe=False)
    except requests.Timeout:
        return JsonResponse({"error": "Service timeout"}, status=504)
    except Exception:
        return JsonResponse({"error": "Service unavailable"}, status=503)


def health_check(request):
    return JsonResponse({"status": "healthy", "gateway": "online"})