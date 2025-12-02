


# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_pymongo import PyMongo
# from io import BytesIO
# import pandas as pd
# import face_recognition
# from models import TeacherModel, SectionModel, StudentModel, AttendanceModel
# from bson.objectid import ObjectId
# from bson.errors import InvalidId
# from datetime import date
# import os

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # MongoDB config
# app.config["MONGO_URI"] = "mongodb://localhost:27017/attendance_app"
# mongo = PyMongo(app)

# # Models
# teacher_model = TeacherModel(mongo)
# section_model = SectionModel(mongo)
# student_model = StudentModel(mongo)
# attendance_model = AttendanceModel(mongo)

# # ---------- ROUTES ----------

# @app.route('/')
# def index():
#     return redirect(url_for('login'))

# # ----- REGISTER -----
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if teacher_model.get_teacher_by_username(username):
#             return "User already exists"
#         teacher_model.create_teacher(username, password)
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # ----- LOGIN -----
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         teacher = teacher_model.get_teacher_by_username(username)
#         if teacher and teacher_model.verify_password(teacher, password):
#             session['teacher_id'] = str(teacher['_id'])
#             return redirect(url_for('dashboard'))
#         return "Invalid credentials"
#     return render_template('login.html')

# # ----- DASHBOARD -----
# @app.route('/dashboard')
# def dashboard():
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))
#     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
#     sections = section_model.get_sections_by_teacher(session['teacher_id'])
#     return render_template('dashboard.html', teacher=teacher, sections=sections)

# # ----- ADD SECTION -----
# @app.route('/add_section', methods=['GET', 'POST'])
# def add_section():
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         code = request.form['code']
#         section_model.create_section(code, session['teacher_id'])
#         return redirect(url_for('dashboard'))
#     return render_template('add_section.html')

# # ----- VIEW SECTION / CAPTURE ATTENDANCE -----
# @app.route('/section/<section_identifier>', methods=['GET', 'POST'])
# def section(section_identifier):
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))

#     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     section_code = section['code']
#     students = student_model.get_students_by_section(section_code)

#     # Capture attendance via uploaded class photo
#     if request.method == 'POST' and 'class_photo' in request.files:
#         class_photo = request.files['class_photo']
#         image_bytes = class_photo.read()
#         class_image = face_recognition.load_image_file(BytesIO(image_bytes))
#         class_encodings = face_recognition.face_encodings(class_image)

#         for student in students:
#             present = any(face_recognition.compare_faces([student['face_encoding']], face)[0] 
#                           for face in class_encodings)
#             attendance_model.mark_attendance(student['_id'], section_code, present=present)

#         return redirect(url_for('section', section_identifier=section_identifier))

#     # Today's attendance
#     today_attendance = attendance_model.get_attendance_by_section_date(section_code)
#     attendance_ids = set([att['student_id'] for att in today_attendance])

#     return render_template('section.html',
#                            section=section,
#                            students=students,
#                            teacher=teacher,
#                            attendance_ids=attendance_ids)

# # ----- ADD SINGLE STUDENT -----
# @app.route('/section/<section_identifier>/add_student', methods=['POST'])
# def add_student(section_identifier):
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     name = request.form['student_name']
#     student_image = request.files['student_image']
#     if not student_image:
#         return "No image uploaded", 400

#     image_bytes = student_image.read()
#     image = face_recognition.load_image_file(BytesIO(image_bytes))
#     encodings = face_recognition.face_encodings(image)
#     if not encodings:
#         return "No face found in image", 400

#     student_model.add_student(name, section['code'], encodings[0].tolist())
#     return redirect(url_for('section', section_identifier=section_identifier))

# # ----- BULK IMPORT STUDENTS -----
# @app.route('/section/<section_identifier>/bulk_import', methods=['POST'])
# def bulk_import_section(section_identifier):
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     excel_file = request.files.get('excel')
#     if not excel_file:
#         return "No Excel file uploaded", 400

#     images_folder = request.form.get('images_folder')  # optional
#     df = pd.read_excel(excel_file)

#     for _, row in df.iterrows():
#         # Try uploaded file first
#         image_file = request.files.get(row['Image Name'])
#         if image_file:
#             image_bytes = image_file.read()
#             image = face_recognition.load_image_file(BytesIO(image_bytes))
#         # Try server folder
#         elif images_folder:
#             image_path = os.path.join(images_folder, row['Image Name'])
#             if not os.path.exists(image_path):
#                 continue
#             image = face_recognition.load_image_file(image_path)
#         else:
#             continue

