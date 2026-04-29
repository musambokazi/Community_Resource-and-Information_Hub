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
- **Database**: SQLite
- **APIs**: Google Places API (Maps)
- **Testing**: Pytest with Requests-Mock

## 📋 Prerequisites
Ensure you have the following installed:
- Python 3.10+
- A Google Cloud API Key (with Places API enabled)

## 🔧 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/m_h_t-musa/Community_Resource-and-Information_Hub.git
   cd Community_Resource-and-Information_Hub
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   # Create the virtual environment
   python3 -m venv .venv
   
   # Activate on Linux/macOS
   source .venv/bin/activate
   
   # Activate on Windows
   .venv\Scripts\activate
   ```

3. **Install Dependencies**
   Ensure your virtual environment is active, then run:
   ```bash
   pip install flask requests pytest requests-mock werkzeug
   ```

4. **Database Configuration**
   Initialize your SQLite database:
   ```bash
   python3 init_db.py
   ```

5. **Add Your API Key & Configuration**
   Create a `.env` file in the root directory and add your Google Maps API key and Flask Secret key:
   ```env
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

## 🚀 Running the App

1. **Start the Flask Server**
   Ensure your `.venv` is activated, then start the server:
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