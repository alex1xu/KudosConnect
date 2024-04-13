from flask import Flask, request, jsonify, Blueprint,session
from . import db,ma
import json
from sqlalchemy import exc
from .models import ApplicationModel

application_routes = Blueprint('application', __name__)

class ApplicationSchema(ma.SQLAlchemySchema):
  class Meta:
    model=ApplicationModel
  id=ma.auto_field()
  status=ma.auto_field()
  create_datetime=ma.auto_field()
  update_datetime=ma.auto_field()

  listing_id=ma.auto_field()
  applicant_id=ma.auto_field()
  review_ids=ma.auto_field()

  description=ma.auto_field()

application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

@application_routes.route('/',methods=['POST'])
def add_application():
  try:
    if 'session' not in session:
      return jsonify({'message':'Unauthorized'}),401

    json_dict = json.loads(json.dumps(request.json))

    if 'applicant_id' not in json_dict or 'listing_id' not in json_dict:
      return {'message': 'Unknown Error'},500

    if len(json_dict['description'])<10 or len(json_dict['description'])>500:
      return {'message': 'Application must be between 10 and 500 characters'},400
    
    new_application = ApplicationModel(**json_dict)

    db.session.add(new_application)
    db.session.commit()

    return application_schema.jsonify(new_application),200
  except exc.SQLAlchemyError:
    db.session.rollback()
    return {'message': 'Unknown Error'},500

@application_routes.route('/', methods=['GET'])
def get_all_applications():
  try:
    all_applications = ApplicationModel.query.all()
    result = applications_schema.dump(all_applications)
    
    return jsonify(result),200
  except exc.SQLAlchemyError as e:
    return {'message':'Unknown Error'},500

@application_routes.route('/<id>', methods=['GET'])
def get_application(id):
  try:
    application = ApplicationModel.query.get(id)

    return application_schema.jsonify(application),200
  except exc.SQLAlchemyError as e:
    return {'message':'Unknown Error'},500

@application_routes.route('/listing/<id>', methods=['GET'])
def get_application_listing(id):
  try:
    applications = db.session.query(ApplicationModel).filter(ApplicationModel.listing_id==id)
    result = applications_schema.dump(applications)

    return jsonify(result),200
  except exc.SQLAlchemyError as e:
    return {'message':'Unknown Error'},500

@application_routes.route('/user/<id>', methods=['GET'])
def get_application_user(id):
  try:
    applications = db.session.query(ApplicationModel).filter(ApplicationModel.applicant_id==id)
    result = applications_schema.dump(applications)
    
    return jsonify(result),200
  except exc.SQLAlchemyError as e:
    return {'message':'Unknown Error'},500

@application_routes.route('/listing/user/<listing_id>/<applicant_id>', methods=['GET'])
def get_application_listing_user(listing_id,applicant_id):
  try:
    applications = db.session.query(ApplicationModel).filter(ApplicationModel.applicant_id==applicant_id).filter(ApplicationModel.listing_id==listing_id)
    result = applications_schema.dump(applications)
    
    return jsonify(result),200
  except exc.SQLAlchemyError as e:
    return {'message':'Unknown Error'},500

@application_routes.route('/<id>', methods=['PUT'])
def update_application(id):
  try:
    if 'session' not in session:
      return jsonify({'message':'Unauthorized'}),401

    application = ApplicationModel.query.get(id)
    json_dict = json.loads(json.dumps(request.json))

    for key in json_dict:
      setattr(application,key,json_dict[key])

    db.session.commit()
    return application_schema.jsonify(application),200
  except exc.SQLAlchemyError as e:
    return str(e.__dict__['orig'])

@application_routes.route('/<id>', methods=['DELETE'])
def delete_application(id):
  try:
    if 'session' not in session:
      return jsonify({'message':'Unauthorized'}),401

    application = ApplicationModel.query.get(id)
    db.session.delete(application)
    db.session.commit()

    return application_schema.jsonify(application),200
  except exc.SQLAlchemyError as e:
    return str(e.__dict__['orig'])