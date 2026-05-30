# Transport Management System

A comprehensive desktop application for managing transport operations, vehicles, drivers, passengers, and maintenance schedules with role-based access control.

## Overview

The Transport Management System is a multi-user application that streamlines transport operations with features including:
- **Driver Management** - Track drivers, assignments, and performance
- **Vehicle Management** - Monitor vehicles, fuel consumption, and maintenance
- **Passenger Management** - Booking, billing, and payment tracking
- **Route & Schedule Management** - Plan routes and manage trip schedules
- **Maintenance Tracking** - Schedule and log maintenance activities
- **Analytics & Reports** - Generate comprehensive reports and insights

## Tech Stack

- **Frontend:** PyQt5 (Desktop GUI)
- **Backend:** Python
- **Database:** SQL Server (via ODBC)
- **Security:** bcrypt (password hashing), cryptography (data encryption)
- **Reporting:** ReportLab (PDF generation), Matplotlib (data visualization)

## Demo  
(Click to view full video on youtube)

[![Transport Management System Demo](https://img.youtube.com/vi/25aBhh11mJk/0.jpg)](https://www.youtube.com/watch?v=25aBhh11mJk)

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Login with credentials provided in `CREDENTIALS.md`

---

**Default Roles:** Admin, Driver, Passenger, Maintenance
