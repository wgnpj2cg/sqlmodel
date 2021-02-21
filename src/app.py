import os
from flask import Flask, request
from sqlalchemy import Column, String, create_engine, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

PORT = os.getenv("PORT")
DBINFO = os.getenv("DBINFO")

app = Flask(__name__)
Base = declarative_base()


class SqlModel(Base):
    __tablename__ = 'sqlmodel'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    key = Column(String(200))
    value = Column(String(200))

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

        obj = SqlModel(key=key, value=value)
        session = DBSession()
        session.add(obj)
        session.commit()

        session.close()

    return "{'code':200}"


@app.route('/get', methods=['POST'])
def get():
    if request.method == 'POST':
        key = request.form['key']
        session = DBSession()
        obj = session.query(SqlModel).filter(SqlModel.status == 0).filter(SqlModel.key == key).first()
        if obj:
            value = obj.value
            obj.status = 1
            session.commit()
            session.close()
            return str(value)
        else:
            session.close()
            return "{'code':400}"


if __name__ == '__main__':
    app.run("0.0.0.0", PORT)
