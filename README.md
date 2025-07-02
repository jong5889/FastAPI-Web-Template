# FastAPI Web Template

이 프로젝트는 FastAPI 백엔드와 React 프론트엔드를 결합한 웹 애플리케이션 개발을 위한 템플릿입니다. Docker 및 Docker Compose를 사용하여 개발 및 배포 환경을 쉽게 구축할 수 있도록 설계되었습니다.

## 주요 기술 스택

*   **백엔드**: Python, FastAPI
*   **프론트엔드**: React, JavaScript
*   **데이터베이스**: PostgreSQL (Docker Compose를 통해 연동)
*   **웹 서버**: Nginx (리버스 프록시 및 정적 파일 서빙)
*   **컨테이너**: Docker, Docker Compose

## 주요 기능

*   **FastAPI 기반 RESTful API**: 효율적이고 빠른 API 개발
*   **React 기반 SPA (Single Page Application)**: 현대적인 사용자 인터페이스
*   **Dockerized Development Environment**: 일관된 개발 환경 제공
*   **PostgreSQL 연동**: 데이터 저장 및 관리
*   **Nginx 리버스 프록시**: 백엔드와 프론트엔드 통합 및 SSL 설정 용이

## 시작하기

### Workflow Diagram

```
+-------------------+       +-------------------+       +-------------------+
|     User Action   | ----> |   Frontend (React)| ----> |   Backend (FastAPI)|
| (Browser/Client)  |       | (Nginx Static/SPA)|       | (API Endpoints)   |
+-------------------+       +-------------------+       +-------------------+
         ^                                                       |
         |                                                       |
         |                                                       v
         |                                               +-------------------+
         |                                               |   Database (PG)   |
         +-----------------------------------------------| (Data Storage)    |
                                                         +-------------------+
```

### 사전 요구 사항

*   [Docker Desktop](https://www.docker.com/products/docker-desktop) (Docker Engine 및 Docker Compose 포함)
*   [Python 3.8+](https://www.python.org/downloads/) (선택 사항, 로컬 개발 시)
*   [Node.js 14+](https://nodejs.org/en/download/) (선택 사항, 프론트엔드 개발 시)

### 설치 및 실행

1.  **프로젝트 클론**:
    ```bash
    git clone https://github.com/jong5889/FastAPI-Web-Template.git
    cd FastAPI-Web-Template
    ```

2.  **환경 변수 설정**:
    `.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 환경 변수를 설정합니다.
    ```bash
    cp .env.example .env
    # .env 파일을 열어 필요한 변수들을 설정합니다.
    ```

3.  **Docker Compose를 사용하여 서비스 실행**:
    ```bash
    docker-compose up --build -d
    ```
    이 명령은 백엔드, 프론트엔드, PostgreSQL 데이터베이스, Nginx 컨테이너를 빌드하고 실행합니다.

4.  **애플리케이션 접근**:
    *   백엔드 API: `http://localhost:8000` (또는 `.env`에 설정된 포트)
    *   프론트엔드 애플리케이션: `http://localhost:3000` (또는 `.env`에 설정된 포트)

## 프로젝트 구조

```
.
├── backend/                # FastAPI 백엔드 애플리케이션
│   ├── app/                # FastAPI 애플리케이션 코드
│   ├── Dockerfile          # 백엔드 Dockerfile
│   └── requirements.txt    # 백엔드 Python 의존성
├── frontend/               # React 프론트엔드 애플리케이션
│   ├── react-app/          # Create React App으로 생성된 React 프로젝트
│   ├── app.py              # Streamlit 앱 (선택 사항)
│   └── requirements.txt    # Streamlit 앱 의존성 (선택 사항)
├── nginx/                  # Nginx 설정 파일
│   └── conf.d/
│       └── default.conf    # Nginx 리버스 프록시 설정
├── tests/                  # 테스트 코드
├── docker-compose.yml      # Docker Compose 설정 파일
├── .env.example            # 환경 변수 예시 파일
├── .gitignore              # Git 무시 파일
├── LICENSE                 # 프로젝트 라이선스
├── README.md               # 현재 파일
└── ...
```

## 테스트

프로젝트의 테스트는 `pytest`를 사용하여 실행할 수 있습니다.

```bash
# 백엔드 컨테이너 내부에서 실행하거나, 로컬에 Python 환경을 설정하여 실행
docker-compose exec backend pytest
```

## 배포

이 템플릿은 Docker Compose를 기반으로 하므로, Docker가 설치된 서버에 `docker-compose.yml` 파일을 배포하여 쉽게 서비스를 실행할 수 있습니다. 추가적인 배포 설정 (예: HTTPS, 도메인 설정)은 `nginx/conf.d/default.conf` 파일을 수정하여 구성할 수 있습니다.

## 기여

기여를 환영합니다! 버그 리포트, 기능 제안 또는 풀 리퀘스트를 통해 프로젝트에 기여할 수 있습니다.

## 라이선스

이 프로젝트는 [LICENSE](LICENSE) 파일에 명시된 라이선스에 따라 배포됩니다.