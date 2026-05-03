# Project Structure

```
citizen-portal/
│
├── app.py                          # Main Flask application
├── recommendation_engine.py        # AI recommendation system
├── seed_data.py                    # Database seeding script
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create from .env.example)
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── README.md                      # Project documentation
├── PROJECT_STRUCTURE.md           # This file
│
├── data/                          # AI model data (auto-generated)
│   ├── faiss.index               # FAISS vector index
│   ├── faiss_meta.json           # Document metadata
│   └── embeddings.npy            # Fallback embeddings
│
├── logs/                          # Application logs
│   └── app.log                   # Main application log
│
├── uploads/                       # User uploaded files
│   └── .gitkeep
│
├── static/                        # Static assets
│   ├── style.css                 # Main stylesheet
│   ├── script.js                 # Main JavaScript
│   ├── store.css                 # Store-specific styles
│   ├── store.js                  # Store functionality
│   ├── admin.js                  # Admin panel scripts
│   │
│   ├── forms/                    # Downloadable forms
│   │   ├── it_cert_form.pdf
│   │   ├── school_admission_form.pdf
│   │   ├── document_checklist.pdf
│   │   └── land_title_application.pdf
│   │
│   ├── img/                      # Images
│   │   ├── logo.png
│   │   ├── degree_ad.jpg
│   │   └── course-card.png
│   │
│   └── store/                    # Product images
│       ├── degree_it.jpg
│       ├── ielts_course.jpg
│       ├── japan_visa.jpg
│       ├── laptop_deal.jpg
│       ├── batik_saree.jpg
│       ├── ol_tuition.jpg
│       ├── al_science.jpg
│       └── placeholder.jpg
│
├── templates/                     # HTML templates
│   ├── index.html                # Main public portal
│   ├── store.html                # E-commerce store
│   ├── admin.html                # Admin dashboard
│   ├── login.html                # Admin login
│   ├── manage.html               # Service management
│   └── base.html                 # Base template (if using)
│
├── scripts/                       # Utility scripts
│   ├── setup.sh                  # Unix setup script
│   ├── setup.bat                 # Windows setup script
│   └── backup_db.py              # Database backup utility
│
└── docs/                          # Additional documentation
    ├── API.md                    # API documentation
    ├── DEPLOYMENT.md             # Deployment guide
    ├── SECURITY.md               # Security guidelines
    └── USER_GUIDE.md             # End-user guide
```

## Key Files Description

### Core Application Files

#### `app.py`
Main Flask application with all routes and business logic:
- Public routes (services, store, search)
- Admin routes (dashboard, CRUD operations)
- AI search endpoints
- Engagement tracking
- Authentication

#### `recommendation_engine.py`
Smart recommendation system:
- User segmentation algorithm
- Personalized ad selection
- Product recommendations
- Education recommendations based on profile

#### `seed_data.py`
Database initialization script:
- Seeds categories, services, products
- Creates sample users across different segments
- Initializes admin user
- Populates ads and officers

### Configuration Files

#### `requirements.txt`
Python package dependencies:
- Flask and extensions
- MongoDB driver
- AI/ML libraries (sentence-transformers, faiss)
- Security libraries (bcrypt)
- Utilities

#### `.env`
Environment configuration (not in version control):
- MongoDB Atlas connection string
- Secret keys
- API keys
- Email configuration
- Application settings

### Frontend Files

#### `templates/index.html`
Main public portal interface:
- Category navigation
- Service browsing
- AI chat panel
- Progressive profile modal
- Multilingual support

#### `templates/store.html`
E-commerce store interface:
- Product grid
- Filters and sorting
- Shopping cart
- Product details modal
- Checkout flow

#### `templates/admin.html`
Admin dashboard:
- Analytics overview
- User insights
- Service management
- Product management
- Ad management

#### `static/script.js`
Main JavaScript functionality:
- Category and service navigation
- AI chat implementation
- Autosuggest search
- Progressive profile forms
- Engagement tracking

#### `static/store.js`
Store-specific JavaScript:
- Product filtering
- Cart management
- Checkout process
- Product modal
- Recommendation display

### Data Directories

#### `data/`
AI model data (generated after index build):
- `faiss.index` - Vector similarity index
- `faiss_meta.json` - Document metadata for search results
- `embeddings.npy` - Fallback if FAISS unavailable

#### `logs/`
Application logs:
- `app.log` - Main application log with timestamps
- Rotated daily in production

#### `uploads/`
User uploaded files:
- Profile pictures
- Document uploads
- Organized by user ID

## Database Collections Structure

### `services`
```javascript
{
  id: "ministry_it",
  category: "cat_it",
  name: {en: "...", si: "...", ta: "..."},
  subservices: [
    {
      id: "it_cert",
      name: {en: "...", si: "...", ta: "..."},
      questions: [
        {
          q: {en: "..."},
          answer: {en: "..."},
          downloads: ["..."],
          location: "...",
          instructions: "..."
        }
      ]
    }
  ]
}
```

