import time
import random
from ml.hokm.env import HokmEnv
from pettingzoo.test import api_test

def run_random_episode():
    env = HokmEnv(render_mode="human")
    env.reset()
    
    print("\n--- Starting Random Episode ---")
    for agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        
        if termination or truncation:
            action = None
        else:
            # Filter invalid actions using action mask
            mask = observation["action_mask"]
            valid_actions = [i for i, valid in enumerate(mask) if valid]
            action = random.choice(valid_actions)
            
        env.step(action)
        
        if termination or truncation:
            print(f"Agent {agent} finished. Reward: {reward}")
            
    print("Episode finished.")
    env.close()

if __name__ == "__main__":
    print("Running PettingZoo API Test...")
    try:
        env = HokmEnv()
        api_test(env, num_cycles=10)
        print("API Test Passed!")
    except Exception as e:
        print(f"API Test Failed: {e}")
        exit(1)

    print("\nRunning Simulation with Random Agents...")
    run_random_episode()
