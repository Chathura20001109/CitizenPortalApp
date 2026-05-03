
# recommendation_engine.py
from datetime import datetime
from bson import ObjectId

class RecommendationEngine:
    def __init__(self, db):
        self.db = db
        self.users = db["users"]
        self.ads = db["ads"]
        self.products = db["products"]

    def get_user_segment(self, user_id):
        if not user_id: return "anonymous"
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
        except:
            return "anonymous"
            
        if not user: return "anonymous"
        
        segments = []
        profile = user.get("profile", {}).get("basic", {})
        extended = user.get("extended_profile", {})
        
        age = profile.get("age")
        if age:
            if 18 <= age <= 25: segments.append("young_adult")
            elif 26 <= age <= 40: segments.append("mid_career")
            elif age > 40: segments.append("senior")
            
        job = extended.get("career", {}).get("current_job", "").lower()
        if "government" in job: segments.append("government_employee")
        if "student" in job: segments.append("student")
        
        if extended.get("family", {}).get("children"):
            segments.append("parent")
            
        return segments

    def generate_education_recommendations(self, user_id):
        if not user_id: return []
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
        except:
            return []
            
        if not user: return []
        
        recs = []
        extended = user.get("extended_profile", {})
        family_ages = extended.get("family", {}).get("children_ages", [])
        
        # Child education recommendations
        for age in family_ages:
            try:
                age = int(age)
                if 14 <= age <= 16:
                    recs.append({
                        "type": "child_education",
                        "title": "O/L Support",
                        "message": "Tuition for O/L exams available.",
                        "link": "/store?category=education"
                    })
                elif 17 <= age <= 19:
                    recs.append({
                        "type": "child_education",
                        "title": "A/L Guidance",
                        "message": "Career guidance after A/L.",
                        "link": "/store?category=education"
                    })
                elif 8 <= age <= 14:
                    recs.append({
                        "type": "child_education",
                        "title": "Kids Coding",
                        "message": "Coding classes for kids.",
                        "link": "/store?product=prod_kids_coding"
                    })
            except:
                pass

        # Adult education
        interests = extended.get("interests", {}).get("learning_interests", [])
        if "degree_programs" in interests:
            recs.append({
                "type": "adult_education",
                "title": "Complete Your Degree",
                "message": "Weekend degree programs for professionals.",
                "link": "/store?product=prod_degree_01"
            })
            
        return recs

    def get_personalized_ads(self, user_id):
        # fetch active ads
        active_ads = list(self.ads.find({"active": True}))
        if not active_ads: return []
        
        segments = self.get_user_segment(user_id)
        
        interests = []
        if user_id:
            try:
                user = self.users.find_one({"_id": ObjectId(user_id)})
                if user:
                    interests = user.get("extended_profile", {}).get("interests", {}).get("learning_interests", [])
            except:
                pass
                
        # Score ads
        scored_ads = []
        for ad in active_ads:
            score = 0
            ad_tags = ad.get('tags', [])
            ad_segments = ad.get('target_segments', [])
            
            # Intersection of segments
            common_segments = set(segments) & set(ad_segments)
            score += len(common_segments) * 10
            
            # Intersection of interests (rough match)
            for interest in interests:
                if interest in ad_tags:
                    score += 5
                    
            scored_ads.append((ad, score))
            
        scored_ads.sort(key=lambda x: x[1], reverse=True)
        # Return top 3 ads only, formatted for frontend
        final_ads = []
        for ad, score in scored_ads[:3]:
            # sanitize ObjectId
            ad["_id"] = str(ad["_id"])
            # sanitize datetime
            for k, v in ad.items():
                if isinstance(v, datetime):
                    ad[k] = v.isoformat()
            final_ads.append(ad)
            
        return final_ads
