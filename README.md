# Airbnb-Style Database Platform

University project for the course *Database Design and Use* (Spring Semester 2025). The repository combines two sequential deliverables into one cohesive full-stack database project:

1. Phase 1 designs the database schema and ER model for an Airbnb-like platform.
2. Phase 2 implements a Bottle-based web application in Python that queries the same MySQL database and exposes the course requirements through a local web UI.

The result is a complete end-to-end example of database modeling, SQL schema design, application logic, and lightweight web presentation working together on a single domain.

## Tech Stack

- MySQL
- MySQL Workbench
- Python 3
- Bottle web framework
- PyMySQL
- HTML

## Repository Structure

```text
.
├── database/
│   ├── er-model/
│   │   └── workbench.mwb
│   ├── schema/
│   │   └── DB.sql
│   └── documentation/
│       └── readme.txt
├── app/
│   ├── app.py
│   ├── sql/
│   │   └── Airbnb.sql
│   ├── website.py
│   └── web/
│       ├── index.html
│       └── forms.html
├── docs/
│   ├── README-assignment-notes.md
│   ├── assignment-1.pdf
│   └── assignment-2.pdf
├── .gitignore
└── README.md
```

### Suggested Mapping From the Current Repository

- `1/` becomes `database/`
- `2/` becomes `app/`
- The root `README.md` becomes the primary project documentation
- The application-specific notes currently in `2/README.md` can be preserved as a supporting document under `docs/`
- The original assignment PDFs are preserved under `docs/`

## Architecture

This project is organized as a two-phase pipeline:

**Phase 1: Database Design**

The first assignment defines the conceptual and logical model of the platform. It includes the ER design, the MySQL schema, and the assumptions used to model users, hosts, guests, properties, bookings, payments, reviews, wishlists, discounts, amenities, and rules.

**Phase 2: Application Logic and Frontend**

The second assignment consumes the schema produced in Phase 1 and implements a small 3-tier web application:

- Presentation layer: HTML pages served from `web/`
- Application layer: Python logic in `app.py`
- Data layer: MySQL database initialized from the Phase 1 schema

The Bottle server defined in `website.py` routes requests from the browser to Python functions, which in turn execute SQL queries through PyMySQL. In practice, the database design determines what the application can query, while the application demonstrates the business use of that schema.

## Features

### Database Design

- ER model for an Airbnb-like platform
- Entities for users, hosts, guests, properties, bookings, payments, reviews, wishlists, facilities, rules, discounts, and supporting relationships
- SQL schema generation for MySQL
- Design assumptions documented in the assignment notes

### Application Logic

The Python application implements the following course requirements:

- `checkIfPropertyExists` checks whether a property of a given type exists in a given location and returns a simple yes/no result.
- `selectTopNhosts` finds the top `N` hosts for each property type by number of listings.
- `findMatchingProperties` identifies properties that match a guest’s wishlist amenities, booking history rules, and host-exclusion constraints.
- `countWordsForProperties` filters properties by booking and wishlist conditions, then performs word-frequency analysis over review text while ignoring stop words.
- `findCommonPropertiesAndGuests` finds shared properties between two guests and returns the related guest/property combination.
- `highValueHost` evaluates properties belonging to high-value hosts and guests using nested SQL aggregation.
- `recommendProperty` computes a weighted recommendation score using amenity preferences, rating, and price, then creates or updates a wishlist entry for the best match.

### Web Interface

- Local Bottle server on `http://localhost:8080`
- HTML form-based interface for submitting query parameters
- Server-side rendering of query results as HTML tables

## Installation & Setup

### 1. Create and load the database

1. Start MySQL locally.
2. Create a database for the project, for example:

   ```sql
   CREATE DATABASE new_airbnb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. Open `database/schema/DB.sql` in MySQL Workbench or your preferred SQL client.
4. Execute the file against the newly created database.
5. Verify that all tables, keys, and relationships were created successfully.

### 2. Configure the Python application

Open `app/app.py` and update the database connection settings near the top of the file:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',
    'database': 'new_airbnb'
}
```

Make sure the `database` value matches the schema you created in MySQL.

### 3. Install dependencies

Create and activate a virtual environment, then install the required packages:

```bash
pip install bottle pymysql
```

If you prefer a requirements file, you can add one with:

```text
bottle
pymysql
```

### 4. Run the application

Start the Bottle server from the application directory:

```bash
python website.py
```

Then open:

```text
http://localhost:8080
```

The root page serves the frontend UI, while the routes in `website.py` expose the implemented SQL-driven functions.

## Notes

- The project was developed as part of a university assignment and therefore emphasizes correctness, explicit SQL logic, and traceable design decisions.
- The application is intended for local execution only.
- The Phase 2 implementation depends on the schema generated in Phase 1.

## Credits

- Developers: Δημήτριος Ανδρεάκης and Σταματίνα Ναδάλη
- Course: Database Design and Use
- Semester: Spring 2025
