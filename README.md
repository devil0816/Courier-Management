# Courier Management System

A web-based Courier Management System built with Flask and SQLite. The application allows users to register, log in, manage courier shipments, and track package status with a visual timeline.

## Features

- **User Authentication**: Secure user registration, login, and session management.
- **Password Reset**: Reset forgotten passwords via verification codes sent to the registered email address.
- **Courier Management**: 
  - Add new couriers (Sender, Receiver, Weight, Charges, Status, and Proof Image).
  - Edit existing courier shipment details.
  - Delete courier records.
  - Search courier shipments by Sender or Receiver.
- **Shipment Tracking**: Track package status (Pending, Dispatched, In Transit, Out for Delivery, Delivered) via tracking ID, complete with a visual progress timeline.

## Tech Stack

- **Backend**: Python (Flask, Flask-SQLAlchemy)
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, Jinja2 Templates, Bootstrap 5 (CSS/JS)
- **SMTP/Email**: Gmail SMTP server integration for sending verification codes

## Setup & Installation

### Prerequisites

- Python 3.10+ installed on your system.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/devil0816/Mood-Based-Music-Recommender.git
   cd Mood-Based-Music-Recommender
   ```

2. **Set Up a Virtual Environment** (Optional but recommended):
   ```bash
   python -m venv .venv
   # On Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install Flask Flask-SQLAlchemy
   ```

4. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add your SMTP credentials:
   ```env
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   SECRET_KEY=your-flask-secret-key
   ```
   *Note: For Gmail, you will need to generate a 16-character App Password.*

5. **Run the Application**:
   ```bash
   python app.py
   ```
   The app will run locally at `http://127.0.0.1:5000/`.
