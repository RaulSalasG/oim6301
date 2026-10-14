import bmi
#result=bmi.compute(70.1,1.72)
#print(result)

people = [
    {"name": "Alice", "height": 1.75, "weight": 70},
    {"name": "Bob", "height": 1.82, "weight": 85},
    {"name": "Charlie", "height": 1.68, "weight": 65},
    {"name": "David", "height": 1.90, "weight": 92},
    {"name": "Emma", "height": 1.60, "weight": 55},
    {"name": "Frank", "height": 1.78, "weight": 76},
    {"name": "Grace", "height": 1.72, "weight": 63},
    {"name": "Henry", "height": 1.85, "weight": 88},
    {"name": "Isabella", "height": 1.65, "weight": 59},
    {"name": "Jack", "height": 1.73, "weight": 95},
    {"name": "Sophia", "height": 1.70, "weight": 72},
    {"name": "Lucas", "height": 1.80, "weight": 68},
    {"name": "Olivia", "height": 1.58, "weight": 52},
    {"name": "James", "height": 1.88, "weight": 105},
    {"name": "Mia", "height": 1.67, "weight": 80}
]

for person in people:
    print(person)
    print(person['height'])
    #print(people['height'])
    print()