#         encodings = face_recognition.face_encodings(image)
#         if encodings:
#             student_model.add_student(row['Name'], section['code'], encodings[0].tolist())

#     return redirect(url_for('section', section_identifier=section_identifier))

# # ----- LOGOUT -----
# @app.route('/logout')
# def logout():
#     session.pop('teacher_id', None)
#     return redirect(url_for('login'))

# # ----- RUN -----
# if __name__ == "__main__":
#     app.run(debug=True)


## VERSION 2 ----------------------------------------------------------------------------------------------------------------------
# from flask import Flask, render_template, request, redirect, url_for, session
# from flask_pymongo import PyMongo
# from io import BytesIO
# import pandas as pd
# import face_recognition
# from models import TeacherModel, SectionModel, StudentModel, AttendanceModel
# from bson.objectid import ObjectId
# from datetime import date
# import os
# from flask import render_template_string
# import zipfile

# app = Flask(__name__)
# app.secret_key = "supersecretkey"

# # MongoDB config
# app.config["MONGO_URI"] = "mongodb://localhost:27017/attendance_app"
# mongo = PyMongo(app)

# # Models
# teacher_model = TeacherModel(mongo)
# section_model = SectionModel(mongo)
# student_model = StudentModel(mongo)
# attendance_model = AttendanceModel(mongo)

# # ---------- ROUTES ----------

# @app.route('/')
# def index():
#     return redirect(url_for('login'))

# # ----- REGISTER -----
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if teacher_model.get_teacher_by_username(username):
#             return "User already exists"
#         teacher_model.create_teacher(username, password)
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # ----- LOGIN -----
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         teacher = teacher_model.get_teacher_by_username(username)
#         if teacher and teacher_model.verify_password(teacher, password):
#             session['teacher_id'] = str(teacher['_id'])
#             return redirect(url_for('dashboard'))
#         return "Invalid credentials"
#     return render_template('login.html')

# # ----- DASHBOARD -----
# @app.route('/dashboard')
# def dashboard():
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))
#     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
#     sections = section_model.get_sections_by_teacher(session['teacher_id'])
#     return render_template('dashboard.html', teacher=teacher, sections=sections)

# # ----- ADD SECTION -----
# @app.route('/add_section', methods=['GET', 'POST'])
# def add_section():
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         code = request.form['code']
#         section_model.create_section(code, session['teacher_id'])
#         return redirect(url_for('dashboard'))
#     return render_template('add_section.html')


# # ----- VIEW SECTION / CAPTURE ATTENDANCE (Group Photo Robust, No Duplicates) -----
# # @app.route('/section/<section_identifier>', methods=['GET', 'POST'])
# # def section(section_identifier):
# #     if 'teacher_id' not in session:
# #         return redirect(url_for('login'))

# #     # Get teacher and section
# #     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
# #     section = section_model.get_section(section_identifier)
# #     if not section:
# #         return "Section not found", 404

# #     section_code = section['code']
# #     students = student_model.get_students_by_section(section_code)

# #     # Capture attendance via uploaded group photo
# #     if request.method == 'POST' and 'class_photo' in request.files:
# #         class_photo = request.files['class_photo']
# #         image_bytes = class_photo.read()
# #         class_image = face_recognition.load_image_file(BytesIO(image_bytes))

# #         # Detect all faces in the group photo
# #         class_encodings = face_recognition.face_encodings(class_image)

# #         today = date.today().isoformat()

# #         # For each student, check if attendance already exists for today
# #         for student in students:
# #             existing = attendance_model.get_attendance_for_student_date(student['_id'], section_code, today)
# #             if existing:
# #                 continue  # skip if already marked

# #             # Default to absent
# #             present = False

# #             # Compare each detected face to this student
# #             for face_encoding in class_encodings:
# #                 matches = face_recognition.compare_faces(
# #                     [student['face_encoding']],
# #                     face_encoding,
# #                     tolerance=0.45
# #                 )
# #                 if matches[0]:
# #                     present = True
# #                     break  # stop checking other faces

# #             # Mark attendance
# #             attendance_model.mark_attendance(student['_id'], section_code, present=present, date_obj=today)

# #         return redirect(url_for('section', section_identifier=section_identifier))

# #     # Get today's attendance (only those marked present)
# #     today_attendance = attendance_model.get_attendance_by_section_date(section_code)
# #     attendance_ids = set([att['student_id'] for att in today_attendance if att.get('present')])

