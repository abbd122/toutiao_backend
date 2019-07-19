import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))

from flask import jsonify


from . import create_app
from settings.default import DefaultConfig

# 功能分支

app = create_app(DefaultConfig, enable_config_file=True)

from utils.middlewares import jwt_authentication
app.before_request(jwt_authentication)


@app.route('/')
def route_map():
    """
    主视图，返回所有视图网址
    """
    rules_iterator = app.url_map.iter_rules()
    return jsonify({rule.endpoint: rule.rule for rule in rules_iterator if rule.endpoint not in ('route_map', 'static')})
