# ✈️ Airport API

**Airport API** is a RESTful service built with Django REST Framework that allows users to interact with an airport's system. The API supports operations related to flights, airplanes, ticket reservations, and more.

## 🚀 Features

- 🔐 JWT Authentication (for both admin and regular users)
- 👥 Role-based access control (admin & user)
- 📦 ViewSets for all resources
- 🔍 Filtering support on Plays and Performances
- 📑 Swagger UI documentation
- 🐳 Dockerized setup with PostgreSQL

## 🛠️ Technologies

- 🐍 Python 3.13
- 🌐 Django 5.2.1
- 🛠️ Django REST Framework
- 🔑 djangorestframework-simplejwt
- 🧾 drf-spectacular (Swagger)
- 🐘 PostgreSQL
- 🐳 Docker & Docker Compose

## 📚 API Overview

### 📦 Resources

- 🛫 `Airport`
- 🗺️ `Route`
- ✈️ `Airplane`
- 👨‍✈️ `Crew`
- 🕒 `Flight`
- 🧾 `Order`
- 🎫 `Ticket`
- 👤 `User` (Custom, based on `AbstractUser`)

### 🔗 Available Endpoints

| 📌 Resource | 🧰 Methods                      |
|-------------|---------------------------------|
| 🛫 Airport  | `GET`, `POST` (admin)           |
| 🗺️ Route   | `GET`, `POST` (admin)           |
| ✈️ Airplane | `GET`, `POST` (admin)           |
| 👨‍✈️ Crew  | `GET`, `POST`, `DELETE` (admin) |
| 🕒 Flight   | `GET`, `POST` (admin)           |
| 🧾 Order    | `GET`, `POST` (user)            |
| 🎫 Ticket   | Created via Reservation         |
| 👤 User     | `GET`, `POST`, `PATCH`          |

### 🔐 Authentication

Use JWT to access protected endpoints:

#### 🪪 Obtain token

```
POST /api/token/
{
  "email": "testuser@example.com",
  "password": "testuser123"
}
```

## 🐳 Setup with Docker

### 📥 1. Clone the repository

```
git clone https://github.com/dmytrominyaylo/airport-api.git
cd airport-api
```

### ⚙️ 2. Create .env file
Use the provided .env.sample to create your own .env file:
```bash
cp .env.sample .env
```
Then fill in the values:
```
DJANGO_SECRET_KEY=<your-secret-key>
POSTGRES_DB=<your_db>
POSTGRES_USER=<your_user>
POSTGRES_PASSWORD=<your_password>
POSTGRES_HOST=db
POSTGRES_PORT=5432
```
### 🔧 3. Build and run the containers
```bash
docker-compose up --build
```
The API will be available at:
```
http://localhost:8000/
```
### 🧪 4. Load initial data (optional)
If you want to prepopulate the database with sample data:
```bash
docker-compose exec airport python manage.py loaddata airport_fixture.json
```
You can create your own user:
```bash
docker-compose exec airport python manage.py createsuperuser
```

### 📖 5. Access API documentation
Swagger UI is available at:
```
http://localhost:8000/api/doc/swagger/
```