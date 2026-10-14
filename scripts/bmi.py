def compute_bmi(weight,height):
    bmi=weight/(height**2)
    return bmi


def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

def main():
    weight = float(input("Enter your weight in kg: "))
    height = float(input("Enter your height in meters: "))
    bmi_v = compute_bmi(weight,height)
    result=classify_bmi(bmi_v)
    print(f'Your bmi is {bmi_v}, and your category is {result}')


if __name__=="__main__":
    main()