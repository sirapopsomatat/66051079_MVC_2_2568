import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, flash

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(base_dir)

from model.models import PoliticianModel

view_dir = os.path.join(base_dir, "view")
app = Flask(__name__, template_folder=view_dir)
app.secret_key = "secret_politician_key"

model = PoliticianModel()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        session['user_role'] = 'admin' if username == 'admin' else 'user'
        session['username'] = username
        return redirect(url_for('all_promises'))
    return '''
        <h2>เข้าสู่ระบบ</h2>
        <form method="post">
            ชื่อผู้ใช้: <input type="text" name="username" placeholder="พิมพ์ admin หรือชื่ออื่น">
            <input type="submit" value="เข้าสู่ระบบ">
        </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def all_promises():
    if 'user_role' not in session:
        return redirect(url_for('login'))
    promises = model.get_all_promises()
    return render_template('all_promises.html', promises=promises)

@app.route('/promise/<id>')
def promise_detail(id):
    promise = model.get_promise_by_id(id)
    if not promise:
        return "ไม่พบข้อมูลคำสัญญา", 404
    updates = model.get_updates_by_promise(id)
    return render_template('promise_detail.html', promise=promise, updates=updates)

@app.route('/promise/<id>/update', methods=['GET', 'POST'])
def update_promise(id):
    if session.get('user_role') != 'admin':
        return "สิทธิ์ของคุณไม่เพียงพอ (ต้องเป็น Admin เท่านั้น)", 403

    promise = model.get_promise_by_id(id)
    if not promise:
        return "ไม่พบข้อมูลคำสัญญา", 404
    if promise['status'] == "เงียบหาย":
        return "คำสัญญานี้ 'เงียบหาย' ไปแล้ว ไม่สามารถอัปเดตได้", 400

    if request.method == 'POST':
        detail = request.form.get('detail')
        success, message = model.add_update(id, detail)
        if success:
            return redirect(url_for('promise_detail', id=id))
        else:
            return message
    return render_template('update_promise.html', promise=promise)
@app.route('/politician/<politician_id>')
def politician_promises(politician_id):
    promises = model.get_promises_by_politician(politician_id)
    pol_name = promises[0]['politician_name'] if promises else "ไม่พบข้อมูล"
    return render_template('politician_promises.html', promises=promises, pol_name=pol_name)

if __name__ == '__main__':
    print(f"Server is starting...\nTemplate folder: {view_dir}")
    app.run(debug=True)