# Project Status & Roadmap

This document tracks the development progress and outlines future tasks for the project.

## ✅ Completed Features

### Backend (FastAPI)
- [x] User authentication with JWT (signup, login, token refresh).
- [x] Role-based access control (e.g., `/admin` endpoint).
- [x] Database integration with SQLAlchemy.
- [x] RESTful API structure with automated Swagger/ReDoc documentation.
- [x] Centralized configuration management using `.env` files.
- [x] Basic logging and error handling.

### Frontend (Nginx)
- [x] Basic static file serving with Nginx.
- [x] Simple placeholder `index.html`.

### Development Environment
- [x] Docker Compose setup for running `backend` and `frontend` services.
- [x] Local development setup scripts and instructions.
- [x] Example environment file (`.env.example`) for easy configuration.

---

## 🚀 Next Steps & Future Enhancements

### Frontend Development
- [x] Choose and implement a JavaScript framework (e.g., React, Vue) for a dynamic user interface.
- [x] Create frontend components for user registration and login to interact with the backend API.
- [x] Develop a UI to display data from protected API endpoints.
- [x] Implement a modern CSS framework or styling solution (e.g., Tailwind CSS, Bootstrap).
- [x] Add user feedback mechanisms (e.g., notifications, modals).

### Backend Enhancements
- [x] Expand API endpoints for core application features (e.g., managing posts, user profiles, etc.).
- [x] Implement comprehensive database models (`models.py`) and schemas (`schemas.py`) for new features.
- [x] Write unit and integration tests for new API endpoints.
- [x] Enhance validation for API inputs.
- [x] Implement rate limiting for public endpoints.

### Security & Authentication
- [x] **(High Priority)** Enhance token security by storing JWTs in `HttpOnly` cookies to mitigate XSS attacks.
- [x] Implement OAuth 2.0 for social logins (e.g., Google, GitHub, Kakao, Naver) to improve user convenience.
- [x] Add Multi-Factor Authentication (MFA), such as TOTP (e.g., Google Authenticator), for high-security applications.
- [ ] Implement a robust Cross-Site Request Forgery (CSRF) protection mechanism if using cookie-based authentication.

### Deployment & Operations
- [ ] Refine the CI/CD pipeline (e.g., add automated testing and deployment stages).
- [ ] Configure a production-ready database.
- [ ] Set up HTTPS for the Nginx server.
- [ ] Implement structured logging for better monitoring in production.