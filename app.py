from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from werkzeug.exceptions import HTTPException
import json

#creating validation errors 
class APIValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = json.dumps(message), status_code


#creating reqparser for student
create_student_parser = reqparse.RequestParser()
create_student_parser.add_argument('roll_number')
create_student_parser.add_argument('first_name')
create_student_parser.add_argument('last_name')


# configuring Flask app
app = Flask(__name__)

# configuring flask to use sql alchemy and url for databse
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_database.sqlite3"
db = SQLAlchemy(app)
api = Api(app)

# student model
class student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))

# course model
class course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(255), nullable=False, unique=True)
    course_name = db.Column(db.String(255), nullable=False)
    course_description = db.Column(db.String(255))

#enrollments model
class enrollment(db.Model):
    __tablename__ = "enrollment"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey(student.student_id), nullable=False
    )
    course_id = db.Column(db.Integer, db.ForeignKey(course.course_id), nullable=False)

class StudentApi(Resource):
    def get(self, student_id):
        #getting student from database
        # if valid, return student data, else return 404 error
        try:
            studentQueried = db.session.query(student).filter(student.student_id == student_id).first()
        except:
            return '', 500
        if studentQueried:
            return{
                "student_id": studentQueried.student_id,
                "first_name": studentQueried.first_name,
                "last_name": studentQueried.last_name,
                "roll_number": studentQueried.roll_number
            }, 200
        else:
            return '', 404
    
    def put(self, student_id):
        #implementing put method
        #putting student information 
        #initializing student parser 
        args = create_student_parser.parse_args()
        roll_number = args.get("roll_number", None)
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)

        if roll_number is None:
            raise APIValidationError(status_code=400, error_code = "STUDENT001", error_message = "Roll Number required and should be String")

        if first_name is None:
            raise APIValidationError(status_code=400, error_code = "STUDENT002", error_message = "First Name is required and should be String")

        if last_name is None:
            raise APIValidationError(status_code=400, error_code = "STUDENT003", error_message = "Last Name is String")

        stud1 = db.session.query(student).filter(student.student_id == student_id).first()

        if not stud1:
            return '', 500

        stud1.first_name = first_name
        stud1.last_name = last_name
        stud1.roll_number = roll_number
        db.session.add(stud1)
        db.session.commit()
        
        return "", 201

    def delete(self, student_id):
        # if enrollments are there for this student, deleting student and enrollments
        #first checking if student exists in database
        stud = db.session.query(student).filter(student.student_id == student_id).first()

        if not stud:
            return '', 404

        enrolled = db.session.query(enrollment).filter(enrollment.student_id == student_id).all()
        #first deleting all enrollments
        try:
            for enrolls in enrolled:
                db.session.delete(enrolls)
                db.session.commit()
        except:
            return '', 500

        try:
            db.session.delete(stud)
            #deleting student
        except:
            return '', 500

        db.session.commit()
        return '', 200

    def post(self):

        #implementing post method 
        #posting student information 
        #initializing student parser 
        args = create_student_parser.parse_args()
        roll_number = args.get("roll_number", None)
        first_name = args.get("first_name", None)
        last_name = args.get("last_name", None)

        if roll_number is None:
            raise APIValidationError(status_code=400, error_code = "STUDENT001", error_message = "Roll Number required and should be String")

        if first_name is None:
            raise APIValidationError(status_code=400, error_code = "STUDENT002", error_message = "First Name is required and should be String")

        if not isinstance(last_name, str):
            raise APIValidationError(status_code=400, error_code = "STUDENT003", error_message = "Last Name is String")

        stud = db.session.query(student).filter(student.roll_number == roll_number).first()

        if stud:
            raise APIValidationError(status_code=409, error_code="STUDENT004", error_message="Roll number must be unique.")

        try:
            new_student = student(roll_number=roll_number, first_name=first_name,last_name=last_name)
        except:
            return '',500

        db.session.add(new_student)
        db.session.commit()
        
        return "", 200

api.add_resource(StudentApi, '/api/student', '/api/student/<string:student_id>')


#creating reqparser for course
create_course_parser = reqparse.RequestParser()
create_course_parser.add_argument('course_name')
create_course_parser.add_argument('course_code')
create_course_parser.add_argument('course_description')