# #     return render_template(
# #         'section.html',
# #         section=section,
# #         students=students,
# #         teacher=teacher,
# #         attendance_ids=attendance_ids
# #     )

# # @app.route('/section/<section_identifier>', methods=['GET', 'POST'])
# # def section(section_identifier):
# #     if 'teacher_id' not in session:
# #         return redirect(url_for('login'))

# #     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
# #     section = section_model.get_section(section_identifier)
# #     if not section:
# #         return "Section not found", 404

# #     section_code = section['code']
# #     students = student_model.get_students_by_section(section_code)

# #     # Get all attendance records for the section
# #     all_attendance = attendance_model.get_all_attendance_for_section(section_code)

# #     # Capture attendance via uploaded group photo
# #     if request.method == 'POST' and 'class_photo' in request.files:
# #         class_photo = request.files['class_photo']
# #         image_bytes = class_photo.read()
# #         class_image = face_recognition.load_image_file(BytesIO(image_bytes))
# #         class_encodings = face_recognition.face_encodings(class_image)

# #         today = date.today().isoformat()

# #         # Mark attendance for each student
# #         for student in students:
# #             existing = attendance_model.get_attendance(student['_id'], section_code, today)
# #             if existing:
# #                 continue

# #             present = False
# #             for face_encoding in class_encodings:
# #                 matches = face_recognition.compare_faces([student['face_encoding']], face_encoding, tolerance=0.45)
# #                 if matches[0]:
# #                     present = True
# #                     break

# #             attendance_model.mark_attendance(student['_id'], section_code, present=present, date=today)

# #         return redirect(url_for('section', section_identifier=section_identifier))

# #     # Get today's attendance
# #     today_attendance = attendance_model.get_attendance_by_section_date(section_code)
# #     attendance_ids = set([att['student_id'] for att in today_attendance if att.get('present')])

# #     return render_template('section.html', section=section, students=students, teacher=teacher, 
# #                            attendance_ids=attendance_ids, all_attendance=all_attendance)

# @app.route('/section/<section_identifier>', methods=['GET', 'POST'])
# def section(section_identifier):
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))

#     teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     section_code = section['code']
#     students = student_model.get_students_by_section(section_code)

#     # Get all attendance records for the section
#     all_attendance = attendance_model.get_all_attendance_for_section(section_code)

#     # Capture attendance via uploaded group photo
#     if request.method == 'POST' and 'class_photo' in request.files:
#         class_photo = request.files['class_photo']
#         image_bytes = class_photo.read()
#         class_image = face_recognition.load_image_file(BytesIO(image_bytes))
#         class_encodings = face_recognition.face_encodings(class_image)

#         today = date.today().isoformat()

#         # Mark attendance for each student
#         for student in students:
#             existing = attendance_model.get_attendance(student['_id'], section_code, today)
#             if existing:
#                 continue

#             present = False
#             for face_encoding in class_encodings:
#                 matches = face_recognition.compare_faces([student['face_encoding']], face_encoding, tolerance=0.45)
#                 if matches[0]:
#                     present = True
#                     break

#             attendance_model.mark_attendance(student['_id'], section_code, present=present, date=today)

#         return redirect(url_for('section', section_identifier=section_identifier))

#     # Get all unique attendance dates
#     attendance_dates = sorted(list(set(att['date'] for att in all_attendance)))

#     # Organize attendance data by student
#     for student in students:
#          student['attendance'] = {att['date']: att['present'] for att in all_attendance if att['student_id'] == student['_id']}

#     return render_template(
#         'section.html', 
#         section=section, 
#         students=students, 
#         teacher=teacher, 
#         attendance_dates=attendance_dates,  # Pass dates to template
#         all_attendance=all_attendance
#     )

# # ----- ADD SINGLE STUDENT -----
# @app.route('/section/<section_identifier>/add_student', methods=['POST'])
# def add_student(section_identifier):
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     name = request.form['student_name']
#     student_image = request.files['student_image']
#     if not student_image:
#         return "No image uploaded", 400

#     image_bytes = student_image.read()
#     image = face_recognition.load_image_file(BytesIO(image_bytes))
#     encodings = face_recognition.face_encodings(image)
#     if not encodings:
#         return "No face found in image", 400

#     student_model.add_student(name, section['code'], encodings[0].tolist())
#     return redirect(url_for('section', section_identifier=section_identifier))

# # ----- BULK IMPORT STUDENTS (Excel + ZIP) -----
# @app.route('/section/<section_identifier>/bulk_import', methods=['POST'])
# def bulk_import_section(section_identifier):
#     if 'teacher_id' not in session:
#         return redirect(url_for('login'))

