##  Project Overview

Project Waya is an engine for a parent-child ecosystem. It streamlines task delegation, automates allowance distribution, and provides educational STEM-focused quizzes to build financial habits in a secure, role-based environment.

### Core Objectives
* **Task Management:** Structured chore and allowance tracking.
* **Financial Literacy:** Interactive quizzes and a visual wallet ledger.
* **Gamification:** Achievement-based badge rewards for consistency.
* **Security:** High-standard data protection and role-based access control (RBAC).


##  Tech Stack

| Component          | Technology                                   |
| :----------------- | :------------------------------------------- |
| **Framework** | Django + Django REST Framework (DRF)         |
| **Database** | PostgreSQL                                   |
| **Authentication** | JWT (JSON Web Tokens)                        |
| **Web Server** | Nginx + Gunicorn                             |
| **Hosting** | Linux VPS (Ubuntu)                           |
| **Security** | HTTPS (Let's Encrypt), GDPR Compliance logic |

---

##  System Architecture

The backend follows a layered "STEM" architecture to ensure scalability and clear separation of concerns.

1.  **Frontend Layer:** React/Vue interfaces hosted on Vercel or Netlify.
2.  **API Layer:** Django REST Framework handling business logic and routing.
3.  **Data Layer:** PostgreSQL managing relational entities and data integrity.
4.  **Security Layer:** SSL/HTTPS encryption and JWT session management.

---

##  Database Entities (ERD Highlights)

The system relies on a robust relational structure to maintain transaction history and user roles:

* **Users:** Custom model with `is_parent` and `is_child` flags.
* **Chores:** Detailed models with title, reward, due date, and status.
* **Wallet & Transactions:** A secure ledger-based system for earning and spending.
* **Quizzes:** STEM-based questions with linked `Attempts` and `Badges`.

---

##  Setup & Installation

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/waya-backend.git](https://github.com/your-username/waya-backend.git)
    cd waya-backend
    ```

2.  **Set up the environment:**
    Ensure you have Python 3.10+ and PostgreSQL 14+ installed.
    ```bash
    # Using pipenv
    pip install pipenv
    pipenv install
    pipenv shell
    ```

3.  **Environment Variables:**
    Create a `.env` file in the root directory:
    ```env
    DEBUG=True
    SECRET_KEY=your-secure-secret-key
    DATABASE_URL=postgres://user:password@localhost:5432/waya
    ```

4.  **Database Migration & Server:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

---

## Production Environment

The production environment is optimized for reliability and performance:
* **Reverse Proxy:** Nginx handles incoming requests and static file serving.
* **Process Manager:** Gunicorn manages application workers.
* **Monitoring:** Sentry for error tracking and UptimeRobot for availability.


---

## Key API Deliverables

* **Auth:** User Registration, Login (JWT), and Profile Management.
* **Chores:** API endpoints for creating, assigning, and approving tasks.
* **Finance:** Wallet balance and transaction history summaries.
* **Education:** Quiz delivery, scoring, and automated badge awarding.
* **Admin:** Full management dashboard via Django Admin.

---

## Security & Compliance
* **JWT Auth:** Secure, stateless session management.
* **Role-Based Access:** Parents can manage all data; children access their specific tasks.
* **Privacy:** GDPR-ready data handling and encrypted storage of sensitive fields.
"""


