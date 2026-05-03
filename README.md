<<<<<<< HEAD
# Citizen Portal



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/chathuranavodya86-group/citizen-portal.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.com/chathuranavodya86-group/citizen-portal/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
=======
# Citizen Services Portal - Advanced Implementation

A comprehensive government citizen services portal with AI-powered search, personalized recommendations, and e-commerce capabilities.

## 🌟 Features

### Core Features
- **Multilingual Support** (English, Sinhala, Tamil)
- **AI-Powered Search** using sentence transformers and FAISS vector indexing
- **Smart Recommendations** based on user demographics and behavior
- **Progressive Profiling** for gradual user data collection
- **Public E-commerce Store** for government services and products
- **Advanced Analytics Dashboard** for administrators
- **Engagement Tracking** with detailed behavioral analytics

### User Segmentation
- Government employees
- Parents with school-age children
- Young professionals
- Career seekers
- Education-focused users

### Product Categories
- Educational programs (Degrees, IELTS, Tuition)
- Visa services (Japan, overseas opportunities)
- Electronics (Government employee discounts)
- Traditional products (Handloom, Batik)
- Professional training and certifications

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask (Python 3.9+)
- **Database**: MongoDB Atlas
- **AI/ML**: Sentence Transformers, FAISS
- **Authentication**: bcrypt, Flask sessions
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

### Database Collections
- `services` - Government ministry services and subservices
- `categories` - Service categories with multilingual names
- `users` - User profiles with progressive data collection
- `products` - E-commerce products
- `orders` - Order management
- `engagements` - User interaction tracking
- `ads` - Personalized advertisements
- `officers` - Government officer information
- `admins` - Admin user accounts

## 📦 Installation

### Prerequisites
```bash
- Python 3.9 or higher
- MongoDB Atlas account
- pip (Python package manager)
- Virtual environment (recommended)
```

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd citizen-portal
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: MongoDB Atlas Setup

1. Create a MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster (free tier available)
3. Create a database user with read/write permissions
4. Whitelist your IP address (or 0.0.0.0/0 for testing)
5. Get your connection string

Your connection string will look like:
```
mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### Step 5: Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` and update:
```env
MONGO_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=citizen_portal
FLASK_SECRET=your-secure-random-secret-key
ADMIN_PWD=your-admin-password
```

### Step 6: Create Required Directories
```bash
mkdir -p data logs static/forms static/store static/img uploads
```

### Step 7: Seed Database
```bash
python seed_data.py
```

This will create:
- 5 service categories
- 3 ministry services with multiple subservices
- 50 sample users across different segments
- 7 products (education, visa services, electronics, fashion)
- 5 targeted advertisements
- Admin user (username: admin)

### Step 8: Build AI Vector Index
```bash
# Start the application
python app.py

# In another terminal or use Postman/curl:
curl -X POST http://localhost:5000/api/admin/build_index \
  -H "Content-Type: application/json" \
  -b "session=admin_session_cookie"

# Or login to admin panel and use the "Build Index" button
```

### Step 9: Run Application
```bash
python app.py
```

The application will be available at:
- Public Portal: http://localhost:5000
- Admin Panel: http://localhost:5000/admin
- Store: http://localhost:5000/store

## 🎯 Usage Guide

### For Citizens

1. **Browse Services**
   - Navigate through categories (IT, Education, Land, Health)
   - Click on ministries to see subservices
   - Select questions to view answers with downloads and locations

2. **AI-Powered Search**
   - Use the search bar or click "Ask (AI)"
   - Type natural language questions
   - Get relevant answers from multiple sources
   - View source references and related documents

3. **Progressive Profile**
   - Optionally create a profile for personalized recommendations
   - Fill step-by-step: Basic info → Contact → Employment
   - Get tailored product and service recommendations

4. **Public Store**
   - Browse products by category
   - Filter by price, delivery options
   - Add to cart and checkout
   - Special deals for government employees

### For Administrators

1. **Login**
   - Navigate to `/admin/login`
   - Default credentials: username=admin, password=admin123
   - Change password immediately after first login

2. **Dashboard**
   - View engagement analytics
   - Monitor user segments
   - Track product performance
   - Export engagement data as CSV

3. **Service Management**
   - Add/edit/delete ministry services
   - Manage categories and officers
   - Update multilingual content

4. **Product Management**
   - Add new products
   - Set pricing and discounts
   - Define target segments
   - Manage inventory

5. **Advertisement Management**
   - Create targeted ads
   - Set priority and active dates
   - Define target segments
   - Track ad engagement

6. **AI Index Management**
   - Rebuild search index after content updates
   - Monitor search performance
   - View index statistics

## 🔧 Configuration

