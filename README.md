# Community_Resource-and-Information_Hub

A Flask-based web application designed to help community members in South Africa find essential local services like police stations, hospitals, and libraries using real-time GPS data.

## 🚀 Features
- **Proximity Search**: Uses Google Places API to find the top 3 closest resources per category.
- **Dynamic Theming**: Supports Navy Dark Mode and Light Mode, syncing automatically with device settings.
- **Mobile Responsive**: Optimized for smartphones using CSS Flexbox and Media Queries.
- **Smooth Navigation**: Auto-scrolls to results after a search is performed.

## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **APIs**: Google Places API (Maps)
- **Testing**: Pytest with Requests-Mock

## 📋 Prerequisites
Ensure you have the following installed:
- Python 3.10+
- PostgreSQL
- A Google Cloud API Key (with Places API enabled)

## 🔧 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/m_h_t-musa/Community_Resource-and-Information_Hub.git](https://github.com/m_h_t-musa/Community_Resource-and-Information_Hub.git)
   cd Community_Resource-and-Information_Hub

2. **Install Dependencies**
   ```bash
   pip install flask requests psycopg2-binary SQLAlchemy pytest requests-mock
   ```

3. **Database Configuration**
   Initialize your PostgreSQL database and run the migration script to create tables:
   ```bash
   python3 init_db.py
   ```

4. **Add Your API Key**
   Open `app.py` and replace the `API_KEY` variable with your unique Google Cloud key.

## 🚀 Running the App

1. **Start the Flask Server**
   ```bash
   python3 app.py
   ```

2. **Access the Application**
   Navigate to `http://127.0.0.1:5000` (or your server's IP address) in your browser.

## 🧪 Testing

Run the automated tests using Pytest:
```bash
pytest
```

## 📁 Project Structure
```
/Community_Resource-and-Information_Hub
├── app.py             # Main Flask Application & API logic
├── init_db.py         # Database initialization script
├── requirements.txt   # Project dependencies
├── static/            # CSS and JavaScript files
├── templates/         # HTML templates
└── .gitignore         # Git configuration
```

## 👥 Usage Example

1. Open the app in your browser.
2. Allow location access for "Precise Location".
3. Click "Use My Precise Location".
4. The page will refresh showing nearby police, hospitals, and transport options.
5. Use the "Specific Search" box to look for places like "Springs Mall".

## 📄 License
MIT License