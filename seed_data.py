from app import app, db, Category, Medicine, User
from datetime import datetime, timedelta
import random

# Categories
HEALTH_CATEGORIES = [
    "Must Haves", "Sexual Wellness", "Personal Care", "Winter Store",
    "Vitamin Store", "Health Concerns", "Health Food and Drinks",
    "Heart Care", "Diabetes Essentials", "Ayurvedic Care",
    "Mother and Baby Care", "Mobility & Elderly Care", "Sports Nutrition",
    "Healthcare Devices", "Skin Care"
]

# Exact Product Image Mapping
# Using specific Unsplash/Pexels photos that visually match the specific medicine type
MEDICINE_IMAGES = {
    # Pills / Tablets
    "Dolo 650mg": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Crocin Advance": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80", # Paracetamol look
    "Calpol 500mg": "https://plus.unsplash.com/premium_photo-1673953509975-576678fa6710?auto=format&fit=crop&w=400&q=80", # Pink/White pills
    "Combiflam": "https://images.unsplash.com/photo-1550572017-edcdb375d042?auto=format&fit=crop&w=400&q=80", # Orange pills
    "Disprin Regular": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=400&q=80", # White effervescent
    "Allegra 120mg": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Cetzine 10mg": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=400&q=80",
    "Cetirizine 10mg": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=400&q=80",
    "Montair LC": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Pantocid 40": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=400&q=80",
     "Glycomet GP 1": "https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=400&q=80",
    "Glycomet GP 2": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Galvus Met": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Janumet 50/500": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Metformin 500": "https://images.unsplash.com/photo-1577401239170-897942555fb3?auto=format&fit=crop&w=400&q=80",
    "Sugar Free Gold": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=400&q=80",
    "Atorva 10mg": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Telma 40": "https://images.unsplash.com/photo-1550572017-edcdb375d042?auto=format&fit=crop&w=400&q=80",
    "Ecosprin 75": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=400&q=80",
    "Limcee 500mg": "https://images.unsplash.com/photo-1550572017-edcdb375d042?auto=format&fit=crop&w=400&q=80", # Orange chewable look
    "Shelcal 500": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Neurobion Forte": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80", # Pinkish
    "Zincovit": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80",
    "Supradyn Daily": "https://images.unsplash.com/photo-1585435557343-3b092031a831?auto=format&fit=crop&w=400&q=80",

    # Syrups / Liquids
    "Benadryl Syrup": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?auto=format&fit=crop&w=400&q=80", # Red liquid
    "Ascoril LS": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=400&q=80",
    "Grilinctus Syrup": "https://images.unsplash.com/photo-1512069772995-ec65ed45afd6?auto=format&fit=crop&w=400&q=80",
    "Dettol Liquid": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=400&q=80", # Amber bottle
    "Savlon Antiseptic": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=400&q=80", # Amber bottle
    "Digene Gel Orange": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?auto=format&fit=crop&w=400&q=80", # Pink/Orange liquid
    "Gelusil Antacid": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?auto=format&fit=crop&w=400&q=80",
    "Cetaphil Cleanser": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80", # Gentle bottle
    "Listerine Mouthwash": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?auto=format&fit=crop&w=400&q=80", # Blue liquid
    "Johnsons Baby Oil": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80", # Clear bottle

    # Creams / Ointments
    "Vicks VapoRub": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80", # Blue tub look
    "Moov Pain Relief": "https://images.unsplash.com/photo-1556228578-0d89b128308f?auto=format&fit=crop&w=400&q=80", # Tube
    "Volini Gel": "https://images.unsplash.com/photo-1556228578-0d89b128308f?auto=format&fit=crop&w=400&q=80",
    "Iodex Balm": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80", # Green jar
    "Betadine Ointment": "https://images.unsplash.com/photo-1556228578-0d89b128308f?auto=format&fit=crop&w=400&q=80",
    "Boroline Cream": "https://images.unsplash.com/photo-1629198688000-71f23e745b6e?auto=format&fit=crop&w=400&q=80", # Green tube
    "Derma Co Sunscreen": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80",
    "Nivea Soft": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80", # White jar
    "Himalaya Baby Lotion": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80",
    "Colgate Total": "https://images.unsplash.com/photo-1556228578-0d89b128308f?auto=format&fit=crop&w=400&q=80",
    "Sensodyne Repair": "https://images.unsplash.com/photo-1556228578-0d89b128308f?auto=format&fit=crop&w=400&q=80",
    "Vaseline Jelly": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80", # Jar
    "Nivea Body Lotion": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80",

    # Inhalers / Sprays / Drops
    "Otrivin Nasal Drops": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=400&q=80",
    "Nasivion Adult": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=400&q=80",
    "Minimalist Salicylic": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=400&q=80", # Dropper bottle
    "Bold Care Spray": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=400&q=80",

    # Powders / Jars
    "Bournvita 500g": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80", # Brown jar
    "Horlicks Classic": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80", # Jar
    "Ensure Vanilla": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80",
    "MuscleBlaze Whey": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80", # Big black jar look
    "ON Gold Whey": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80",
    "Glucon-D Orange": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Box
    "Cerelac Wheat": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80",
    "Eno Regular": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Sachet/Pack

    # Devices
    "Thermometer Digital": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=400&q=80",
    "Dr. Morepen BP": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=400&q=80", # BP machine look
    "Oximeter Digital": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=400&q=80", # Finger device
    "Vaporizer Steamer": "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?auto=format&fit=crop&w=400&q=80",
    "Accu-Chek Active": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=400&q=80", # Meter
    "OneTouch Select": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=400&q=80",

    # Others
    "Band-Aid Washproof": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Box
    "Cotton Roll": "https://mingde.en.made-in-china.com/product/rwsTXyeclHYD/China-100-Pure-Cotton-High-Absorbency-Medical-Cotton-Wool-Roll.html", # White fluff
    "Dettol Soap": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Box
    "Whisper Ultra": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Packet
    "Pampers Active M": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Large packet
    "MamyPoko Pants L": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Large packet
    "Manforce Strawberry": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Box
    "Durex Air Thin": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80", # Box
}