### Email Configuration (Optional)
For email notifications and marketing:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

### Payment Gateway (Future Enhancement)
Stripe integration ready:
```env
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

### Production Settings
```env
FLASK_ENV=production
DEBUG=False
SESSION_COOKIE_SECURE=True
```

## 🧪 Testing

### Manual Testing Checklist
- [ ] Service browsing and navigation
- [ ] Multilingual content display
- [ ] AI search with various queries
- [ ] Progressive profile creation
- [ ] Product browsing and filtering
- [ ] Add to cart and checkout flow
- [ ] Admin login and management
- [ ] Engagement tracking
- [ ] Analytics dashboard

### Test Queries for AI Search
1. "How to apply for an IT certificate?"
2. "Where can I check my exam results?"
3. "How to register my child in school?"
4. "What documents are needed for land title?"
5. "Digital services registration process"

### Test User Segments
The seeded data includes 50 users in these segments:
- Government employees (15) - Target: degree programs, laptops
- Young professionals (15) - Target: IELTS, overseas opportunities
- Parents (20) - Target: tuition, children's education

## 📊 API Documentation

### Public Endpoints

#### Get All Services
```http
GET /api/services
Response: Array of service objects
```

#### Get Single Service
```http
GET /api/service/:service_id
Response: Service object with subservices
```

#### Get Categories
```http
GET /api/categories
Response: Array of category objects
```

#### Search Autosuggest
```http
GET /api/search/autosuggest?q=exam
Response: Array of matching services
```

#### AI Search
```http
POST /api/ai/search
Body: {"query": "how to apply for IT certificate", "top_k": 5}
Response: {"answer": "...", "sources": [...], "hits": 5}
```

#### Get Products
```http
GET /api/store/products?category=education&min_price=10000
Response: Array of product objects
```

#### Log Engagement
```http
POST /api/engagement
Body: {"user_id": "...", "service": "...", "question_clicked": "..."}
Response: {"status": "ok"}
```

### Admin Endpoints (Require Authentication)

#### Build AI Index
```http
POST /api/admin/build_index
Response: {"count": 150, "faiss": true}
```

#### Get Insights
```http
GET /api/admin/insights
Response: {"age_groups": {...}, "jobs": {...}, "services": {...}}
```

#### Manage Services
```http
GET /api/admin/services
POST /api/admin/services (body: service object)
DELETE /api/admin/services/:service_id
```

## 🔐 Security Considerations

### Implemented
- ✅ Bcrypt password hashing
- ✅ Session-based authentication
- ✅ CORS configuration
- ✅ Input validation
- ✅ MongoDB injection prevention
- ✅ Secure cookie settings

### Recommended for Production
- [ ] HTTPS/SSL certificate
- [ ] Rate limiting (Redis-based)
- [ ] CSRF protection
- [ ] Content Security Policy headers
- [ ] Regular security audits
- [ ] Database backup automation
- [ ] API key authentication for sensitive endpoints

## 🚀 Deployment

### MongoDB Atlas (Database)
Already configured - no changes needed for production

### Heroku Deployment
```bash
# Install Heroku CLI
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set MONGO_URI="your-mongodb-uri"
heroku config:set FLASK_SECRET="your-secret"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main
```

### DigitalOcean/AWS Deployment
```bash
# On server
sudo apt update
sudo apt install python3-pip python3-venv nginx

# Clone and setup
git clone <repo>
cd citizen-portal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/citizen-portal/static;
    }
}
```

## 📈 Performance Optimization

### Database Indexing
Already implemented:
- Service ID unique index
- User email index
- Engagement timestamp index
- Product category index

### Caching Strategy
Recommended additions:
- Redis for session storage
- Query result caching
- Static file CDN

### Monitoring
- MongoDB Atlas built-in monitoring
- Application logs in `logs/app.log`
- Custom analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@citizenportal.gov.lk
- Documentation: /docs

## 🗺️ Roadmap

### Phase 1 (Current)
- ✅ Core service portal
- ✅ AI-powered search
- ✅ User segmentation
- ✅ E-commerce store
- ✅ Admin dashboard

### Phase 2 (Planned)
- [ ] Mobile app (React Native)
- [ ] Payment gateway integration
- [ ] SMS notifications
- [ ] Advanced chatbot
- [ ] Multi-tenant support for different regions

### Phase 3 (Future)
- [ ] Blockchain for land records
- [ ] Biometric authentication
- [ ] API marketplace
- [ ] Real-time service status
- [ ] Citizen feedback system

## 📞 Contact

Project Lead: Government Digital Services
Email: digital@gov.lk
Website: https://portal.gov.lk

---

**Built with ❤️ for Sri Lankan Citizens**
>>>>>>> ed8db14 (Initial commit)
