import os
import ray
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.tune.registry import register_env
from pettingzoo.test import api_test

from ml.hokm.env import HokmEnv

def env_creator(config):
    return HokmEnv()

def train():
    # Register the environment
    register_env("hokm_v2", env_creator)

    # Initialize Ray
    ray.init()

    # Configure PPO
    config = (
        PPOConfig()
        .environment("hokm_v2")
        .framework("torch")
        .rollouts(num_rollout_workers=1)
        .training(
            model={
                "fcnet_hiddens": [256, 256],
                "fcnet_activation": "relu",
            }
        )
        .multi_agent(
            policies={"shared_policy"},
            policy_mapping_fn=lambda agent_id, episode, worker, **kwargs: "shared_policy",
        )
    )

    # Run training
    tune.run(
        "PPO",
        config=config.to_dict(),
        stop={"training_iteration": 10},
        checkpoint_freq=5,
        storage_path=os.path.abspath("./results"),
    )

    ray.shutdown()

if __name__ == "__main__":
    # Basic API test
    print("Running API test...")
    env = HokmEnv()
    api_test(env, num_cycles=10)
    print("API test passed!")

    print("Starting training...")
    train()
