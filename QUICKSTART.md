# 🚀 Quick Start Guide - 5 Minutes to Running Portal

Get the Citizen Portal up and running with MongoDB Atlas in 5 minutes!

## Prerequisites
- Python 3.9+ installed
- MongoDB Atlas account (free tier works!)
- Git installed

## Step 1: MongoDB Atlas Setup (2 minutes)

### Create Free MongoDB Atlas Cluster

1. **Sign up** at https://www.mongodb.com/cloud/atlas/register
   
2. **Create a cluster**
   - Choose **FREE** M0 tier
   - Select your preferred region (closest to you)
   - Click "Create Cluster"

3. **Create Database User**
   - Go to "Database Access" in left menu
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `citizenportal`
   - Password: Generate a secure password (save it!)
   - Database User Privileges: "Atlas admin"
   - Click "Add User"

4. **Whitelist Your IP**
   - Go to "Network Access" in left menu
   - Click "Add IP Address"
   - For testing: Click "Allow Access from Anywhere" (0.0.0.0/0)
   - For production: Add your specific IP
   - Click "Confirm"

5. **Get Connection String**
   - Go to "Database" in left menu
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy the connection string
   - It looks like: `mongodb+srv://citizenportal:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
   - **IMPORTANT**: Replace `<password>` with your actual password!

## Step 2: Clone and Setup (1 minute)

```bash
# Clone repository
git clone <your-repo-url>
cd citizen-portal

# Make setup script executable (Unix/Mac)
chmod +x setup.sh

# Run automated setup
./setup.sh
```

The setup script will:
- Create virtual environment
- Install all dependencies
- Create required directories
- Generate secure secret keys
- Prompt for MongoDB URI

When prompted for MongoDB URI, paste your connection string from Step 1.

### Windows Users
```cmd
# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir data logs static\forms static\store static\img uploads

# Copy environment file
copy .env.example .env
```

Then edit `.env` file and add your MongoDB URI.

## Step 3: Seed Database (1 minute)

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Unix/Mac
# or
venv\Scripts\activate     # Windows

# Run seed script
python seed_data.py
```

This creates:
- ✅ 5 service categories
- ✅ 3 ministry services with questions
- ✅ 7 products (education, visa, electronics)
- ✅ 5 targeted ads
- ✅ 50 sample users
- ✅ Admin user (username: `admin`)

## Step 4: Run Application (30 seconds)

```bash
python app.py
```

You should see:
```
INFO - Starting application on 0.0.0.0:5000
INFO - MongoDB Atlas connection successful
* Running on http://0.0.0.0:5000
```

## Step 5: Access & Test (30 seconds)

### 🌐 Public Portal
Open: http://localhost:5000

**Try these:**
- Browse categories (IT, Education, Land)
- Click on a ministry → subservice → question
- Use search: "How to apply for IT certificate"
- Click "Ask (AI)" to test AI chat

### 🛒 E-commerce Store
Open: http://localhost:5000/store

**Try these:**
- Browse products
- Filter by category
- Add items to cart
- View product details

### 👨‍💼 Admin Panel
Open: http://localhost:5000/admin

