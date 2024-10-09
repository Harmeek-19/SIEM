# SIEM Tool Project

## 1. Project Overview

This Security Information and Event Management (SIEM) tool is designed to collect, analyze, and correlate security events from various sources to detect and respond to security threats in real-time. It provides a centralized dashboard for monitoring security events, generating alerts, and facilitating incident response.

Key Features:
- Real-time log collection and analysis
- Threat detection using machine learning algorithms
- Customizable alert rules and notifications
- Integration with threat intelligence feeds
- Comprehensive reporting and analytics
- User-friendly dashboard for security monitoring

## 2. Technology Stack

- Backend:
  - Django 5.1.1
  - Django REST Framework 3.15.2
  - Celery 5.4.0 (for asynchronous task processing)
  - PostgreSQL 13 (database)
  - Redis 6 (for caching and as message broker)
  - Elasticsearch 8.15.1 (for efficient log storage and searching)

- Frontend:
  - Next.js (React framework)
  - Tailwind CSS (for styling)

- Containerization:
  - Docker
  - Docker Compose

- Authentication:
  - JWT (JSON Web Tokens)

## 3. Project Structure

```
/siem_project_root
├── .gitignore
├── docker-compose.yml
├── README.md
├── siem_project/                 # Django backend
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── siem_project/             # Main Django project directory
│   ├── alert_engine/             # Alert management app
│   ├── data_processing/          # Log processing and analysis app
│   ├── authentication/           # Custom user authentication app
│   └── threat_intelligence/      # Threat intel integration app
└── siem-dashboard/               # Next.js frontend
    ├── .dockerignore
    ├── Dockerfile.frontend
    ├── package.json
    ├── next.config.js
    └── src/
        ├── components/
        ├── pages/
        └── styles/
```

## 4. Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/Harmeek-19/SIEM.git
   cd siem_project
   ```

2. Build and start the Docker containers:
   ```
   docker-compose up --build
   ```

3. Run migrations for the Django backend:
   ```
   python manage.py migrate
   ```

4. Create a superuser for Django admin:
   ```
   python manage.py createsuperuser
   ```

5. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

## 5. Database Configuration

The project uses PostgreSQL. The configuration is managed through Docker Compose and environment variables. Ensure the following environment variables are set:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

## 6. Environment Variables

Create a `.env` file in the project root with the following variables:

```
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@postgres:5432/dbname
REDIS_URL=redis://redis:6379/0
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
```

## 7. Running the Server

The server components run in Docker containers. Use the following commands:

- Start all services: `docker-compose up`
- Stop all services: `docker-compose down`
- Rebuild containers: `docker-compose up --build`

## 8. API Endpoints

- `/api/security-events/`: CRUD operations for security events
- `/api/alerts/`: Manage alerts
- `/api/threat-intel/`: Access threat intelligence data
- `/api/reports/`: Generate and retrieve reports

For a complete list of endpoints, access the Swagger documentation at `/api/docs/`.

## 9. Authentication

The system uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Obtain a token: `POST /api/auth/token/`
2. Use the token in the Authorization header: `Authorization: Bearer <your_token>`

## 10. Models

Key models include:
- `SecurityEvent`: Represents individual security events
- `Alert`: Stores generated alerts
- `AlertRule`: Defines rules for alert generation
- `ThreatIntelligence`: Stores threat intelligence data

## 11. User Management

User management is handled through the custom `authentication` app. It includes:
- Custom user model with role-based access control
- User registration and profile management
- Password reset functionality

## 12. Log Collection and Processing

- Logs are collected using Celery tasks
- Raw logs are processed and normalized
- Processed logs are stored in Elasticsearch for efficient querying

## 13. Alert Engine

- Customizable alert rules
- Real-time alert generation based on log analysis
- Alert notifications via email and in-app notifications

## 14. Search Functionality

- Utilizes Elasticsearch for fast, full-text search across logs and events
- Advanced filtering and aggregation capabilities

## 15. Pagination

API endpoints use cursor-based pagination for efficient data retrieval, especially for large datasets.

## 16. Error Handling and Logging

- Centralized error handling for API responses
- Comprehensive logging using Python's logging module
- Log rotation and retention policies

## 17. Testing

Run tests using:
```
docker-compose exec web python manage.py test
```

The project includes:
- Unit tests for models and utility functions
- Integration tests for API endpoints
- Frontend tests using Jest and React Testing Library

## 18. Deployment

For production deployment:
1. Update environment variables for production settings
2. Use a production-grade web server like Nginx
3. Ensure proper security measures (firewall, HTTPS, etc.)
4. Set up monitoring and alerting for the SIEM system itself

## 19. Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make changes and commit: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

## 20. Troubleshooting

- Check Docker logs: `docker-compose logs`
- Ensure all required services are running
- Verify environment variables are set correctly
- Check the application logs for specific error messages

## 21. License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 22. Acknowledgments

- [Django](https://www.djangoproject.com/)
- [Next.js](https://nextjs.org/)
- [Elasticsearch](https://www.elastic.co/)
- [Docker](https://www.docker.com/)

## 23. Contact

For any queries or support, please contact Harmeek Singh at harmeek1929@gmail.com.

## Additional Features

- **Machine Learning Integration**: Utilizes scikit-learn for anomaly detection in security events.
- **Real-time Updates**: WebSocket integration for live updates on the dashboard.
- **Compliance Reporting**: Built-in reports for common compliance standards (e.g., GDPR, HIPAA).
- **Threat Intelligence Integration**: Automated updates from various threat feeds.
- **Scalable Architecture**: Designed to handle high volumes of log data efficiently.
