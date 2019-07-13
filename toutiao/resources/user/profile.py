from flask_restful import Resource,request
from flask_restful.reqparse import RequestParser
from flask import current_app,g

from utils.storage import upload_image
from utils.decorators import login_reqired
from utils.parser import image_file
from models.user import User
from models import db


class PhotoResource(Resource):
    '''
    修改图片数据
    '''
    # method_decorators = [login_reqired]

    def patch(self):
        user_id = g.user_id
        parser = RequestParser()
        parser.add_argument('photo', type=image_file, required=True, location='files')
        result = parser.parse_args()
        photo = result.get('photo')
        photo_data = photo.read()
        pic_name = upload_image(photo_data)

        try:
            user = User.query.get(user_id)
            user.profile_photo = pic_name
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return {'message': '数据库异常'}, 507
        full_path = current_app.config['QINIU_DOMAIN'] + pic_name
        return {'full_path': full_path}

