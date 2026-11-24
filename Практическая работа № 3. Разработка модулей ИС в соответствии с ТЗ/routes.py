import re
from datetime import date
from functools import wraps
from flask import Blueprint,render_template,redirect,url_for,flash,request,abort
from flask_login import login_user,logout_user,login_required,current_user
from .extensions import db
from .models import User,Event,Request as Booking,Status,Review
main=Blueprint('main',__name__);auth=Blueprint('auth',__name__);participant=Blueprint('participant',__name__);admin=Blueprint('admin',__name__)
def admin_only(fn):
 @wraps(fn)
 @login_required
 def wrapped(*a,**kw):
  if current_user.role!='admin':abort(403)
  return fn(*a,**kw)
 return wrapped
@main.get('/')
def index():return render_template('index.html',events=Event.query.filter_by(is_active=True).order_by(Event.event_date).all())
@auth.route('/register',methods=['GET','POST'])
def register():
 if request.method=='POST':
  login=request.form.get('login','').strip();email=request.form.get('email','').strip().lower();phone=request.form.get('phone','').strip();pw=request.form.get('password','');errors=[]
  if not re.fullmatch(r'[A-Za-zА-Яа-яЁё0-9_.-]{6,50}',login):errors.append('Логин: 6–50 допустимых символов.')
  if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email):errors.append('Некорректный email.')
  if not re.fullmatch(r'[+()\d\-\s]{7,24}',phone):errors.append('Некорректный телефон.')
  if len(pw)<8:errors.append('Пароль должен быть не короче 8 символов.')
  if User.query.filter_by(login=login).first():errors.append('Логин уже занят.')
  if User.query.filter_by(email=email).first():errors.append('Email уже зарегистрирован.')
  if errors:
   [flash(x,'error') for x in errors];return render_template('register.html')
  u=User(login=login,email=email,phone=phone);u.set_password(pw);db.session.add(u);db.session.commit();flash('Регистрация завершена. Войдите.','success');return redirect(url_for('auth.login'))
 return render_template('register.html')
@auth.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  u=User.query.filter_by(login=request.form.get('login','').strip()).first()
  if u and u.check_password(request.form.get('password','')):
   login_user(u);return redirect(url_for('admin.dashboard' if u.role=='admin' else 'participant.dashboard'))
  flash('Неверный логин или пароль.','error')
 return render_template('login.html')
@auth.get('/logout')
@login_required
def logout():logout_user();return redirect(url_for('main.index'))
@participant.get('/')
@login_required
def dashboard():return render_template('dashboard.html',items=Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all(),events=Event.query.filter_by(is_active=True).all())
@participant.post('/requests')
@login_required
def create_request():
 ev=db.session.get(Event,request.form.get('event_id',type=int));pay=request.form.get('payment_method','')
 if not ev or not ev.is_active or pay not in {'Без оплаты','Картой на месте','По счёту'}:flash('Проверьте мероприятие и способ оплаты.','error')
 elif Booking.query.filter_by(user_id=current_user.id,event_id=ev.id).first():flash('Заявка уже существует.','error')
 else:
  st=Status.query.filter_by(name='Новая').one();db.session.add(Booking(user_id=current_user.id,event_id=ev.id,status_id=st.id,payment_method=pay));db.session.commit();flash('Заявка создана.','success')
 return redirect(url_for('participant.dashboard'))
@participant.post('/requests/<int:rid>/review')
@login_required
def review(rid):
 b=db.session.get(Booking,rid)
 if not b or b.user_id!=current_user.id:abort(404)
 text=request.form.get('text','').strip();rating=request.form.get('rating',type=int)
 if b.status.name!='Завершено' or b.review or not text or len(text)>1500 or rating not in range(1,6):flash('Отзыв недоступен или заполнен неверно.','error')
 else:db.session.add(Review(request_id=b.id,text=text,rating=rating));db.session.commit();flash('Отзыв сохранён.','success')
 return redirect(url_for('participant.dashboard'))
@admin.get('/')
@admin_only
def dashboard():
 q=Booking.query.join(Status);sid=request.args.get('status',type=int)
 if sid:q=q.filter(Booking.status_id==sid)
 return render_template('admin.html',items=q.order_by(Booking.created_at.desc()).all(),statuses=Status.query.all(),selected=sid)
@admin.post('/requests/<int:rid>/status')
@admin_only
def change_status(rid):
 b=db.session.get(Booking,rid);st=db.session.get(Status,request.form.get('status_id',type=int))
 if not b or not st:abort(404)
 nxt={'Новая':'Мероприятие назначено','Мероприятие назначено':'Завершено'}
 if nxt.get(b.status.name)!=st.name:flash('Недопустимый переход статуса.','error')
 else:b.status=st;db.session.commit();flash('Статус изменён.','success')
 return redirect(url_for('admin.dashboard'))
@admin.route('/events',methods=['GET','POST'])
@admin_only
def events():
 if request.method=='POST':
  try:dt=date.fromisoformat(request.form.get('event_date',''))
  except ValueError:dt=None
  title=request.form.get('title','').strip();venue=request.form.get('venue','').strip()
  if not title or not venue or not dt:flash('Заполните название, место и дату.','error')
  else:db.session.add(Event(title=title,venue=venue,event_date=dt,description=request.form.get('description','')));db.session.commit();flash('Мероприятие добавлено.','success')
 return render_template('events.html',events=Event.query.order_by(Event.event_date).all())