#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     excel_file = request.files.get('excel')
#     zip_file = request.files.get('images_zip')
#     if not excel_file or not zip_file:
#         return "Excel and ZIP files are required", 400

#     # Load Excel
#     df = pd.read_excel(excel_file)

#     # Extract ZIP in memory
#     zip_bytes = BytesIO(zip_file.read())
#     with zipfile.ZipFile(zip_bytes) as z:
#         zip_images = {name: z.read(name) for name in z.namelist()}

#     for _, row in df.iterrows():
#         student_name = row['Name']
#         image_name = row['Image Name']

#         if image_name not in zip_images:
#             print(f"Image {image_name} not found in ZIP, skipping {student_name}")
#             continue

#         # Load image and generate face encoding
#         image_bytes = BytesIO(zip_images[image_name])
#         image = face_recognition.load_image_file(image_bytes)
#         encodings = face_recognition.face_encodings(image)
#         if not encodings:
#             print(f"No face found in {image_name}, skipping {student_name}")
#             continue

#         student_model.add_student(student_name, section['code'], encodings[0].tolist())

#     return redirect(url_for('section', section_identifier=section_identifier))

# # ----- LOGOUT -----
# @app.route('/logout')
# def logout():
#     session.pop('teacher_id', None)
#     return redirect(url_for('login'))

# # ----------- PRINT -----------------
# @app.route('/section/<section_identifier>/print')
# def print_attendance(section_identifier):
#     section = section_model.get_section(section_identifier)
#     if not section:
#         return "Section not found", 404

#     students = student_model.get_students_by_section(section['code'])
#     all_attendance = attendance_model.get_all_attendance_for_section(section['code'])

#     # Get all unique dates
#     dates = sorted(list({att['date'] for att in all_attendance}))

#     # Build table rows
#     table_rows = ""
#     for student in students:
#         row = f"<tr><td>{student['name']}</td>"
#         total_f2f = 0
#         for d in dates:
#             att = next((a for a in all_attendance if a['student_id'] == student['_id'] and a['date'] == d), None)
#             if att and att.get('present'):
#                 row += "<td class='present'>✅</td>"
#                 total_f2f += 2.5
#             else:
#                 row += "<td class='absent'>❌</td>"
#         row += f"<td>{total_f2f}</td>"  # Total F2F (count of presents)
#         row += "<td>________</td><td>________</td><td>________</td>"  # Lab, Lecture, Total Attendance placeholders
#         row += "</tr>"
#         table_rows += row

#     # HTML template for printing
#     html = f"""
#     <html>
#       <head>
#         <title>Monthly Class Attendance</title>
#         <style>
#           @media print {{
#             @page {{ size: landscape; }}
#           }}
#           body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; color: #000; }}
#           h2, h3 {{ margin: 0; }}
#           .meta {{ margin-bottom: 20px; }}
#           table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
#           th, td {{ border: 1px solid #000; padding: 6px; text-align: center; }}
#           th {{ background-color: #f0f0f0; }}
#           td:first-child {{ text-align: left; font-weight: 500; }}
#           .present {{ color: green; font-weight: bold; }}
#           .absent {{ color: red; font-weight: bold; }}
#           .signature {{ margin-top: 40px; display: flex; justify-content: space-between; }}
#           .signature div {{ text-align: center; width: 45%; }}
#         </style>
#       </head>
#       <body>
#         <div class="meta">
#           <h2>College of Technologies – Information Technology Department</h2>
#           <h3>MONTHLY CLASS ATTENDANCE</h3>
#           <p><strong>Course Code:</strong> {section.get('course_code','IT4')} &nbsp;&nbsp; 
#              <strong>Section Code:</strong> {section['code']}</p>
#         </div>

#         <table>
#           <thead>
#             <tr>
#               <th rowspan="2">Name of Students</th>
#               <th colspan="{len(dates)}">Face-to-Face Classes</th>
#               <th rowspan="2">Total F2F (hrs)</th>
#               <th rowspan="2">Lab (hrs)</th>
#               <th rowspan="2">Lecture (hrs)</th>
#               <th rowspan="2">Total Attendance (hrs)</th>
#             </tr>
#             <tr>
#               {''.join(f'<th>{d}</th>' for d in dates)}
#             </tr>
#           </thead>
#           <tbody>
#             {table_rows}
#           </tbody>
#         </table>

