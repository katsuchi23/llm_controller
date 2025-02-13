import random

def random_point():
    x = random.randint(0, 140) / 10
    y = (random.randint(0, 90) / 10) - 3
    theta = 0
    return (x,y,theta)