# 100+ Real-Life Medicines Data (Exact same logic as previous)
REAL_MEDICINES_DB = [
    # --- Must Haves (Fever/Pain) ---
    {"name": "Dolo 650mg", "cat": "Must Haves", "type": "Tablet", "unit": "Strip of 15", "price": 30.00},
    {"name": "Crocin Advance", "cat": "Must Haves", "type": "Tablet", "unit": "Strip of 20", "price": 25.50},
    {"name": "Calpol 500mg", "cat": "Must Haves", "type": "Tablet", "unit": "Strip of 15", "price": 18.00},
    {"name": "Combiflam", "cat": "Must Haves", "type": "Tablet", "unit": "Strip of 20", "price": 45.00},
    {"name": "Disprin Regular", "cat": "Must Haves", "type": "Tablet", "unit": "Strip of 10", "price": 12.00},
    {"name": "Vicks VapoRub", "cat": "Must Haves", "type": "Ointment", "unit": "Bottle of 50g", "price": 145.00},
    {"name": "Betadine Ointment", "cat": "Must Haves", "type": "Ointment", "unit": "Tube of 20g", "price": 110.00},
    {"name": "Moov Pain Relief", "cat": "Must Haves", "type": "Cream", "unit": "Tube of 50g", "price": 160.00},
    {"name": "Volini Gel", "cat": "Must Haves", "type": "Cream", "unit": "Tube of 30g", "price": 125.00},
    {"name": "Iodex Balm", "cat": "Must Haves", "type": "Ointment", "unit": "Bottle of 40g", "price": 130.00},
    {"name": "Dettol Liquid", "cat": "Must Haves", "type": "Syrup", "unit": "Bottle of 200ml", "price": 180.00},
    {"name": "Savlon Antiseptic", "cat": "Must Haves", "type": "Syrup", "unit": "Bottle of 200ml", "price": 160.00},
    {"name": "Band-Aid Washproof", "cat": "Must Haves", "type": "Device", "unit": "Pack of 100", "price": 150.00},
    {"name": "Thermometer Digital", "cat": "Must Haves", "type": "Device", "unit": "Unit", "price": 250.00},
    {"name": "Cotton Roll", "cat": "Must Haves", "type": "Device", "unit": "Pack of 50gm", "price": 40.00},

    # --- Health Concerns (Cold/Cough/Digestion/Allergy) ---
    {"name": "Benadryl Syrup", "cat": "Health Concerns", "type": "Syrup", "unit": "Bottle of 150ml", "price": 130.00},
    {"name": "Cetirizine 10mg", "cat": "Health Concerns", "type": "Tablet", "unit": "Strip of 10", "price": 18.00},
    {"name": "Ascoril LS", "cat": "Health Concerns", "type": "Syrup", "unit": "Bottle of 100ml", "price": 115.00},
    {"name": "Grilinctus Syrup", "cat": "Health Concerns", "type": "Syrup", "unit": "Bottle of 100ml", "price": 108.00},
    {"name": "Otrivin Nasal Drops", "cat": "Health Concerns", "type": "Drops", "unit": "Bottle of 10ml", "price": 95.00},
    {"name": "Nasivion Adult", "cat": "Health Concerns", "type": "Drops", "unit": "Bottle of 10ml", "price": 88.00},
    {"name": "Allegra 120mg", "cat": "Health Concerns", "type": "Tablet", "unit": "Strip of 10", "price": 190.00},
    {"name": "Cetzine 10mg", "cat": "Health Concerns", "type": "Tablet", "unit": "Strip of 15", "price": 25.00},
    {"name": "Montair LC", "cat": "Health Concerns", "type": "Tablet", "unit": "Strip of 10", "price": 160.00},
    {"name": "Digene Gel Orange", "cat": "Health Concerns", "type": "Syrup", "unit": "Bottle of 200ml", "price": 120.00},
    {"name": "Gelusil Antacid", "cat": "Health Concerns", "type": "Syrup", "unit": "Bottle of 200ml", "price": 110.00},
    {"name": "Eno Regular", "cat": "Health Concerns", "type": "Powder", "unit": "Sachet", "price": 8.00},
    {"name": "Pudin Hara", "cat": "Health Concerns", "type": "Capsule", "unit": "Strip of 10", "price": 30.00},
    {"name": "Omenez 20", "cat": "Health Concerns", "type": "Capsule", "unit": "Strip of 20", "price": 140.00},
    {"name": "Pantocid 40", "cat": "Health Concerns", "type": "Tablet", "unit": "Strip of 15", "price": 155.00},

    # --- Diabetes Essentials ---
    {"name": "Glycomet GP 1", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Strip of 15", "price": 110.00},
    {"name": "Glycomet GP 2", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Strip of 15", "price": 145.00},
    {"name": "Galvus Met", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Strip of 10", "price": 280.00},
    {"name": "Janumet 50/500", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Strip of 15", "price": 450.00},
    {"name": "Metformin 500", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Strip of 10", "price": 45.00},
    {"name": "Accu-Chek Active", "cat": "Diabetes Essentials", "type": "Device", "unit": "Pack of 50", "price": 950.00},
    {"name": "OneTouch Select", "cat": "Diabetes Essentials", "type": "Device", "unit": "Pack of 50", "price": 1150.00},
    {"name": "Sugar Free Gold", "cat": "Diabetes Essentials", "type": "Tablet", "unit": "Pack of 500", "price": 285.00},

    # --- Heart Care ---
    {"name": "Atorva 10mg", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 15", "price": 98.00},
    {"name": "Atorva 20mg", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 15", "price": 185.00},
    {"name": "Rosuvas 10", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 10", "price": 180.00},
    {"name": "Telma 40", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 15", "price": 220.00},
    {"name": "Telma AM", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 15", "price": 290.00},
    {"name": "Ecosprin 75", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 14", "price": 5.00},
    {"name": "Ecosprin 150", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 14", "price": 9.00},
    {"name": "Ciplar LA 40", "cat": "Heart Care", "type": "Tablet", "unit": "Strip of 15", "price": 110.00},

    # --- Skin Care ---
    {"name": "Cetaphil Cleanser", "cat": "Skin Care", "type": "Syrup", "unit": "Bottle of 125ml", "price": 305.00},
    {"name": "Minimalist Salicylic", "cat": "Skin Care", "type": "Drops", "unit": "Bottle of 30ml", "price": 545.00},
    {"name": "Derma Co Sunscreen", "cat": "Skin Care", "type": "Cream", "unit": "Tube of 50g", "price": 499.00},
    {"name": "Boroline Cream", "cat": "Skin Care", "type": "Cream", "unit": "Tube of 20g", "price": 40.00},
    {"name": "Nivea Soft", "cat": "Skin Care", "type": "Cream", "unit": "Jar of 100ml", "price": 190.00},
    {"name": "Candid Powder", "cat": "Skin Care", "type": "Powder", "unit": "Bottle of 100g", "price": 145.00},
    {"name": "Fusen Cream", "cat": "Skin Care", "type": "Cream", "unit": "Tube of 15g", "price": 95.00},
    {"name": "Betnovate C", "cat": "Skin Care", "type": "Cream", "unit": "Tube of 30g", "price": 65.00},
    {"name": "BoroPlus", "cat": "Skin Care", "type": "Cream", "unit": "Tube of 40g", "price": 55.00},

    # --- Vitamin Store ---
    {"name": "Becosules Z", "cat": "Vitamin Store", "type": "Capsule", "unit": "Strip of 20", "price": 45.00},
    {"name": "Limcee 500mg", "cat": "Vitamin Store", "type": "Tablet", "unit": "Strip of 15", "price": 22.00},
    {"name": "Shelcal 500", "cat": "Vitamin Store", "type": "Tablet", "unit": "Strip of 15", "price": 118.00},
    {"name": "Neurobion Forte", "cat": "Vitamin Store", "type": "Tablet", "unit": "Strip of 30", "price": 38.00},
    {"name": "Zincovit", "cat": "Vitamin Store", "type": "Tablet", "unit": "Strip of 15", "price": 105.00},
    {"name": "Supradyn Daily", "cat": "Vitamin Store", "type": "Tablet", "unit": "Strip of 15", "price": 55.00},
    {"name": "Evion 400", "cat": "Vitamin Store", "type": "Capsule", "unit": "Strip of 10", "price": 32.00},
    {"name": "A to Z Gold", "cat": "Vitamin Store", "type": "Capsule", "unit": "Strip of 15", "price": 180.00},
    {"name": "Revital H", "cat": "Vitamin Store", "type": "Capsule", "unit": "Strip of 10", "price": 110.00},

    # --- Health Food / Sports Nutrition ---
    {"name": "Bournvita 500g", "cat": "Health Food and Drinks", "type": "Powder", "unit": "Jar of 500g", "price": 280.00},
    {"name": "Horlicks Classic", "cat": "Health Food and Drinks", "type": "Powder", "unit": "Jar of 500g", "price": 285.00},
    {"name": "Ensure Vanilla", "cat": "Health Food and Drinks", "type": "Powder", "unit": "Box of 400g", "price": 640.00},
    {"name": "Protinex Tasty", "cat": "Sports Nutrition", "type": "Powder", "unit": "Jar of 250g", "price": 450.00},
    {"name": "MuscleBlaze Whey", "cat": "Sports Nutrition", "type": "Powder", "unit": "Jar of 1kg", "price": 1899.00},
    {"name": "ON Gold Whey", "cat": "Sports Nutrition", "type": "Powder", "unit": "Jar of 2lbs", "price": 3100.00},
    {"name": "Glucon-D Orange", "cat": "Health Food and Drinks", "type": "Powder", "unit": "Box of 500g", "price": 150.00},

    # --- Personal Care ---
    {"name": "Dettol Soap", "cat": "Personal Care", "type": "Device", "unit": "Pack of 4", "price": 160.00},
    {"name": "Colgate Total", "cat": "Personal Care", "type": "Cream", "unit": "Tube of 120g", "price": 140.00},
    {"name": "Sensodyne Repair", "cat": "Personal Care", "type": "Cream", "unit": "Tube of 100g", "price": 220.00},
    {"name": "Listerine Mouthwash", "cat": "Personal Care", "type": "Syrup", "unit": "Bottle of 250ml", "price": 150.00},
    {"name": "Whisper Ultra", "cat": "Personal Care", "type": "Device", "unit": "Pack of 15", "price": 180.00},
    
    # --- Mother and Baby ---
    {"name": "Pampers Active M", "cat": "Mother and Baby Care", "type": "Device", "unit": "Pack of 66", "price": 899.00},
    {"name": "MamyPoko Pants L", "cat": "Mother and Baby Care", "type": "Device", "unit": "Pack of 50", "price": 850.00},
    {"name": "Johnsons Baby Oil", "cat": "Mother and Baby Care", "type": "Syrup", "unit": "Bottle of 200ml", "price": 250.00},
    {"name": "Himalaya Baby Lotion", "cat": "Mother and Baby Care", "type": "Cream", "unit": "Bottle of 200ml", "price": 165.00},
    {"name": "Cerelac Wheat", "cat": "Mother and Baby Care", "type": "Powder", "unit": "Box of 300g", "price": 275.00},
    {"name": "Woodwards Gripe", "cat": "Mother and Baby Care", "type": "Syrup", "unit": "Bottle of 130ml", "price": 60.00},

    # --- Ayurvedic ---
    {"name": "Dabur Chyawanprash", "cat": "Ayurvedic Care", "type": "Cream", "unit": "Jar of 950g", "price": 395.00},
    {"name": "Himalaya Liv.52", "cat": "Ayurvedic Care", "type": "Tablet", "unit": "Bottle of 60", "price": 150.00},
    {"name": "Patanjali Aloe Vera", "cat": "Ayurvedic Care", "type": "Cream", "unit": "Tube of 150ml", "price": 90.00},
    {"name": "Isabgol Husk", "cat": "Ayurvedic Care", "type": "Powder", "unit": "Pack of 100g", "price": 115.00},
    {"name": "Zandu Balm", "cat": "Ayurvedic Care", "type": "Ointment", "unit": "Bottle of 25g", "price": 85.00},
    {"name": "Triphala Churna", "cat": "Ayurvedic Care", "type": "Powder", "unit": "Jar of 100g", "price": 75.00},

    # --- Sexual Wellness ---
    {"name": "Manforce Strawberry", "cat": "Sexual Wellness", "type": "Device", "unit": "Pack of 10", "price": 90.00},
    {"name": "Durex Air Thin", "cat": "Sexual Wellness", "type": "Device", "unit": "Pack of 10", "price": 220.00},
    {"name": "Skore Dots", "cat": "Sexual Wellness", "type": "Device", "unit": "Pack of 10", "price": 110.00},
    {"name": "Bold Care Spray", "cat": "Sexual Wellness", "type": "Drops", "unit": "Bottle of 20g", "price": 499.00},
    {"name": "Shilajit Gold", "cat": "Sexual Wellness", "type": "Capsule", "unit": "Bottle of 20", "price": 850.00},

    # --- Winter Store ---
    {"name": "Vaseline Jelly", "cat": "Winter Store", "type": "Cream", "unit": "Jar of 50g", "price": 55.00},
    {"name": "Nivea Body Lotion", "cat": "Winter Store", "type": "Cream", "unit": "Bottle of 400ml", "price": 325.00},
    {"name": "Ponds Moisturizer", "cat": "Winter Store", "type": "Cream", "unit": "Box of 100g", "price": 190.00},
    {"name": "BoroPlus Lotion", "cat": "Winter Store", "type": "Cream", "unit": "Bottle of 200ml", "price": 180.00},
    {"name": "Dove Body Wash", "cat": "Winter Store", "type": "Syrup", "unit": "Bottle of 250ml", "price": 220.00},

    # --- Healthcare Devices ---
    {"name": "Dr. Morepen BP", "cat": "Healthcare Devices", "type": "Device", "unit": "Unit", "price": 1200.00},
    {"name": "Omron Thermometer", "cat": "Healthcare Devices", "type": "Device", "unit": "Unit", "price": 250.00},
    {"name": "Vaporizer Steamer", "cat": "Healthcare Devices", "type": "Device", "unit": "Unit", "price": 350.00},
    {"name": "Oximeter Digital", "cat": "Healthcare Devices", "type": "Device", "unit": "Unit", "price": 800.00},
    {"name": "Nebulizer Kit", "cat": "Healthcare Devices", "type": "Device", "unit": "Unit", "price": 1600.00},
]

TYPE_DEFAULTS = {
    "Tablet": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80",
    "Capsule": "https://images.unsplash.com/photo-1628771065518-0d82f1938462?auto=format&fit=crop&w=400&q=80",
    "Syrup": "https://images.unsplash.com/photo-1624454002302-36b824d7bd0a?auto=format&fit=crop&w=400&q=80",
    "Cream": "https://images.unsplash.com/photo-1556228720-1987ba42a67d?auto=format&fit=crop&w=400&q=80",
    "Ointment": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=400&q=80",
    "Device": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=400&q=80",
    "Powder": "https://images.unsplash.com/photo-1594110834316-4404e019685e?auto=format&fit=crop&w=400&q=80",
    "Drops": "https://images.unsplash.com/photo-1603398938378-e54eab446dde?auto=format&fit=crop&w=400&q=80",
    "Injection": "https://images.unsplash.com/photo-1585822946522-f38b299e9842?auto=format&fit=crop&w=400&q=80",
}

def seed_data():
    with app.app_context():
        print("Starting Database Reset & Population...")
        
        db.drop_all()
        db.create_all()
        print("Database Schema Created.")

        # Create Admin with Store Manager Role
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            # Explicitly assign store_manager role
            admin_user = User(username='admin', password_hash=generate_password_hash('admin123'), role='store_manager')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created with Store Manager role.")
        
        # Ensure admin_user is fetched after commit if it was just created
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
             print("Error: Admin user could not be found or created.")
             return

        # Create Categories
        categories_map = {}
        for cat_name in HEALTH_CATEGORIES:
            category = Category(name=cat_name)
            db.session.add(category)
            categories_map[cat_name] = category
        db.session.commit()
        
        # Reload categories to get IDs
        for cat_name in HEALTH_CATEGORIES:
            categories_map[cat_name] = Category.query.filter_by(name=cat_name).first()

        medicines_to_add = []
        for data in REAL_MEDICINES_DB:
             # Expiry Logic: Mixed states
            rand_val = random.random()
            if rand_val < 0.05: # 5% Expired
                days_diff = random.randint(1, 100)
                expiry = datetime.now() - timedelta(days=days_diff)
                quantity = random.randint(0, 5) # Low stock if expired
            elif rand_val < 0.15: # 10% Near Expiry
                days_diff = random.randint(1, 58)
                expiry = datetime.now() + timedelta(days=days_diff)
                quantity = random.randint(10, 40)
            else: # 85% Safe
                days_diff = random.randint(90, 730)
                expiry = datetime.now() + timedelta(days=days_diff)
                quantity = random.randint(20, 100)
            
            # Select EXACT image if mapped, else None (User must add manually)
            selected_image = MEDICINE_IMAGES.get(data['name'])
            # if not selected_image:
            #     selected_image = TYPE_DEFAULTS.get(data['type'], TYPE_DEFAULTS['Tablet'])

            med = Medicine(
                name=data['name'],
                category_id=categories_map[data['cat']].id,
                price=data['price'],
                quantity=quantity,
                expiry_date=expiry.date(),
                availability=True,
                medicine_type=data['type'],
                unit=data['unit'],
                image_url=selected_image
            )
            medicines_to_add.append(med)
            
        db.session.bulk_save_objects(medicines_to_add)
        db.session.commit()
        print(f"Successfully populated {len(medicines_to_add)} medicines with EXACT realistic images.")

if __name__ == "__main__":
    seed_data()
