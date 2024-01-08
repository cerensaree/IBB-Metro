# -*- coding:utf-8 -*-
from flask import Flask, json, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
import redis
import os
import requests
import uuid

app = Flask(__name__)
api_v1_blueprint = Blueprint('api_v1', __name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",
                                                       "postgresql://metro:metrodb.12345@metro-db.metroprojecttest.svc.cluster.mantam/metro")
db = SQLAlchemy(app)

redis_cache = redis.StrictRedis(host=os.environ.get("REDISHOST", "metro-redis.metroprojecttest.svc.cluster.mantam"),
                                port=os.environ.get("REDIS_PORT", "6379"), db=os.environ.get("REDIS_DB_VALUE", "0"),
                                password=os.environ.get("REDIS_PSWRD", "metroapi"))

section_translate = {
    "YURUYEN MERDIVEN": "Yürüyen Merdiven",
    "ASANSOR": "Asansör"
}

state_translate = {
    "AsansörGenelArıza": "Asansör Genel Arıza",
    "MerdivenGenelArıza": "Merdiven Genel Arıza",
    "MerdivenAcilDurdurma": "Merdiven Acil Durdurma"
}


class Metro(db.Model):
    __tablename__ = 'tbl_metro'
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.String(255))
    station = db.Column(db.String(255))
    equipment = db.Column(db.String(255))
    section = db.Column(db.String(255))
    state = db.Column(db.String(255))
    starttime = db.Column(db.String(255))


def get_token():
    service_token_url = "https://apicore.metro.istanbul/Authentication/AccessToken"

    service_token_data = {
        "user": "CoreApiTokenUser",
        "password": "8x/A?D(G-KaPdSgVkYp3s6v9y$B&E)H@MbQeThWmZq4t7w!z%C*F-JaNdRfUjXn2r5u8x/A?D(G+KbPeShVkYp3s6v9y$B&E)H@McQfTjWnZq4t7w!z%C*F-JaNdRgUk",
        "deviceId": "0",
        "deviceModel": "0",
        "employeeId": "0",
        "employeeCode": "0",
        "memberId": "0",
        "userName": "0",
        "language": "0",
        "appCode": "CRMW",
        "companyId": "0",
        "from": 100
    }
    headers = {"Content-Type": "application/json", "Accept": "*/*", "Connection": "keep-alive"}
    response = requests.post(service_token_url, json=service_token_data, headers=headers)

    if response.status_code == 200:
        token_value = response.json().get("data", {}).get("token")
        return token_value
    else:
        return None


