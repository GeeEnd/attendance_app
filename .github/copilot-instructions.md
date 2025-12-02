# AI Copilot Instructions for ATM2 (Face Recognition Attendance System)

## Project Overview

This is a **Flask-based face recognition attendance tracking system** for university instructors. Teachers register, create course sections, enroll students with facial images, and mark attendance via group class photos. The system stores facial encodings (not images) in MongoDB for privacy and performs real-time face matching.

**Key Stack:** Flask, MongoDB, PyMongo, face_recognition, OpenCV, Pandas, Tailwind CSS

## Architecture & Data Flow

### Core Entity Relationships
- **Teachers** → **Sections** → **Students** → **Attendance Records**
  - Each teacher manages multiple sections (courses)
  - Each section contains multiple students with face encodings
  - Attendance is marked per student per section per date

### Critical Data Model Pattern
In `models.py`, all models follow the same structure:
1. Constructor receives `mongo` object and stores reference to collection
2. CRUD methods use `self.collection` for all database operations
3. Use `ObjectId()` for MongoDB ID conversions with error handling

**Example from StudentModel:**
```python
def add_student(self, name, section_code, face_encoding):
    """face_encoding is a list of floats from face_recognition.face_encodings"""
    return self.collection.insert_one({
        'name': name,
        'section_code': section_code,
        'face_encoding': face_encoding  # Always stored as list (NumPy array converted to list)
    })
```

### Section Lookup Pattern
Sections are looked up by `'code'` field (not MongoDB `_id`). The `get_section()` method tries two lookups:
1. First attempts ObjectId match (for API compatibility)
2. Falls back to `'code'` string match (primary)

Always use `section['code']` when referencing section identifiers in routes.

## Performance & Caching Pattern

**Face encoding cache is critical for speed:**
- `ENCODING_CACHE` dict stores `{section_code: [(student_id, numpy_array), ...]}`
- Populated on first attendance check via `get_cached_encodings(section_code)`
- **Must invalidate after adding/bulk importing students:** `del ENCODING_CACHE[section['code']]`
- Without this, new students won't be recognized until app restart

## Image Processing Workflow

### Standard Pipeline (Used in attendance, add_student, bulk_import)
```python
# 1. Read bytes from file upload
image_bytes = np.frombuffer(file_upload.read(), np.uint8)

# 2. Decode using OpenCV (NOT PIL)
cv_image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

# 3. Convert BGR→RGB (cv2 uses BGR by default)
rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

# 4. Generate encodings
encodings = face_recognition.face_encodings(rgb_image)

# 5. Store as Python list (not NumPy array)
student_model.add_student(name, section_code, encodings[0].tolist())
```

**Optimization for class photos:** Resize to 25% before encoding for 16x speed improvement:
```python
small_img = cv2.resize(cv_image, (0, 0), fx=0.25, fy=0.25)
```

## Session & Authentication

- Session variable: `session['teacher_id']` stores ObjectId as string
- **All protected routes must check:** `if 'teacher_id' not in session: return redirect(url_for('login'))`
- Google OAuth integrated via Authlib (requires `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` env vars)

## Attendance Logic

### Core Constraint: No Duplicate Records Per Day
The `mark_attendance()` method prevents duplicates:
```python
def mark_attendance(self, student_id, section_code, date_obj=None, present=True):
    existing_record = self.collection.find_one({...})  # Check first
    if existing_record:
        update  # Update if exists
    else:
        insert  # Insert if new
```

**Important:** Always pass `date_obj=today` when marking from group photos to prevent timezone/date bugs.

### Face Matching Tolerance
- **Distance threshold: `0.45`** (tuned empirically)
- Only matches with distance < 0.45 are marked present
- Used in: `live_mark_attendance()` and class photo upload flow

## Critical Project Quirks

1. **Date handling:** Always use `date.today().isoformat()` (ISO 8601 format) for consistency with MongoDB queries

2. **Face encoding storage:** Stored as Python lists in MongoDB, converted back to NumPy arrays when cached:
   ```python
   np.array(s['face_encoding'])  # In get_cached_encodings()
   ```

3. **Bulk import format:** Requires **Excel file + ZIP archive**
   - Excel: Columns `'Name'` and `'Image Name'`
   - ZIP: Contains image files matching `'Image Name'` values
   - Images extracted in-memory (no disk I/O)

4. **Section code uniqueness:** Enforced at dashboard POST—must check `section_model.get_section(code)` returns None before creating

5. **Environment setup:** MongoDB uses cloud URI in current code:
   ```
   mongodb+srv://gilcagande:test1234@cluster0.q5frxuy.mongodb.net/AttedanceApp
   ```

## Common Modification Patterns

### Adding a new attendance-related endpoint
1. Verify session: `if 'teacher_id' not in session: return redirect(url_for('login'))`
2. Get section: `section = section_model.get_section(section_identifier)`
3. Pass `section['code']` to model methods (never use MongoDB `_id` for section queries)
4. After modifying students: invalidate cache with `del ENCODING_CACHE[section['code']]`

### Modifying face matching logic
- Edit tolerance threshold in `section()` POST and `live_mark_attendance()` (both currently use `0.45`)
- Distance calculation: `face_recognition.face_distance(known_encodings, test_encoding)`

### Adding section fields
- Update `SectionModel.create_section()` parameters
- Update dashboard.html form fields
- Update `edit_section()` and `delete_section()` routes if needed

## Development Workflow

**Start the app:**
```powershell
python app.py
```
- Flask runs on `http://localhost:5000`
- Debug mode enabled; code changes auto-reload

**Run without MongoDB** (for testing): Create a mock TeacherModel, SectionModel, etc. returning dummy data

**Print attendance** endpoint generates browser-print-friendly HTML table—test via `/section/<code>/print`

## Template Structure

All templates use **Tailwind CSS** via CDN. Key templates:
- `login.html`: Basic form + Google OAuth button
- `register.html`: Teacher registration
- `dashboard.html`: Teacher's sections with add/edit/delete UI
- `section.html`: Student roster + attendance capture + bulk import form

Forms use POST to routes like `/section/<id>/add_student` and `/section/<id>/bulk_import`.
