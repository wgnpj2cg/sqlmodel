import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask, request
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sentry_sdk.init(
    dsn="https://9d6fa06d07b34398b3f045c325672f04@o358176.ingest.sentry.io/5854384",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

PORT = os.getenv("PORT")
DBINFO = os.getenv("DBINFO")


app = Flask(__name__)
Base = declarative_base()


class SqlModel(Base):
    __tablename__ = 'sqlmodel'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    key = Column(String(200))
    value = Column(String(200))

    only_run_once_time = Column(Integer(), default=0)
    status = Column(Integer(), default=0)


engine = create_engine(DBINFO)

DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# set/
# get/
# clean/
@app.route('/set', methods=['POST'])
def set():
    if request.method == 'POST':
        key = request.form['key']
        value = request.form['value']
        if 'only_run_once_time' in request.form:
            obj = SqlModel(key=key, value=value, only_run_once_time=1)
        else:
            obj = SqlModel(key=key, value=value)
        session = DBSession()
        session.add(obj)
        session.commit()

        session.close()

    return {'code': 200}


@app.route('/get', methods=['POST'])
def get():
    if request.method == 'POST':
        key = request.form['key']
        session = DBSession()
        obj = session.query(SqlModel).filter(SqlModel.status == 0).filter(SqlModel.key == key).first()
        if obj:
            value = obj.value
            if obj.only_run_once_time == 0:
                session.close()
                return str(value)
            obj.status = 1
            session.commit()
            session.close()
            return str(value)
        else:
            session.close()
            return {'code': 400}


@app.route('/update_by_key_change_value', methods=['POST'])
def update():
    if request.method == 'POST':
        key = request.form['key']

        value = request.form['value']

        session = DBSession()
        objs = session.query(SqlModel).filter(SqlModel.key == key).all()
        if objs:
            for obj in objs:
                obj.value = value
                session.commit()
        session.close()
    return {'code': 200}


if __name__ == '__main__':
    app.run("0.0.0.0", PORT)