def authorize_request(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        token = authorization_header.split('Bearer ')[1].strip()

        user_info = redis_cache.get(token)

        if user_info:
            user_data = json.loads(user_info)
            return user_data

    return None


def authorized_endpoint(func):
    def wrapper(*args, **kwargs):
        user_data = authorize_request(request)
        if user_data:
            result = func(*args, **kwargs)
            # result_json = jsonify(result)
            return result
        else:
            return jsonify({"error": "Unauthorized"}), 401

    return wrapper


@api_v1_blueprint.route('/breakdown/list', methods=['GET'])
@authorized_endpoint
def get_data():
    try:
        cached_data = redis_cache.get('cache_data')
        if cached_data:
            return jsonify(json.loads(cached_data))
        cache_data = Metro.query.all()

        result = []

        for data in cache_data:
            line = data.line
            station = data.station
            equipment = data.equipment
            section = data.section
            state = data.state
            starttime = data.starttime

            line_info = next((item for item in result if item["line"] == line), None)

            if line_info is None:
                line_info = {
                    "line": line,
                    "stations": []
                }
                result.append(line_info)

            station_info = next((item for item in line_info["stations"] if item["name"] == station), None)

            if station_info is None:
                station_info = {
                    "name": station,
                    "equipments": []
                }
                line_info["stations"].append(station_info)

            equipment_info = {
                "name": equipment,
                "section": section,
                "state": state,
                "starttime": starttime
            }

            station_info["equipments"].append(equipment_info)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


@api_v1_blueprint.route('/section/translate', endpoint='section_translate', methods=['GET'])
@authorized_endpoint
def get_section_translate():
    try:
        cached_data = redis_cache.get('section_translate')
        if cached_data:
            return jsonify(json.loads(cached_data))

        cache_data = Metro.query.with_entities(Metro.section).group_by(Metro.section).all()

        result = []

        for data in cache_data:
            result.append({"key": data.section, "value": section_translate.get(data.section, data.section)})

        redis_cache.set('section_translate', json.dumps(result))

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


@api_v1_blueprint.route('/state/translate', endpoint='state_translate', methods=['GET'])
@authorized_endpoint
def get_state_translate():
    try:
        cached_data = redis_cache.get('state_translate')
        if cached_data:
            return jsonify(json.loads(cached_data))

        cache_data = Metro.query.with_entities(Metro.state).group_by(Metro.state).all()

        result = []

        for data in cache_data:
            result.append({"key": data.state, "value": state_translate.get(data.state, data.state)})

        redis_cache.set('state_translate', json.dumps(result))

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


@api_v1_blueprint.route('/login', endpoint='login', methods=['POST'])
def login_with_service_token():
    token = get_token()
    login_url = "https://apicore.metro.istanbul/Authentication/Login"

    login_Data = request.json

    if token is None:
        token = get_token()

    elif token is not None:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(login_url, json=login_Data, headers=headers)

        if response.status_code == 200:
            response_json = response.json()
            try:
                if not response_json.get("success", False):
                    return jsonify({"error": response_json.get("responseText", "Giriş Başarısız")}), 401
            except:
                return jsonify({"error": "Giriş Başarısız"}), 401
            data = response_json.get("data", {}).get("Employee", {})
            person_name = data.get("name")
            person_photo = data.get("photo")
            person_code = data.get("code")
            random_token = str(uuid.uuid4())
            data = {
                "token": random_token,
                "name": person_name,
                "code": person_code,
                "photo": person_photo
            }
            cache_token = redis_cache.set(random_token, json.dumps(data))
            return jsonify(data), 200
        else:
            return jsonify(
                {"error": "An error occured."}), response.status_code if response and response.status_code else 401
    else:
        return jsonify({"error": "Service Token is None"}), 401


@api_v1_blueprint.route('/logout', endpoint='logout', methods=['POST'])
def logout_with_service_token():
    try:
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split('Bearer ')[1].strip()
            if token:
                if redis_cache.exists(token):
                    redis_cache.delete(token)
                    return jsonify({"Message": "Session successfully terminated."}), 200
                else:
                    return jsonify({"Error": "Invalid session token."}), 401
            else:
                return jsonify({"Error": "Token missing"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}, 500)


@app.route('/api/v2/breakdown/list', methods=['GET'])
def get_data():
    try:
        cached_data = redis_cache.get('cache_data')
        if cached_data:
            return jsonify(json.loads(cached_data))
        cache_data = Metro.query.all()

        result = []

        for data in cache_data:
            line = data.line
            station = data.station
            equipment = data.equipment
            section = data.section
            state = data.state
            starttime = data.starttime

            line_info = next((item for item in result if item["line"] == line), None)

            if line_info is None:
                line_info = {
                    "line": line,
                    "stations": []
                }
                result.append(line_info)

            station_info = next((item for item in line_info["stations"] if item["name"] == station), None)

            if station_info is None:
                station_info = {
                    "name": station,
                    "equipments": []
                }
                line_info["stations"].append(station_info)

            equipment_info = {
                "name": equipment,
                "section": section,
                "state": state,
                "starttime": starttime
            }

            station_info["equipments"].append(equipment_info)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})


app.register_blueprint(api_v1_blueprint, url_prefix='/api/v1')
