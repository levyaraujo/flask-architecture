import traceback
from flask import Blueprint, make_response
from flask_restful import Api, Resource, reqparse
from extensions.models.tables import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import traceback


bp = Blueprint("api", __name__)
api = Api(bp)

request = reqparse.RequestParser()
request.add_argument("name", required=True, help="The field 'name' must be filled")
request.add_argument("email", required=True, help="The field 'email' must be filled")
request.add_argument(
    "password", required=True, help="The field 'password' must be filled"
)
request.add_argument("active", type=bool)


class UserRegister(Resource):
    def post(self):
        data = request.parse_args()
        user = UserModel(**data)
        user.active = False

        if user.find_email(data.email):
            return {"message": "this email is already registered."}
        try:
            user.save_user()
            user.send_confirmation_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return make_response({"error": "an internal server has occurred"}, 500)
        return make_response({"success": "User registered successfully"}, 201)

    def get(self, id):
        user = UserModel.find_user(id)
        if user:
            return user.json()
        return make_response({"message": "User not found"}, 404)

    def delete(self, id):
        user = UserModel.find_user(id)
        if user:
            user.delete_user()
            return make_response({"deleted": f"{user.name} deleted"})
        return make_response({"not_found": "user not found"}, 404)


class UserLogin(Resource):
    @staticmethod
    def post():
        request.remove_argument("name")
        data = request.parse_args()
        user = UserModel.find_email(data.email)
        pwd = data.password

        if user and (user.check_pwd(pwd)):
            if user.active:
                access_token = create_access_token(identity=user.name)
                return make_response({"logged_in": f"{access_token}"}, 200)
            return make_response({"message": "user not confirmed"}, 400)
        return {"message": "username or password is incorrect"}, 401

    @jwt_required()
    @staticmethod
    def get():
        current_user = get_jwt_identity()
        return make_response({"message": f"logged in as {current_user}"}, 200)


class UserConfirm(Resource):
    @classmethod
    def get(cls, id):
        user = UserModel.find_user(id)
        if not user:
            return make_response({"message": f"user id {id} not found "}, 404)
        user.active = True
        user.save_user()
        return make_response({"message": "your email is confirmed"})


def init_app(app):
    api.add_resource(
        UserRegister,
        "/register",
        "/delete/<int:id>",
        "/users/<int:id>",
    )
    api.add_resource(UserLogin, "/login", "/user")
    api.add_resource(UserConfirm, "/confirmacao/<int:id>")
    app.register_blueprint(bp)