#         <div style="margin-top: 40px;">
#           <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
#             <tr>
#               <td style="padding: 6px;"><strong>Total Face-to-Face Classes (in hours):</strong> __________</td>
#               <td style="padding: 6px;"><strong>Total Synchronous/Asynchronous Classes (in hours):</strong> __________</td>
#             </tr>
#             <tr>
#               <td style="padding: 6px;"><strong>Total Laboratory Classes (in hours):</strong> __________</td>
#               <td style="padding: 6px;"><strong>Total Attendance (in hours):</strong> __________</td>
#             </tr>
#             <tr>
#               <td colspan="2" style="padding: 6px;"><strong>Percentage of Class Hours Attended:</strong> __________%</td>
#             </tr>
#           </table>

#           <p style="margin-top: 20px;"><strong>Inclusive of the following:</strong></p>
#           <ol style="margin-left: 20px;">
#             <li>Orientation/Consultation</li>
#             <li>Face-to-Face Lecture</li>
#             <li>Synchronous/Asynchronous Lecture</li>
#             <li>Laboratory (Face-to-Face/Synchronous/Asynchronous)</li>
#           </ol>

#           <div class="signature">
#             <div>
#               <p>Prepared by:</p><br><br>
#               <p>__________________________</p>
#               <p>Instructor</p>
#             </div>
#             <div>
#               <p>Document Code: QF-ITAA-01/SOPAA</p>
#               <p>Revision no.: 01</p>
#               <p>Issue Date: January 27, 2023</p>
#               <p>Page: 1 of 1</p>
#             </div>
#           </div>
#         </div>

#       </body>
#     </html>
#     """
#     return html


# # ----- RUN -----
# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session,request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from authlib.integrations.flask_client import OAuth
import base64
from io import BytesIO
import pandas as pd
import numpy as np
import cv2
import face_recognition
from models import TeacherModel, SectionModel, StudentModel, AttendanceModel
from datetime import date
import zipfile
import os
from PIL import Image
from datetime import datetime


# ---------- APP CONFIG ----------
# app = Flask(__name__)
# app.secret_key = "supersecretkey"
# app.config["MONGO_URI"] = "mongodb://localhost:27017/attendance_app"
# mongo = PyMongo(app)
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# MongoDB URI
app.config["MONGO_URI"] = os.getenv(
    "MONGO_URI",
    "mongodb+srv://geeen:test1234@cluster0.q5frxuy.mongodb.net/attendance_app?retryWrites=true&w=majority"
)
mongo = PyMongo(app)


oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',  # Google user info
    client_kwargs={'scope': 'openid email profile'},
)

# Models
teacher_model = TeacherModel(mongo)
section_model = SectionModel(mongo)
student_model = StudentModel(mongo)
attendance_model = AttendanceModel(mongo)

# Cache for student encodings (avoid DB hits)
ENCODING_CACHE = {}

def get_cached_encodings(section_code):
    """Retrieve and cache student encodings for faster matching"""
    if section_code not in ENCODING_CACHE:
        students = student_model.get_students_by_section(section_code)
        ENCODING_CACHE[section_code] = [
            (s['_id'], np.array(s['face_encoding'])) for s in students if 'face_encoding' in s
        ]
    return ENCODING_CACHE[section_code]

# ---------- ROUTES ----------

@app.route('/')
def index():
    return redirect(url_for('login'))

# ----- REGISTER -----
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        password = request.form['password']

        # Check if a teacher with the same full name OR username exists
        existing_teacher = teacher_model.get_teacher_by_username(username)
        if existing_teacher or teacher_model.get_teacher_by_full_name(full_name):
            error = "Username or full name already exists"
        else:
            teacher_model.create_teacher(full_name, username, password)
            # Redirect to login with success message
            return redirect(url_for('login', success='Registration successful! You can now login.'))

    return render_template('register.html', error=error)



# ----- LOGIN -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    success = request.args.get('success')  # capture success message from URL
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        teacher = teacher_model.get_teacher_by_username(username)
        if teacher and teacher_model.verify_password(teacher, password):
            session['teacher_id'] = str(teacher['_id'])
            return redirect(url_for('dashboard'))
        error = "Invalid credentials"
    return render_template('login.html', error=error, success=success)

# Redirect user to Google login
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

