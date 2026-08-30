import pandas as pd
import random
import os

def generate_cake_data(num_samples=1000):
    data = []
    
    flavors = ['chocolate', 'vanilla', 'fruit', 'nuts', 'spicy']
    complexities = ['minimal', 'standard', 'intricate']
    occasions = ['birthday', 'wedding', 'anniversary', 'other']
    
    for _ in range(num_samples):
        tiers = random.randint(1, 5)
        weight = round(random.uniform(0.5, 10.0), 1)
        flavor = random.choice(flavors)
        complexity = random.choice(complexities)
        occasion = random.choice(occasions)
        
        # Base price logic for synthetic data
        base_rate = 500
        if flavor == 'chocolate': base_rate = 700
        if flavor == 'fruit': base_rate = 650
        if flavor == 'nuts': base_rate = 800
        
        comp_mult = {'minimal': 0.8, 'standard': 1.0, 'intricate': 1.5}
        occ_mult = {'birthday': 1.0, 'wedding': 2.0, 'anniversary': 1.2, 'other': 1.0}
        
        tier_price = (tiers - 1) * 500
        price = (weight * base_rate * comp_mult[complexity] * occ_mult[occasion]) + tier_price
        
        # Add some noise
        price = price * random.uniform(0.9, 1.1)
        price = round(price / 50) * 50
        
        data.append({
            'tiers': tiers,
            'weight': weight,
            'flavor': flavor,
            'complexity': complexity,
            'occasion': occasion,
            'price': price
        })
        
    df = pd.DataFrame(data)
    os.makedirs('ai_features/data', exist_ok=True)
    df.to_csv('ai_features/data/cake_prices.csv', index=False)
    print(f"Generated {num_samples} samples and saved to ai_features/data/cake_prices.csv")

if __name__ == "__main__":
    generate_cake_data()
