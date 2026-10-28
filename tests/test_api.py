import requests, os
BASE=os.getenv("APP_URL","http://localhost:5000")
def test_health():
    r=requests.get(BASE+"/health",timeout=5); assert r.status_code==200 and r.json()["status"]=="ok"
def test_login_success():
    r=requests.post(BASE+"/api/login",json={"username":"demo","password":"demo123"},timeout=5)
    assert r.status_code==200 and r.json()["success"]
def test_login_failure():
    r=requests.post(BASE+"/api/login",json={"username":"","password":""},timeout=5)
    assert r.status_code==401
def test_search():
    d=requests.get(BASE+"/api/search",params={"from":"Pune","to":"Delhi"},timeout=5).json()
    assert len(d["trips"]) >= 1 and d["trips"][0]["to"]=="Delhi"
def test_booking_and_cancellation():
    b=requests.post(BASE+"/api/book",timeout=5).json()
    c=requests.post(BASE+"/api/cancel",timeout=5).json()
    assert b["success"] and "confirmed" in b["message"].lower()
    assert c["success"] and "cancelled" in c["message"].lower()
