# Airbnb-Style Database Platform

An end-to-end database project for an Airbnb-like accommodation service.

This repository brings together the conceptual database design, the provided MySQL database, the Python application logic, and a lightweight Bottle-based web interface into one cohesive system. The `workbench.mwb` file documents and visualizes the ER model, the `Airbnb.sql` file provides the database used by the project, and the Python layer implements the SQL-driven functionality that demonstrates how the model operates in practice.

## Overview

The project models the core workflow of a short-term rental platform. Users can act as hosts and guests, browse and list properties, make bookings, leave reviews, manage wishlists, and receive recommendations. The database captures the structure of that domain, while the application layer executes the queries and business logic that make the system usable.

The repository is organized around three practical parts:

- Database design and ER visualization
- Application logic and SQL queries
- Web pages used to test and display results locally

## Repository Structure

```text
.
├── er-model/
│   └── workbench.mwb
├── app/
│   ├── app.py
│   ├── sql/
│   │   └── Airbnb.sql
│   ├── website.py
│   └── web/
│       ├── index.html
│       └── forms.html
└── README.md
```

## Architecture

The project starts with the ER model in `er-model/workbench.mwb`, which captures the structure of the Airbnb-style domain. That model defines the entities and relationships that the rest of the project relies on.

The database itself is provided in `app/sql/Airbnb.sql`. The Python application in `app/app.py` connects to that database and implements the SQL-based operations required by the project. These include property checks, host ranking, property filtering, review-text analysis, guest similarity queries, host-value analysis, and a recommendation algorithm.

The Bottle entry point in `app/website.py` exposes the functionality through local routes, while the HTML files in `app/web/` provide a simple browser interface for submitting parameters and inspecting the results.

## Main Features

### Database Model

- Airbnb-style schema covering users, hosts, guests, properties, bookings, payments, reviews, wishlists, facilities, rules, discounts, and related entities
- Primary keys, foreign keys, and junction tables that preserve relational integrity
- A model focused on realistic SQL querying rather than a simplified demo schema

### Application Logic

- `checkIfPropertyExists` checks whether a property of a given type exists in a given location.
- `selectTopNhosts` returns the top `N` hosts for each property type based on listing count.
- `findMatchingProperties` filters properties using wishlist amenities, booking history rules, and host-exclusion constraints.
- `countWordsForProperties` identifies qualifying properties and performs frequency analysis on review text after removing stop words.
- `findCommonPropertiesAndGuests` finds overlapping property history between two guests.
- `highValueHost` evaluates high-value properties and aggregates amenity frequency with nested SQL logic.
- `recommendProperty` computes a weighted recommendation score using amenities, price, and rating, then stores the best match in a wishlist when appropriate.

### Web Interface

- Local Bottle server for browser-based testing
- HTML forms for submitting query parameters
- Server-rendered tables for displaying query results
- A lightweight presentation layer intended for demonstration and validation

## Installation & Setup

### 1. Restore the database

1. Start a local MySQL server.
2. Import `app/sql/Airbnb.sql` into a MySQL database using MySQL Workbench or another SQL client.
3. Make sure the database name used locally matches the value configured in `app/app.py`.
4. If necessary, update the `database` field in `app/app.py` so it points to your local MySQL database.

### 2. Configure the Python connection

Open `app/app.py` and update the database connection settings near the top of the file if needed:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password_here',
    'database': 'new_airbnb'
}
```

The application expects a local MySQL database that contains the imported `Airbnb.sql` data.

### 3. Install dependencies

Install the required Python packages:

```bash
pip install bottle pymysql
```

### 4. Run the application

Start the Bottle server from the `app/` directory:

```bash
python website.py
```

Then open:

```text
http://localhost:8080
```

The root page serves the browser UI, and the routes exposed by `website.py` forward requests to the Python functions in `app.py`.