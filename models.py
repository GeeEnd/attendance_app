# models.py
from bson.objectid import ObjectId
from bson.errors import InvalidId

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

class TeacherModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.teachers

    def create_teacher(self, full_name, username, password):
        hashed = generate_password_hash(password)
        return self.collection.insert_one({
            'full_name': full_name,
            'username': username,
            'password': hashed
        })

    def get_teacher_by_username(self, username):
        return self.collection.find_one({'username': username})

    def get_teacher_by_id(self, teacher_id):
        return self.collection.find_one({'_id': ObjectId(teacher_id)})

    def verify_password(self, teacher, password):
        return check_password_hash(teacher['password'], password)
    
    def get_teacher_by_full_name(self, full_name):
        return self.collection.find_one({'full_name': full_name})


class SectionModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.sections

    def create_section(self, course_code, code, time, units, room, day, teacher_id):
        return self.collection.insert_one({
            'course_code': course_code,
            'code': code,      # stored as 'code'
            'time': time,
            'units': units,
            'room': room,
            'day': day,
            'teacher_id': teacher_id
        })

    def get_sections_by_teacher(self, teacher_id):
        return list(self.collection.find({'teacher_id': teacher_id}))

    def get_section(self, identifier):
        """Fetch section by either ObjectId or section code (stored as 'code')"""
        try:
            obj_id = ObjectId(identifier)
            section = self.collection.find_one({'_id': obj_id})
            if section:
                return section
        except InvalidId:
            pass

        # Corrected: use 'code' instead of 'section_code'
        return self.collection.find_one({'code': identifier})
    def update_section(self, code, data):
        return self.mongo.db.sections.update_one({"code": code}, {"$set": data})

    def delete_section(self, code):
        return self.mongo.db.sections.delete_one({"code": code})


class StudentModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.students

    def add_student(self, name, section_code, face_encoding):
        """face_encoding is a list of floats from face_recognition.face_encodings"""
        return self.collection.insert_one({
            'name': name,
            'section_code': section_code,
            'face_encoding': face_encoding
        })

    def get_students_by_section(self, section_code):
        return list(self.collection.find({'section_code': section_code}))
    
    def get_student_by_id(self, student_id):
        from bson.objectid import ObjectId
        try:
            return self.collection.find_one({'_id': ObjectId(student_id)})
        except:
            return None


class AttendanceModel:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = mongo.db.attendance

    # Mark attendance (prevents duplicates)
    def mark_attendance(self, student_id, section_code, date_obj=None, present=True):
        if not date_obj:
            date_obj = date.today().isoformat()

        existing_record = self.collection.find_one({
            'student_id': student_id,
            'section_code': section_code,
            'date': date_obj
        })

        if existing_record:
            # Update existing record
            self.collection.update_one(
                {'_id': existing_record['_id']},
                {'$set': {'present': present}}
            )
            return existing_record['_id']

        # Insert new record
        return self.collection.insert_one({
            'student_id': student_id,
            'section_code': section_code,
            'date': date_obj,
            'present': present
        })

    # Get attendance by section and date
    def get_attendance_by_section_date(self, section_code, date_obj=None):
        if not date_obj:
            date_obj = date.today().isoformat()
        return list(self.collection.find({
            'section_code': section_code,
            'date': date_obj
        }))

    # Get all attendance for a section
    def get_all_attendance_for_section(self, section_code):
        return list(self.collection.find({
            'section_code': section_code
        }).sort('date', 1))

    # Get attendance for a student on a specific date
    def get_attendance_for_student_date(self, student_id, section_code, date_obj=None):
        if not date_obj:
            date_obj = date.today().isoformat()
        return self.collection.find_one({
            'student_id': student_id,
            'section_code': section_code,
            'date': date_obj
        })

    # Remove duplicates keeping latest
    def remove_duplicates(self):
        pipeline = [
            {
                "$group": {
                    "_id": {"student_id": "$student_id", "section_code": "$section_code", "date": "$date"},
                    "ids": {"$push": "$_id"},
                    "count": {"$sum": 1}
                }
            },
            {"$match": {"count": {"$gt": 1}}}
        ]
        duplicates = list(self.collection.aggregate(pipeline))
        for d in duplicates:
            ids = d["ids"]
            for _id in ids[:-1]:
                self.collection.delete_one({"_id": _id})