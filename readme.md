# Library Management System

This is a Django-based Library Management System API that allows users to manage books, authors, borrowing records, and generate activity reports. It uses Docker for containerization, Celery for background tasks, JWT authentication for secured access, and Swagger for API documentation.

---

## Approach

1. **Core Features:**
   - Models for `Author`, `Book`, and `BorrowRecord`.
   - APIs for CRUD operations on authors, books, and borrowing records.
   - Reports generation and access restricted to admin users.

2. **JWT Authentication:**
   - Implemented `login` and `register` APIs.
   - Secured all APIs requiring a valid JWT token.

3. **Background Tasks with Celery:**
   - Report generation runs as a background task using Celery.
   - Reports are saved in a `reports/` directory as JSON files with timestamps.

4. **Swagger Documentation:**
   - Integrated Swagger UI at `/swagger` for API documentation and testing.
   - APIs require adding a `Bearer <your-token>` in the authorization header for secured endpoints.

---

## Steps to Run the Project

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Set Up Docker:**
   Ensure Docker and Docker Compose are installed on your system.

3. **Build and Run the Docker Container:**
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build the Docker image using the `Dockerfile`.
   - Run the Django application in a Docker container.

4. **Access the Application:**
   - Open a browser and go to `http://127.0.0.1:8000/swagger/` to access the Swagger UI.

---

## API Documentation

### Testing the APIs

1. **Register a User:**
   - Use the `POST /register/` endpoint to create a new user.
   - Example Request Body:
     ```json
     {
         "username": "testuser",
         "password": "testpassword"
     }
     ```

2. **Login:**
   - Use the `POST /login/` endpoint to obtain JWT tokens.
   - Example Request Body:
     ```json
     {
         "username": "testuser",
         "password": "testpassword"
     }
     ```
   - Copy the `access` token from the response.

3. **Authorize:**
   - In the Swagger UI, click on the `Authorize` button.
   - Enter the token in the format:
     ```
     Bearer <your-token>
     ```

4. **Use the APIs:**
   - Access other endpoints like `/authors/`, `/books/`, `/borrow/`, and `/reports/`.
   - Example: Add a new author using `POST /authors/`:
     ```json
     {
         "name": "J.K. Rowling",
         "bio": "British author, best known for the Harry Potter series."
     }
     ```

5. **Reports API:**
   - Generate a new report using `POST /reports/` (admin access required).
   - Retrieve the latest report using `GET /reports/`.
   - The reports directory contains the latest reports you can verify after using /reports post

---

## Notes
- Ensure the Celery worker is running to enable background tasks for report generation.
- Static files are served properly through the configured Docker container.
- Use Aniket and Aniket@88 for admin login or create one using django admin interface.
- If you face any difficulty or any error please reach out to me on aniketlokhande420@gmail.com or give a call on 8605470673
