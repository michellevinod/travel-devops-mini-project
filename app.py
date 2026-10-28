from flask import Flask, request, jsonify, render_template_string
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time, os

app = Flask(__name__)
REQUESTS = Counter("travel_http_requests_total", "Total HTTP requests", ["method","endpoint","status"])
LATENCY = Histogram("travel_http_request_duration_seconds", "HTTP request latency", ["endpoint"])
BOOKINGS = Counter("travel_bookings_total", "Booking actions", ["action"])
INPROGRESS = Gauge("travel_demo_up", "Application up indicator")
INPROGRESS.set(1)

PAGE = """
<!doctype html><html><head><title>Travel Booking Demo</title>
<style>body{font:16px Arial;max-width:850px;margin:40px auto;padding:0 18px;background:#f5f7fb;color:#172033}
.card{background:white;padding:22px;margin:16px 0;border-radius:12px;box-shadow:0 2px 12px #0001}
input,button{padding:10px;margin:5px;border:1px solid #ccd2df;border-radius:6px}button{background:#2457c5;color:white;cursor:pointer}
#message{font-weight:bold;color:#176b3a}.trip{padding:10px;border:1px solid #ddd;margin:8px 0;border-radius:8px}</style></head>
<body><h1>✈ Travel Booking Portal</h1><p>DevOps CI/CD demonstration application</p>
<div class="card"><h2>1. Login (Demo)</h2><p>Demo mode: enter any non-empty username and password. Signup and real accounts are not implemented.</p><input id="username" placeholder="Username"><input id="password" type="password" placeholder="Password"><button id="loginBtn" onclick="login()">Login</button></div>
<div class="card"><h2>2. Search trips</h2><input id="origin" placeholder="From" value="Pune"><input id="destination" placeholder="To" value="Delhi"><button id="searchBtn" onclick="searchTrips()">Search</button><div id="results"></div></div>
<div class="card"><h2>3. Booking</h2><button id="bookBtn" onclick="book()">Book selected trip</button><button id="cancelBtn" onclick="cancel()">Cancel booking</button><p id="bookingStatus">No booking yet</p></div>
<p id="message" role="status"></p>
<script>
let loggedIn=false, selected=false, booked=false;
function msg(t){document.getElementById('message').innerText=t}
async function login(){const u=document.getElementById('username').value,p=document.getElementById('password').value;
const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});const d=await r.json();loggedIn=d.success;msg(d.message)}
async function searchTrips(){const a=document.getElementById('origin').value,b=document.getElementById('destination').value;
const r=await fetch('/api/search?from='+encodeURIComponent(a)+'&to='+encodeURIComponent(b));const d=await r.json();
document.getElementById('results').innerHTML=d.trips.map((t,i)=>'<div class="trip"><label><input type="radio" name="selectedTrip" id="trip-'+t.id+'" value="'+t.id+'" '+(i===0?'checked':'')+'>'+t.id+': '+t.from+' → '+t.to+' | ₹'+t.price+'</label></div>').join('');selected=d.trips.length>0;msg('Search completed. Select a trip before booking.')}
async function book(){if(!loggedIn){msg('Please login first');return}if(!selected){msg('Search for a trip first');return}
const choice=document.querySelector('input[name="selectedTrip"]:checked');if(!choice){msg('Please select a trip');return}
const r=await fetch('/api/book',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({trip_id:choice.value})});const d=await r.json();booked=d.success;document.getElementById('bookingStatus').innerText=d.message;msg(d.message)}
async function cancel(){if(!booked){msg('No active booking to cancel');return}
const r=await fetch('/api/cancel',{method:'POST'});const d=await r.json();if(d.success)booked=false;document.getElementById('bookingStatus').innerText=d.message;msg(d.message)}
</script></body></html>"""

@app.before_request
def start_timer():
    request._started_at = time.perf_counter()

@app.after_request
def record_metrics(response):
    endpoint = request.endpoint or "unknown"
    REQUESTS.labels(request.method, endpoint, str(response.status_code)).inc()
    LATENCY.labels(endpoint).observe(time.perf_counter() - getattr(request, "_started_at", time.perf_counter()))
    return response

@app.get("/")
def home(): return render_template_string(PAGE)

@app.get("/health")
def health(): return jsonify(status="ok")

@app.get("/metrics")
def metrics(): return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.post("/api/login")
def login():
    d=request.get_json(silent=True) or {}
    ok=bool(d.get("username") and d.get("password"))
    return jsonify(success=ok,message="Login successful" if ok else "Invalid credentials"), (200 if ok else 401)

@app.get("/api/search")
def search():
    origin=request.args.get("from","Pune"); dest=request.args.get("to","Delhi")
    return jsonify(trips=[{"id":"TR101","from":origin,"to":dest,"price":4500},{"id":"TR102","from":origin,"to":dest,"price":5200}])

active_booking = {"id": None, "trip_id": None}

@app.post("/api/book")
def book():
    d=request.get_json(silent=True) or {}
    trip_id=d.get("trip_id","TR101")
    if trip_id not in {"TR101","TR102"}:
        return jsonify(success=False,message="Please select a valid trip"), 400
    active_booking.update(id="BK1001", trip_id=trip_id)
    BOOKINGS.labels("book").inc()
    return jsonify(success=True,message=f"Booking confirmed: BK1001 for {trip_id}")

@app.post("/api/cancel")
def cancel():
    if active_booking["id"] is None:
        return jsonify(success=False,message="No active booking to cancel"), 409
    active_booking.update(id=None, trip_id=None)
    BOOKINGS.labels("cancel").inc()
    return jsonify(success=True,message="Booking cancelled")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")))
