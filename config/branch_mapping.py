BRANCH_MAP = {
    "CS": [
        "Computer Engineering",
        "Computer Engineering (Regional Language)",
        "Computer Engineering (Software Engineering)",
        "Computer Science",
        "Computer Science and Business Systems",
        "Computer Science and Design",
        "Computer Science and Engineering",
        "Computer Science and Engineering (Artificial Intelligence and Data Science)",
        "Computer Science and Engineering (Artificial Intelligence)",
        "Computer Science and Engineering (Cyber Security)",
        "Computer Science and Engineering (Internet of Things and Cyber Security Including Block Chain",
        "Computer Science and Engineering (IoT)",
        "Computer Science and Engineering(Artificial Intelligence and Machine Learning)",
        "Computer Science and Engineering(Cyber Security)",
        "Computer Science and Engineering(Data Science)",
        "Computer Science and Information Technology",
        "Computer Science and Technology",
        "Computer Technology",
        "Cyber Security",
        "Data Engineering",
        "Data Science",
    ],
    "IT": [
        "Information Technology",
    ],
    "AI_DS": [
        "Artificial Intelligence",
        "Artificial Intelligence (AI) and Data Science",
        "Artificial Intelligence and Data Science",
    ],
    "AI_ML": [
        "Artificial Intelligence and Machine Learning",
    ],
    "ENTC": [
        "5G",
        "ELECTRONICS AND COMMUNICATION ENGINEERING (BIO-MEDICAL ENGINEERING)",
        "Electrical Engg[Electronics and Power]",
        "Electrical, Electronics and Power",
        "Electronics Engineering",
        "Electronics Engineering ( VLSI Design and Technology)",
        "Electronics and Biomedical Engineering",
        "Electronics and Communication (Advanced Communication Technology)",
        "Electronics and Communication Engineering",
        "Electronics and Communication(Advanced Communication Technology)",
        "Electronics and Computer Engineering",
        "Electronics and Computer Science",
        "Electronics & Telecommunication Engineering",
        "Electronics and Telecommunication Engg",
        "VLSI",
    ],
    "ELECTRICAL": [
        "Electrical Engg [Electrical and Power]",
        "Electrical Engineering",
        "Electrical and Computer",
        "Electrical and Computer Engineering",
        "Electrical and ComputerEngineering",
        "Electrical and Electronics Engineering",
    ],
    "MECHANICAL": [
        "Manufacturing Science and Engineering",
        "MECHANICAL AND RAIL ENGINEERING",
        "Mechanical & Automation Engineering",
        "Mechanical Engineering",
        "Mechanical Engineering[Sandwich]",
        "Mechanical and Automation Engineering",
        "Mechanical and Mechatronics Engineering (Additive Manufacturing)",
        "Mechatronics Engineering",
        "Production Engineering",
        "Production Engineering[Sandwich]",
    ],
    "CIVIL": [
        "Architectural Assistantship",
        "Civil Engineering",
        "Civil Engineering (Structural Engineering)",
        "Civil Engineering with Computer Application",
        "Civil Engineering and Planning",
        "Civil and Environmental Engineering",
        "Civil and infrastructure Engineering",
        "Structural Engineering",
    ],
    "CHEMICAL": [
        "Chemical Engineering",
        "Dyestuff Technology",
        "Oil Fats and Waxes Technology",
        "Oil Technology",
        "Oil and Paints Technology",
        "Oil,Oleochemicals and Surfactants Technology",
        "Paints Technology",
        "Petro Chemical Engineering",
        "Petro Chemical Technology",
        "Pharmaceutical and Fine Chemical Technology",
        "Pharmaceuticals Chemistry and Technology",
        "Surface Coating Technology",
    ],
    "ROBOTICS": [
        "Automation and Robotics",
        "Industrial IoT",
        "Internet of Things (IoT)",
        "Robotics",
        "Robotics and Artificial Intelligence",
        "Robotics and Automation",
    ],
    "AUTOMOBILE": [
        "Automobile Engineering",
        "Automotive Technology",
        "Mechanical Engineering Automobile",
    ],
    "INSTRUMENTATION": [
        "Instrumentation Engineering",
        "Instrumentation and Control Engineering",
    ],
    "AERONAUTICAL": [
        "Aeronautical Engineering",
    ],
    "AGRICULTURE": [
        "Agricultural Engineering",
        "Agriculture Engineering",
    ],
    "BIOTECH": [
        "Bio Medical Engineering",
        "Bio Technology",
    ],
    "FOOD_TECH": [
        "Food Engineering",
        "Food Engineering and Technology",
        "Food Technology",
        "Food Technology And Management",
    ],
    "FIRE_SAFETY": [
        "Fire Engineering",
        "Safety and Fire Engineering",
    ],
    "TEXTILE": [
        "Fashion Technology",
        "Fibres and Textile Processing Technology",
        "Man Made Textile Technology",
        "Technical Textiles",
        "Textile Chemistry",
        "Textile Engineering / Technology",
        "Textile Plant Engineering",
        "Textile Technology",
    ],
    "MATERIALS": [
        "Metallurgy and Material Technology",
        "Plastic Technology",
        "Plastic and Polymer Engineering",
        "Plastic and Polymer Technology",
        "Polymer Engineering and Technology",
    ],
    "PRINTING_PACKAGING": [
        "Paper and Pulp Technology",
        "Printing Technology",
        "Printing and Packing Technology",
    ],
    "MINING": [
        "Mining Engineering",
    ],
    "LOGISTICS": [
        "Logistics",
    ],
}


BRANCH_ALIASES = {
    "AI": ["AI_DS", "AI_ML"],
    "AIDS": ["AI_DS"],
    "AI&DS": ["AI_DS"],
    "AI_DS": ["AI_DS"],
    "AIML": ["AI_ML"],
    "AI&ML": ["AI_ML"],
    "AI_ML": ["AI_ML"],
    "CSE": ["CS"],
    "COMPUTER": ["CS"],
    "COMPUTER_SCIENCE": ["CS"],
    "EXTC": ["ENTC"],
    "E_AND_TC": ["ENTC"],
}


def get_branches_for_input(branch_input):
    branch_key = branch_input.strip().upper().replace(" ", "_")
    group_keys = BRANCH_ALIASES.get(branch_key, [branch_key])

    branches = []
    for group_key in group_keys:
        branches.extend(BRANCH_MAP.get(group_key, []))

    return branches