# Callback after Google login
@app.route('/login/google/callback')
def authorize_google():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()

    # Example: find or create teacher
    teacher = teacher_model.get_teacher_by_full_name(user_info['name'])
    if not teacher:
        # create new teacher
        teacher_model.create_teacher(
            full_name=user_info['name'],
            username=user_info['email'],
            password=''  # no password needed for Google login
        )
        teacher = teacher_model.get_teacher_by_full_name(user_info['name'])

    # Login teacher
    session['teacher_id'] = str(teacher['_id'])
    return redirect(url_for('dashboard'))

# ----- DASHBOARD and ADD SECTION -----
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    teacher = teacher_model.get_teacher_by_id(session['teacher_id'])

    # Handle add section form
    if request.method == 'POST':
        course_code = request.form['course_code']
        code = request.form['code']              # use 'code'
        time = request.form['time']
        units = request.form['units']
        room = request.form['room']
        day = request.form['day']

        # Ensure 'code' is unique for this teacher
        existing = section_model.get_section(code)
        if existing:
            return "Section code already exists", 400

        section_model.create_section(course_code, code, time, units, room, day, session['teacher_id'])
        return redirect(url_for('dashboard'))

    sections = section_model.get_sections_by_teacher(session['teacher_id'])
    return render_template('dashboard.html', teacher=teacher, sections=sections)


# ----- SECTION: Capture Attendance -----
@app.route('/section/<section_identifier>', methods=['GET', 'POST'])
def section(section_identifier):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    teacher = teacher_model.get_teacher_by_id(session['teacher_id'])
    section = section_model.get_section(section_identifier)  # looks for code
    if not section:
        return "Section not found", 404

    code = section['code']  # consistent
    students = student_model.get_students_by_section(code)
    all_attendance = attendance_model.get_all_attendance_for_section(code)
    today = date.today().isoformat()

    # Capture attendance via uploaded class photo
    if request.method == 'POST' and 'class_photo' in request.files:
        class_photo = request.files['class_photo']
        image_bytes = np.frombuffer(class_photo.read(), np.uint8)
        cv_image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        small_img = cv2.resize(cv_image, (0, 0), fx=0.25, fy=0.25)
        rgb_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

        class_encodings = face_recognition.face_encodings(rgb_img)
        cached_students = get_cached_encodings(code)
        if not cached_students:
            return "No student encodings found", 400

        known_ids, known_encodings = zip(*cached_students)
        known_encodings = np.array(known_encodings)

        for face_encoding in class_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match = np.argmin(distances)
            if distances[best_match] < 0.45:
                matched_id = known_ids[best_match]
                attendance_model.mark_attendance(matched_id, code, present=True, date_obj=today)

        return redirect(url_for('section', section_identifier=section_identifier))

    # Prepare attendance data
    attendance_dates = sorted({att['date'] for att in all_attendance})
    for student in students:
        student['attendance'] = {att['date']: att['present'] for att in all_attendance if att['student_id'] == student['_id']}

    return render_template(
        'section.html',
        section=section,
        students=students,
        teacher=teacher,
        attendance_dates=attendance_dates,
        all_attendance=all_attendance
    )


# ----- ADD STUDENT -----
@app.route('/section/<section_identifier>/add_student', methods=['POST'])
def add_student(section_identifier):
    section = section_model.get_section(section_identifier)
    if not section:
        return "Section not found", 404

    name = request.form['student_name']
    student_image = request.files['student_image']
    if not student_image:
        return "No image uploaded", 400

    image_bytes = np.frombuffer(student_image.read(), np.uint8)
    cv_image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

    encodings = face_recognition.face_encodings(rgb_image)
    if not encodings:
        return "No face found in image", 400

    student_model.add_student(name, section['code'], encodings[0].tolist())

    # Clear cache for this section so new student is included
    if section['code'] in ENCODING_CACHE:
        del ENCODING_CACHE[section['code']]

    return redirect(url_for('section', section_identifier=section_identifier))


# ----- BULK IMPORT STUDENTS (Excel + ZIP) -----
@app.route('/section/<section_identifier>/bulk_import', methods=['POST'])
def bulk_import_section(section_identifier):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    section = section_model.get_section(section_identifier)
    if not section:
        return "Section not found", 404

    excel_file = request.files.get('excel')
    zip_file = request.files.get('images_zip')
    if not excel_file or not zip_file:
        return "Excel and ZIP files are required", 400

    df = pd.read_excel(excel_file)

    # Extract ZIP images in memory
    zip_bytes = BytesIO(zip_file.read())
    with zipfile.ZipFile(zip_bytes) as z:
        zip_images = {name: z.read(name) for name in z.namelist()}

    for _, row in df.iterrows():
        student_name = row['Name']
        image_name = row['Image Name']

        if image_name not in zip_images:
            print(f"Image {image_name} not found, skipping {student_name}")
            continue

        file_bytes = np.frombuffer(zip_images[image_name], np.uint8)
        cv_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        encodings = face_recognition.face_encodings(rgb_image)
        if not encodings:
            print(f"No face found in {image_name}, skipping {student_name}")
            continue

        student_model.add_student(student_name, section['code'], encodings[0].tolist())

    # Clear cache for section (refresh on next use)
    if section['code'] in ENCODING_CACHE:
        del ENCODING_CACHE[section['code']]

    return redirect(url_for('section', section_identifier=section_identifier))