#class for courses
class CourseApi(Resource):
    def get(self, course_id):
        #getting course from database
        # if valid, return course data, else return 404 error
        try:
            qCourse = db.session.query(course).filter(course.course_id == course_id).first()
        except:
            return '', 500
        if qCourse:
            return{
                "course_id": qCourse.course_id,
                "course_code": qCourse.course_code,
                "course_name": qCourse.course_name,
                "course_description": qCourse.course_description
            }, 200
        else:
            return '', 404
    

    def post(self):
        #implementing post method 
        #posting course information 
        #initializing course parser 
        args = create_course_parser.parse_args()
        course_code = args.get("course_code", None)
        course_name = args.get("course_name", None)
        course_description = args.get("course_description", None)

        if course_name is None:
            raise APIValidationError(status_code=400, error_code = "COURSE001", error_message = "Course Name is required and should be string.")

        if course_code is None:
            raise APIValidationError(status_code=400, error_code = "COURSE002", error_message = "Course Code is required and should be string.")

        if not isinstance(course_description, str):
            raise APIValidationError(status_code=400, error_code = "COURSE003", error_message = "Course Description should be string.")

        qCourse = db.session.query(course).filter(course.course_code == course_code).first()

        if qCourse:
            raise APIValidationError(status_code=409, error_code="COURSE004", error_message="Course code must be unique.")

        new_course = course(course_code=course_code, course_description=course_description, course_name = course_name)
        db.session.add(new_course)
        db.session.commit()
        
        return "", 201


    def put(self, course_id):
        #implementing put method
        #posting course information 
        #initializing course parser 
        args = create_course_parser.parse_args()
        course_code = args.get("course_code", None)
        course_name = args.get("course_name", None)
        course_description = args.get("course_description", None)
        
        if course_name is None:
            raise APIValidationError(status_code=400, error_code = "COURSE001", error_message = "Course Name is required and should be string.")

        if course_code is None:
            raise APIValidationError(status_code=400, error_code = "COURSE002", error_message = "Course Code is required and should be string.")

        if not isinstance(course_description, str):
            raise APIValidationError(status_code=400, error_code = "COURSE003", error_message = "Course Description should be string.")

        qCourse = db.session.query(course).filter(course.course_id == course_id).first()

        if not qCourse:
            return '', 500

        qCourse.course_name = course_name
        qCourse.course_code = course_code
        qCourse.course_description = course_description
        db.session.add(qCourse)
        db.session.commit()
        
        return "", 201

    def delete(self, course_id):
        # if enrollments are there for this course, deleting course and enrollments
        #first checking if course exists in database
        qCourse = db.session.query(course).filter(course.course_id == course_id).first()

        if not qCourse:
            return '', 404

        enrolled = db.session.query(enrollment).filter(enrollment.student_id == course_id).all()
        #first deleting all enrollments
        try:
            for enrolls in enrolled:
                db.session.delete(enrolls)
                db.session.commit()
        except:
            return '', 500

        try:
            db.session.delete(qCourse)
            #deleting student
        except:
            return '', 500

        db.session.commit()
        return 200

api.add_resource(CourseApi, '/api/course', '/api/course/<string:course_id>')


#creating reqparser for enrollments
create_enroll_parser = reqparse.RequestParser()
create_enroll_parser.add_argument('course_id')

#class for enrollments
class EnrollmentAPI(Resource):
    
    def get(self, student_id):
        #implementing get method for student enrollments
        #check for student enrollments and return a list of enrollments

        try:
            enrolled = db.session.query(enrollment).filter(enrollment.student_id == student_id).all()
        except:
            return '', 500

        if enrolled:
            enrolls = []
            #will hold all enrollments

            for enroll in enrolled:
                enrolls.append(
                    {
                        "enrollment_id":enroll.enrollment_id,
                        "student_id":enrollment.student_id,
                        "course_id":enrollment.course_id
                    }
                )
            
            return enrolls, 200
        
        else:
            return '', 404


    def post(self, student_id):
        #implementing post method for student enrollments
        #checking for errors first, then uploading to database

        args = create_enroll_parser.parse_args()
        course_id = args.get("course_id", None)

        if not course_id or not isinstance(course_id,str):
            raise APIValidationError(status_code=400, error_code = "ENROLLMENT003", error_message="Course code is required and should be string.")

        courseCheck = db.session.query(course).filter(course.course_id == course_id).first()

        if not courseCheck:
            raise APIValidationError(status_code=400, error_code = "ENROLLMENT001", error_message="Course does not exist")

        studentCheck = db.session.query(student).filter(student.student_id == student_id).first()

        if not studentCheck:
            raise APIValidationError(status_code=400, error_code = "ENROLLMENT002", error_message="Student does not exist.")

        try:
            new_enrollment = enrollment(student_id = student_id, course_id = course_id)
            db.session.add(new_enrollment)
            db.session.commit()
        except:
            return '', 500

        return '', 201


    def delete(self, student_id, course_id):
        #checking if student id and course id are valid 
        #checking if enrollment is found in database
        #if enrollment is in database, deleting

        courseCheck = db.session.query(course).filter(course.course_id == course_id).first()

        if not courseCheck:
            raise APIValidationError(status_code=400, error_code = "ENROLLMENT001", error_message="Course does not exist")

        studentCheck = db.session.query(student).filter(student.student_id == student_id).first()

        if not studentCheck:
            raise APIValidationError(status_code=400, error_code = "ENROLLMENT002", error_message="Student does not exist.")

        enrollmentCheck = db.session.query(enrollment).filter(enrollment.student_id == student_id, enrollment.course_id ==course_id).first()

        if not enrollmentCheck:
            return '', 404

        try:
            db.session.delete(enrollmentCheck)
            db.session.commit()
        except: 
            return '', 500

        return '',200


api.add_resource(EnrollmentAPI, '/api/student/<string:student_id>/course/<string:course_id>', '/api/student/<string:student_id>/course')

if __name__ == '__main__':
    app.run()