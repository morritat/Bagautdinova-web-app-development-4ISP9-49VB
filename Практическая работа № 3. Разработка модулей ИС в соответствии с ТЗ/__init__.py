import os
from datetime import date,timedelta
from flask import Flask
from .extensions import db,login_manager,csrf
from .models import Event,Status,User
def create_app(test_config=None):
 app=Flask(__name__,instance_relative_config=True); app.config.from_object('config.Config')
 if test_config: app.config.update(test_config)
 os.makedirs(app.instance_path,exist_ok=True); db.init_app(app);login_manager.init_app(app);csrf.init_app(app)
 from .routes import main,auth,participant,admin
 app.register_blueprint(main);app.register_blueprint(auth,url_prefix='/auth');app.register_blueprint(participant,url_prefix='/cabinet');app.register_blueprint(admin,url_prefix='/admin')
 with app.app_context():
  db.create_all()
  if not Status.query.first(): db.session.add_all([Status(name='Новая'),Status(name='Мероприятие назначено'),Status(name='Завершено')])
  if not Event.query.first(): db.session.add_all([Event(title='Форум цифровых решений',event_date=date.today()+timedelta(days=20),venue='Конференц-зал А',description='Цифровые продукты и сервисы'),Event(title='Веб-разработка 2027',event_date=date.today()+timedelta(days=35),venue='Зал инноваций',description='Современные веб-технологии')])
  db.session.commit()
  pw=os.getenv('ADMIN_PASSWORD'); login=os.getenv('ADMIN_LOGIN','admin')
  if pw and not User.query.filter_by(login=login).first():
   u=User(login=login,email=os.getenv('ADMIN_EMAIL','admin@example.test'),phone='+70000000000',role='admin');u.set_password(pw);db.session.add(u);db.session.commit()
 return app