@app.route('/section/<section_identifier>/live_mark', methods=['POST'])
def live_mark_attendance(section_identifier):
    if 'teacher_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    section = section_model.get_section(section_identifier)
    if not section:
        return jsonify({"error": "Section not found"}), 404

    data = request.get_json()
    image_data = data['image'].split(',')[1]
    image_bytes = base64.b64decode(image_data)
    pil_img = Image.open(BytesIO(image_bytes))
    frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # Resize for speed
    small_frame = cv2.resize(frame, (0,0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_encodings = face_recognition.face_encodings(rgb_small)
    cached_students = get_cached_encodings(section['code'])
    if not cached_students:
        return jsonify({"error": "No students in section"}), 400

    known_ids, known_encodings = zip(*cached_students)
    known_encodings = np.array(known_encodings)

    marked_students = []
    today = date.today().isoformat()

    for face_encoding in face_encodings:
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match = np.argmin(distances)
        if distances[best_match] < 0.45:
            student_id = known_ids[best_match]
            # ✅ Skip if already marked present
            record = attendance_model.get_attendance_for_student_date(student_id, section['code'], today)
            if record and record['present']:
                continue
            attendance_model.mark_attendance(student_id, section['code'], present=True, date_obj=today)
            student = student_model.get_student_by_id(student_id)
            marked_students.append(student['name'])

    return jsonify({"marked_students": list(set(marked_students))})

# ----- PRINT ATTENDANCE -----
@app.route('/section/<section_identifier>/print')
def print_attendance(section_identifier):
    section = section_model.get_section(section_identifier)
    if not section:
        return "Section not found", 404

    teacher = teacher_model.get_teacher_by_id(section['teacher_id'])
    students = student_model.get_students_by_section(section['code'])
    all_attendance = attendance_model.get_all_attendance_for_section(section['code'])

    dates = sorted(list({att['date'] for att in all_attendance}))
    table_rows = ""

    # Build table rows
    for i, student in enumerate(students, start=1):
        row = f"<tr><td>{i}</td><td>{student['name']}</td>"
        for d in dates:
            att = next((a for a in all_attendance if a['student_id'] == student['_id'] and a['date'] == d), None)
            row += "<td>✅</td>" if att and att.get('present') else "<td>❌</td>"
        # Add empty cells for synchronous/asynchronous
        row += "<td></td><td></td><td></td>"
        row += "</tr>"
        table_rows += row

    html = f"""
      <html>
      <head>
        <title>Monthly Class Attendance</title>
        <style>
          @media print {{
            @page {{ size: landscape; margin: 20mm; }}
          }}
          body {{
            font-family: 'Calibri', sans-serif;
            margin: 20px;
            color: #333;
          }}
          .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            line-height: 1.2;
            margin-bottom: 20px;
          }}
          .header img {{
            width: 80px;
          }}
          .school-info {{
            text-align: center;
            flex: 1;
          }}
          .school-title {{
            font-weight: bold;
            font-size: 18px;
          }}
          .subtitle {{
            font-size: 13px;
          }}
          .generated {{
            font-size: 11px;
            text-align: right;
            margin-top: -15px;
            margin-bottom: 5px;
            font-style: italic;
          }}
          h3 {{
            text-align: center;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 16px;
            text-decoration: underline;
          }}
          .section-info table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
            font-size: 12px;
          }}
          .section-info td {{
            padding: 3px 6px;
          }}
          table.attendance {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 12px;
          }}
          table.attendance th, table.attendance td {{
            border: 1px solid #000;
            padding: 4px;
            text-align: center;
          }}
          table.attendance th {{
            background-color: #f0f0f0;
          }}
          table.attendance tr:nth-child(even) {{
            background-color: #fafafa;
          }}
          .footer {{
            margin-top: 30px;
            font-size: 12px;
          }}
          .footer p {{
            margin: 3px 0;
          }}
          .prepared {{
            margin-top: 20px;
          }}
        </style>
        <script>
          window.onload = function() {{
            setTimeout(() => {{
              window.print();
              window.onafterprint = () => window.close();
            }}, 500);
          }};
        </script>
      </head>
      <body>

        <!-- Header -->
        <div class="header">
          <img src="/static/bsu_logo.png" alt="BukSU Logo" />
          <div class="school-info">
            <div class="school-title">BUKIDNON STATE UNIVERSITY</div>
            <div class="subtitle">Malaybalay City, Bukidnon 8700</div>
            <div class="subtitle">Tel (088) 813-5661 loc 362 | www.buksu.edu.ph</div>
            <br>
            <div><strong>College of Technologies – Information Technology Department</strong></div>
            
          </div>
          <div class="generated">
            Generated by: {teacher['full_name']}<br>
            Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}
          </div>
        </div>

        <h3>MONTHLY CLASS ATTENDANCE</h3>

        <!-- Section Info -->
        <div class="section-info">
          <table style="border:none;">
            <tr><td><b>Course Code:</b> {section['course_code']}</td><td><b>Day:</b> {section['day']}</td></tr>
            <tr><td><b>Section Code:</b> {section['code']}</td><td><b>Units:</b> {section['units']}</td></tr>
            <tr><td><b>Time:</b> {section['time']}</td><td><b>Room No./G-Class Code:</b> {section['room']}</td></tr>
            <tr><td><b>Course Title:</b> Advanced Database Systems</td><td></td></tr>
          </table>
        </div>

        <!-- Attendance Table -->
        <table class="attendance">
          <thead>
            <tr>
              <th rowspan="2">No.</th>
              <th rowspan="2">Name of Students</th>
              <th colspan="{len(dates)}">Face-to-Face Classes (75%)</th>
              <th colspan="3">Synchronous/Asynchronous Classes (25%)</th>
            </tr>
            <tr>
              {''.join(f'<th>{d}</th>' for d in dates)}
              <th>Date</th><th>Date</th><th>Date</th>
            </tr>
          </thead>
          <tbody>
            {table_rows}
          </tbody>
        </table>

        <!-- Footer -->
        <div class="footer">
          <p><b>Total Face-to-Face Classes (in hours):</b> __________</p>
          <p><b>Total Synchronous/Asynchronous Classes (in hours):</b> __________</p>
          <p><b>Total Laboratory Classes (in hours):</b> __________</p>
          <p><b>Total Number of Class Hours:</b> __________</p>

          <div class="prepared">
            <p><b>Prepared by:</b></p>
            <p style="margin-left:50px;">{teacher['full_name'].upper()}</p>
            <p style="margin-left:50px;"><i>Instructor (signature over printed name)</i></p>
          </div>

          <br>
          <p style="font-size:11px;"><b>*Inclusive of the following:</b> Orientation, Quizzes, Consultation, and other activities.</p>
        </div>

      </body>
      </html>
      """
    return html


@app.route('/sections/create', methods=['POST'])
def create_section():
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    course_code = request.form['course_code']
    code = request.form['code']
    time = request.form['time']
    units = request.form['units']
    room = request.form['room']
    day = request.form['day']

    existing = section_model.get_section(code)
    if existing:
        return "Section code already exists", 400

    section_model.create_section(course_code, code, time, units, room, day, session['teacher_id'])
    return redirect(url_for('dashboard'))

# ----- LOGOUT -----
@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect(url_for('login'))

# ----- EDIT SECTION -----
@app.route('/sections/<code>/edit', methods=['POST'])
def edit_section(code):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    data = {
        "course_code": request.form.get("course_code"),
        "code": request.form.get("new_code"),
        "time": request.form.get("time"),
        "units": request.form.get("units"),
        "room": request.form.get("room"),
        "day": request.form.get("day"),
    }

    # remove empty fields
    data = {k: v for k, v in data.items() if v}

    section_model.update_section(code, data)

    return redirect(url_for('dashboard'))




# ----- DELETE SECTION -----
@app.route('/sections/<code>/delete', methods=['POST'])
def delete_section(code):
    if 'teacher_id' not in session:
        return redirect(url_for('login'))

    result = section_model.delete_section(code)

    if result.deleted_count == 0:
        return "Section not found", 404

    return redirect(url_for('dashboard'))


# # ---------- RUN ----------
# if __name__ == "__main__":
#     app.run(debug=True)

# ---------- RUN ----------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    # Get port from Render environment variable (default 5000 locally)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)