**Login with:**
- Username: `admin`
- Password: (check your `.env` file's `ADMIN_PWD`)

**Important First Step:**
1. After logging in, click **"Build AI Index"** button
2. Wait for confirmation (takes 30-60 seconds)
3. Now AI search will work!

### ✅ Verify Everything Works

Test the AI search:
```bash
curl -X POST http://localhost:5000/api/ai/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how to register for digital services", "top_k": 3}'
```

## 📊 Sample Data Overview

### Users Created (50 total)
- **15 Government Employees** (age 35-45)
  - Target segments: degree programs, laptops
  - Has children in school
  
- **15 Young Professionals** (age 25-35)
  - Target segments: IELTS, overseas opportunities
  - Career-focused
  
- **20 Parents** (age 40-55)
  - Target segments: tuition, children education
  - Multiple children of school age

### Products Available
1. **Bachelor of IT** - LKR 185,000 (Degree program)
2. **IELTS Course** - LKR 25,000 (Language training)
3. **Japan Visa** - LKR 45,000 (Visa services)
4. **Laptop Deal** - LKR 85,000 (Electronics)
5. **Batik Saree** - LKR 4,500 (Fashion)
6. **O/L Tuition** - LKR 18,000 (Education)
7. **A/L Science** - LKR 24,000 (Education)

## 🧪 Testing User Segments

To test personalization, you need a user ID. Get one from the database:

```bash
# Connect to MongoDB Atlas via connection string
# Or use MongoDB Compass (GUI)

# In your code, you can get sample user IDs:
python3 -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client['citizen_portal']

# Get first government employee
user = db.users.find_one({'extended_profile.career.current_job': {'$regex': 'Government'}})
print('Government Employee ID:', str(user['_id']))

# Get first parent
user = db.users.find_one({'extended_profile.family.children': {'$exists': True, '$ne': []}})
print('Parent ID:', str(user['_id']))
"
```

Then test recommendations:
```bash
curl http://localhost:5000/api/recommendations/USER_ID_HERE
```

## 🎯 Common Test Queries

Try these in the AI search:

1. "How to apply for IT certificate?"
2. "Where can I check exam results?"
3. "How to register my child in school?"
4. "What documents needed for land title?"
5. "Digital services registration process"

## 🔧 Troubleshooting

### Problem: MongoDB Connection Failed
**Solution:**
- Check your connection string in `.env`
- Ensure password doesn't contain special characters (use simple password)
- Verify IP is whitelisted in MongoDB Atlas
- Check internet connection

### Problem: FAISS Installation Failed
**Solution:**
- Comment out `faiss-cpu==1.7.4` in `requirements.txt`
- Run `pip install -r requirements.txt` again
- The system will use numpy fallback (slower but works)

### Problem: AI Search Returns No Results
**Solution:**
- Make sure you clicked "Build AI Index" in admin panel
- Check `data/faiss.index` or `data/faiss_meta.json` exist
- Re-run: POST to `/api/admin/build_index`

### Problem: Port 5000 Already in Use
**Solution:**
Edit `.env` and change:
```env
PORT=8000
```
Then restart: `python app.py`

## 📱 Mobile Testing

Test on your phone:
1. Find your computer's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. Access: `http://YOUR_IP:5000`
3. Make sure firewall allows port 5000

## 🚀 Next Steps

### For Development
1. **Explore the code**
   - `app.py` - Main application
   - `recommendation_engine.py` - AI recommendations
   - `templates/` - Frontend HTML
   - `static/` - CSS and JavaScript

2. **Customize content**
   - Edit `seed_data.py` to add your services
   - Add real product images to `static/store/`
   - Update forms in `static/forms/`

3. **Add features**
   - Implement payment gateway
   - Add email notifications
   - Create mobile app

### For Production

1. **Security**
   ```env
   FLASK_ENV=production
   DEBUG=False
   SESSION_COOKIE_SECURE=True
   ```

2. **Change credentials**
   - Update admin password
   - Generate new secret keys

3. **Deploy**
   - See `README.md` for deployment guides
   - Use Gunicorn for production server
   - Set up HTTPS with SSL certificate

## 📚 Documentation

- **Full Guide**: See `README.md`
- **API Docs**: Test endpoints with Postman
- **Project Structure**: See `PROJECT_STRUCTURE.md`

## 🆘 Need Help?

**Check logs:**
```bash
tail -f logs/app.log
```

**Database issues:**
- Use MongoDB Compass to view data visually
- Check MongoDB Atlas dashboard for metrics

**Python errors:**
- Ensure virtual environment is activated
- Check Python version: `python3 --version`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## ✅ Success Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Connection string obtained and configured
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Database seeded (50 users, 7 products, etc.)
- [ ] Application running on port 5000
- [ ] Can browse services at http://localhost:5000
- [ ] Can access store at http://localhost:5000/store
- [ ] Admin login works at http://localhost:5000/admin
- [ ] AI Index built successfully
- [ ] AI search returns results

If all checked ✅, you're ready to develop!

## 🎉 Congratulations!

Your Citizen Portal is now running with:
- ✅ Full-featured service portal
- ✅ AI-powered search
- ✅ E-commerce store
- ✅ User segmentation
- ✅ Admin dashboard
- ✅ 50 sample users for testing

**Total setup time: < 5 minutes** ⚡

---

**Ready to customize?** Edit `seed_data.py` and add your own services, products, and content!