import os
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME', 'citizen_portal')]

new_products = [
    {
        'id': 'prod_adv_ai_01',
        'name': 'Advanced AI & Machine Learning Course',
        'category': 'education',
        'subcategory': 'professional_development',
        'price': 45000,
        'original_price': 60000,
        'currency': 'LKR',
        'images': ['/static/store/advanced_ai.jpg'],
        'description': 'Master AI and Machine Learning. Perfect for IT professionals and engineers looking to upgrade their skills.',
        'features': ['Python, TensorFlow, PyTorch', 'Hands-on projects', 'Government certified', 'Weekend classes'],
        'tags': ['ai', 'machine_learning', 'it', 'engineer', 'developer', 'technology'],
        'target_segments': ['tech_professional', 'engineer', 'graduate'],
        'in_stock': True,
        'delivery_options': ['online', 'classroom'],
        'rating': 4.9,
        'reviews_count': 112,
        'created': datetime.now(timezone.utc)
    },
    {
        'id': 'prod_teacher_training_01',
        'name': 'Modern Pedagogical Methods Workshop',
        'category': 'education',
        'subcategory': 'training',
        'price': 15000,
        'original_price': 20000,
        'currency': 'LKR',
        'images': ['/static/store/teacher_training.jpg'],
        'description': 'A comprehensive workshop for teachers to learn modern teaching methods, digital classrooms, and student psychology.',
        'features': ['Interactive sessions', 'Digital tools training', 'Certificate of completion', 'Meals included'],
        'tags': ['teacher', 'education', 'training', 'school', 'pedagogy'],
        'target_segments': ['teacher', 'educator', 'government_employee'],
        'in_stock': True,
        'delivery_options': ['classroom'],
        'rating': 4.8,
        'reviews_count': 85,
        'created': datetime.now(timezone.utc)
    },
    {
        'id': 'prod_med_equip_01',
        'name': 'Professional Stethoscope & BP Monitor Kit',
        'category': 'health',
        'subcategory': 'equipment',
        'price': 25000,
        'currency': 'LKR',
        'images': ['/static/store/med_equip.jpg'],
        'description': 'High-quality medical equipment kit for doctors, nurses, and medical students.',
        'features': ['Premium Stethoscope', 'Digital BP Monitor', 'Carrying case', '2-year warranty'],
        'tags': ['doctor', 'nurse', 'health', 'medical', 'hospital'],
        'target_segments': ['healthcare_professional', 'doctor', 'nurse', 'student'],
        'in_stock': True,
        'delivery_options': ['delivery', 'pickup'],
        'rating': 4.7,
        'reviews_count': 230,
        'created': datetime.now(timezone.utc)
    }
]

for p in new_products:
    db.products.update_one({'id': p['id']}, {'$set': p}, upsert=True)

print('Added new products successfully.')
