# CampusOne - Campus Management System

CampusOne is a modern, responsive, and feature-rich Campus Management System built with Django. It provides comprehensive dashboard views, directories, notices, event management, weekly timetable grids, assignments, and attendance tracking for three user roles: **Administrators**, **Faculty**, and **Students**.

The application is architected to run serverlessly on **Vercel** backed by a **Supabase PostgreSQL database** and **Supabase Cloud Storage** for permanent media file uploads.

---

## 🚀 Live Demo

* **URL**: `https://your-vercel-app.vercel.app`
* **Admin Onboarding URL**: `https://your-vercel-app.vercel.app/register-admin/` (Requires the secret invite code)

---

## 🌟 Key Features

### 🔑 Administrator Dashboard
* **Onboarding & Approvals**: Approve or reject student and faculty registration requests.
* **Attendance Auditing**: Monitor campus attendance and approve correction requests sent by faculty.
* **Directories**: Browse searchable and filterable student and faculty listings.
* **Announcements & Noticeboard**: Publish important campus announcements.
* **Campus Event Management**: Publish events and monitor registration metrics.
* **Bulk User Upload**: Onboard students and faculty instantly by uploading Excel/CSV rosters.

### 👨‍🏫 Faculty Dashboard
* **Attendance Management**: Mark attendance for designated classes and submit correction audits.
* **Timetable Schedule**: View weekly lectures in a structured 2D table grid.
* **Assignments**: Create assignments, upload reference sheets, and grade student submissions.
* **Noticeboard Access**: View all administrator notices.

### 🎓 Student Dashboard
* **Attendance Reports**: Track attendance percentages per subject with eligibility color status indicators.
* **Timetable Schedule**: View weekly class schedules in a structured 2D table grid.
* **Assignments & Submissions**: View assignment details, download question sheets, and submit answer attachments.
* **Events & Noticeboard**: View notices and register for campus events, with WhatsApp message sharing integration.

---

## 🛠 Tech Stack

* **Web Framework**: Django (Python)
* **Hosting Platform**: Vercel (Serverless Functions)
* **Database**: Supabase PostgreSQL
* **File Storage**: Supabase Storage (S3-compatible API)
* **Styling**: Modern CSS (featuring dark/light mode toggles and Google Material Symbols)

---

## ⚙️ Local Development Setup

Follow these steps to run CampusOne locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/campusone-django.git
cd campusone-django
```

### 2. Create and Activate a Virtual Environment
**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
By default, the application will use local SQLite for development:
```bash
python manage.py migrate
```

### 5. Start the Development Server
```bash
python manage.py runserver
```
Visit the application in your browser at `http://127.0.0.1:8000/`.

---

## ☁️ Production Deployment (Vercel & Supabase)

CampusOne is configured to deploy directly to Vercel and connect with Supabase services.

### 1. Supabase Database Configuration
1. Create a new project on your **Supabase Dashboard**.
2. Go to **Project Settings** -> **Database** and copy your **Transaction Connection Pooler** string (URI).

### 2. Supabase Storage Configuration
1. Go to **Storage** on the Supabase dashboard and create a new bucket named **`media`**. Set it to **Public**.
2. Go to **Project Settings** -> **API** -> **S3 Connection** and copy your **Endpoint URL**.
3. Generate **S3 Access Keys** and note the **Access Key ID** and **Secret Access Key**.

### 3. Deploy to Vercel
1. Link your GitHub repository to your **Vercel Dashboard**.
2. Under **Project Settings** -> **Environment Variables**, add the following keys:

| Environment Variable | Value Description |
| :--- | :--- |
| `DATABASE_URL` | Your Supabase transaction connection string |
| `SUPABASE_ACCESS_KEY_ID` | Your Supabase S3 Access Key ID |
| `SUPABASE_SECRET_ACCESS_KEY` | Your Supabase S3 Secret Access Key |
| `SUPABASE_S3_ENDPOINT` | Your Supabase S3 Endpoint URL |
| `ADMIN_SIGNUP_SECRET` | A secret invite code of your choice (e.g. `MyCode2026`) for creating Admin accounts |
| `EMAIL_HOST_PASSWORD` | (Optional) Gmail App Password for SMTP activation emails |

3. Click **Deploy**. Vercel will build the project, run the build script `build_files.sh` to migrate your database, and launch the site.

---

## 🔑 Creating Your First Admin Account

Once the live site is deployed on Vercel:
1. Navigate to the registration link: `/register-admin/` (or click **Register Admin** at the bottom of the Sign In page).
2. Enter your details along with your custom `ADMIN_SIGNUP_SECRET` code.
3. This creates a master administrator account (`is_superuser=True`, `is_staff=True`), allowing you to instantly log in and access the CampusOne dashboards.

---

## 📄 License

This project is licensed under the MIT License.
