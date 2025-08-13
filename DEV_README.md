# DEV Project Setup Guide

Follow these steps to set up your development environment for this project.

---

## 1. Copy Environment File

```sh
cp -RPp .env.example .env
```

---

## 2. Edit Environment Variables

- Open the `.env` file.

- **Uncomment** the following line and update it as shown:

  ```env
  CORS_ALLOW_ORIGIN='http://localhost:5173;http://localhost:8080'
  ```

- **Delete** or comment out any line that says:

  ```env
  CORS_ALLOW_ORIGIN='*'
  ```

---

## 3. Switch to Correct Node Version

```sh
nvm use 22
```

---

## 4. Install Frontend Dependencies

```sh
npm install
```

---

## 5. Build Frontend

```sh
npm run build
```

---

## 6. Create Python Virtual Environment

Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

```sh
mkproject --python=python3.12 -f castopenwebui
```

---

## 7. Install Backend Dependencies

```sh
cd backend
pip install -r requirements.txt
```

---

## 8. Start Backend Development Server

```sh
LOCAL=1 ./dev.sh

```

---

## 9. Start Frontend Development Server

In a new terminal window, from the **root directory**:

```sh
npm run dev
```

---

## 10. Access API Documentation

- Open [http://localhost:8080/docs](http://localhost:8080/docs) in your browser.

---

## 11. Access the Frontend

- Go to [http://localhost:5173/](http://localhost:5173/)
- Create a superuser account and start using the system!

---