### `users`
```javascript
{
  profile: {
    basic: {name, age, location, phone},
    contact: {email, phone},
    employment: {job}
  },
  extended_profile: {
    family: {marital_status, children, children_ages, children_education},
    education: {highest_qualification, institution, year_graduated},
    career: {current_job, years_experience, skills, career_goals},
    interests: {hobbies, learning_interests, service_preferences},
    consent: {marketing_emails, personalized_ads, data_analytics}
  },
  created: Date,
  updated: Date,
  last_active: Date
}
```

### `products`
```javascript
{
  id: "prod_degree_01",
  name: "...",
  category: "education",
  subcategory: "degree_programs",
  price: 185000,
  original_price: 225000,
  currency: "LKR",
  images: ["..."],
  description: "...",
  features: ["..."],
  tags: ["..."],
  target_segments: ["..."],
  in_stock: true,
  delivery_options: ["..."],
  rating: 4.5,
  reviews_count: 47,
  created: Date
}
```

### `engagements`
```javascript
{
  user_id: "...",
  session_id: "...",
  age: 35,
  job: "...",
  desires: ["..."],
  question_clicked: "...",
  service: "...",
  ad: "...",
  time_spent: 120,
  scroll_depth: 85,
  device_info: {user_agent, ip_address, screen_resolution},
  referral_data: {referrer, utm_source, utm_medium},
  timestamp: Date
}
```

### `ads`
```javascript
{
  id: "ad_degree_01",
  title: "...",
  body: "...",
  link: "...",
  active: true,
  priority: "high",
  tags: ["..."],
  target_segments: ["..."],
  image: "...",
  created: Date,
  start_date: Date,
  end_date: Date
}
```

## Module Dependencies

### Core Dependencies
- **Flask 3.0.0**: Web framework
- **PyMongo 4.6.0**: MongoDB driver with Atlas support
- **python-dotenv 1.0.0**: Environment configuration

### AI/ML Dependencies
- **sentence-transformers 2.3.1**: Text embeddings
- **faiss-cpu 1.7.4**: Vector similarity search
- **numpy 1.24.3**: Numerical operations
- **scikit-learn 1.3.2**: Additional ML utilities

### Security Dependencies
- **bcrypt 4.1.2**: Password hashing
- **flask-login 0.6.3**: Session management
- **PyJWT 2.8.0**: Token generation

### Utility Dependencies
- **Flask-CORS 4.0.0**: Cross-origin requests
- **Flask-Mail 0.9.1**: Email functionality
- **pandas 2.1.4**: Data processing

## Environment Variables Required

```bash
# Database
MONGO_URI=                    # MongoDB Atlas connection string
DB_NAME=citizen_portal        # Database name

# Application
FLASK_SECRET=                 # Session secret key
FLASK_ENV=development         # development/production
DEBUG=True                    # True/False
PORT=5000                     # Application port
HOST=0.0.0.0                  # Host address

# Authentication
ADMIN_PWD=                    # Initial admin password
ADMIN_EMAIL=                  # Admin email

# AI/ML
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_DIM=384

# Email (Optional)
MAIL_SERVER=
MAIL_PORT=
MAIL_USE_TLS=
MAIL_USERNAME=
MAIL_PASSWORD=

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

## Access Points

### Public URLs
- **Homepage**: http://localhost:5000/
- **Store**: http://localhost:5000/store
- **Health Check**: http://localhost:5000/health

### Admin URLs
- **Admin Login**: http://localhost:5000/admin/login
- **Admin Dashboard**: http://localhost:5000/admin
- **Service Management**: http://localhost:5000/admin/manage

### API Endpoints
- **Services**: http://localhost:5000/api/services
- **Categories**: http://localhost:5000/api/categories
- **AI Search**: http://localhost:5000/api/ai/search
- **Products**: http://localhost:5000/api/store/products
- **Recommendations**: http://localhost:5000/api/recommendations/{user_id}

## Development Workflow

1. **Setup**: Run `python seed_data.py`
2. **Development**: Run `python app.py` with DEBUG=True
3. **Testing**: Access different user segments with sample users
4. **Index Building**: POST to `/api/admin/build_index` after content changes
5. **Monitoring**: Check `logs/app.log` for errors
6. **Backup**: Regularly backup MongoDB Atlas data

## Production Considerations

1. **Security**
   - Change all default passwords
   - Enable HTTPS
   - Set SESSION_COOKIE_SECURE=True
   - Implement rate limiting

2. **Performance**
   - Use production WSGI server (Gunicorn)
   - Enable database connection pooling
   - Implement Redis caching
   - Use CDN for static files

3. **Monitoring**
   - Set up MongoDB Atlas monitoring
   - Configure application monitoring (New Relic, DataDog)
   - Set up log aggregation
   - Enable error tracking (Sentry)

4. **Backup**
   - Configure MongoDB Atlas automated backups
   - Export engagement data regularly
   - Backup uploaded files to S3/Cloud Storage
   - Version control for code

## Git Ignore Recommendations

```gitignore
# Environment
.env
venv/
__pycache__/
*.pyc

# Data
data/
logs/
uploads/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```