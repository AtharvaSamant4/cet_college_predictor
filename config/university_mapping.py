# config/university_mapping.py

# Mapping of Maharashtra districts to their respective Home Universities for CET seats
DISTRICT_TO_UNIVERSITY = {
    # Mumbai University (MU)
    "Mumbai City": "Mumbai University",
    "Mumbai Suburban": "Mumbai University",
    "Mumbai": "Mumbai University",
    "Thane": "Mumbai University",
    "Palghar": "Mumbai University",
    "Raigad": "Mumbai University",
    "Ratnagiri": "Mumbai University",
    "Sindhudurg": "Mumbai University",
    
    # Savitribai Phule Pune University (SPPU)
    "Pune": "Savitribai Phule Pune University",
    "Ahmednagar": "Savitribai Phule Pune University",
    "Nashik": "Savitribai Phule Pune University",
    
    # Shivaji University (SUK)
    "Kolhapur": "Shivaji University",
    "Sangli": "Shivaji University",
    "Satara": "Shivaji University",
    
    # Punyashlok Ahilyadevi Holkar Solapur University (PAHSU)
    "Solapur": "Punyashlok Ahilyadevi Holkar Solapur University",
    
    # Dr. Babasaheb Ambedkar Marathwada University (BAMU)
    "Aurangabad": "Dr. Babasaheb Ambedkar Marathwada University",
    "Chhatrapati Sambhajinagar": "Dr. Babasaheb Ambedkar Marathwada University",
    "Jalna": "Dr. Babasaheb Ambedkar Marathwada University",
    "Beed": "Dr. Babasaheb Ambedkar Marathwada University",
    "Osmanabad": "Dr. Babasaheb Ambedkar Marathwada University",
    "Dharashiv": "Dr. Babasaheb Ambedkar Marathwada University",
    
    # Swami Ramanand Teerth Marathwada University (SRTMU)
    "Nanded": "Swami Ramanand Teerth Marathwada University",
    "Latur": "Swami Ramanand Teerth Marathwada University",
    "Parbhani": "Swami Ramanand Teerth Marathwada University",
    "Hingoli": "Swami Ramanand Teerth Marathwada University",
    
    # Sant Gadge Baba Amravati University (SGBAU)
    "Amravati": "Sant Gadge Baba Amravati University",
    "Akola": "Sant Gadge Baba Amravati University",
    "Washim": "Sant Gadge Baba Amravati University",
    "Buldhana": "Sant Gadge Baba Amravati University",
    "Yavatmal": "Sant Gadge Baba Amravati University",
    
    # Rashtrasant Tukadoji Maharaj Nagpur University (RTMNU)
    "Nagpur": "Rashtrasant Tukadoji Maharaj Nagpur University",
    "Wardha": "Rashtrasant Tukadoji Maharaj Nagpur University",
    "Bhandara": "Rashtrasant Tukadoji Maharaj Nagpur University",
    "Gondia": "Rashtrasant Tukadoji Maharaj Nagpur University",
    
    # Kavayitri Bahinabai Chaudhari North Maharashtra University (KBCNMU)
    "Jalgaon": "Kavayitri Bahinabai Chaudhari North Maharashtra University",
    "Dhule": "Kavayitri Bahinabai Chaudhari North Maharashtra University",
    "Nandurbar": "Kavayitri Bahinabai Chaudhari North Maharashtra University",
    
    # Gondwana University (GU)
    "Gadchiroli": "Gondwana University",
    "Chandrapur": "Gondwana University",
}

def get_home_university(district_name: str) -> str:
    if not district_name:
        return None
    
    # Try exact match first
    if district_name in DISTRICT_TO_UNIVERSITY:
        return DISTRICT_TO_UNIVERSITY[district_name]
        
    # Try case-insensitive / partial match
    lower_district = district_name.lower()
    for d, u in DISTRICT_TO_UNIVERSITY.items():
        if d.lower() in lower_district or lower_district in d.lower():
            return u
            
    return None
