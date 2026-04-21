DROP TABLE IF EXISTS resources; -- Clears the old table if it exists

CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- A unique number for each card
    title TEXT NOT NULL,                  -- The name of the clinic or service
    category TEXT NOT NULL,               -- health, transport, etc.
    desc TEXT NOT NULL,                   -- The description
    lat REAL,                             -- Latitude for the map
    lon REAL                              -- Longitude for the map
);