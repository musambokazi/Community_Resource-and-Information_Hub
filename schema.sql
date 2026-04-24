-- Clears old tables if they exist
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS cached_results;
DROP TABLE IF EXISTS resources;

-- Main resources table
CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    desc TEXT NOT NULL,
    lat REAL,
    lon REAL,
    image TEXT,
    google_place_id TEXT UNIQUE -- To avoid duplicates from Google
);

-- Caching table to store search results by location/query
CREATE TABLE cached_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    lat REAL,
    lon REAL,
    results_json TEXT, -- Store the JSON results
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL -- Should be hashed in production
);

-- Favorites table
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    resource_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(resource_id) REFERENCES resources(id)
);