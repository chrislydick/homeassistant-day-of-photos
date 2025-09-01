#!/usr/bin/env python3
"""
Simple script to edit the LLM configuration file.
"""

import json
import os
from pathlib import Path

def edit_config():
    """Edit the LLM configuration file."""
    config_path = Path("llm_config.json")
    
    if not config_path.exists():
        print("❌ Configuration file not found. Run the main script first to create it.")
        return
    
    # Load current config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("🔧 LLM Configuration Editor")
    print("=" * 50)
    print("Current configuration:")
    print(json.dumps(config, indent=2))
    print("\n" + "=" * 50)
    
    # Ask what to edit
    print("\nWhat would you like to edit?")
    print("1. Vision analysis prompt")
    print("2. Negative indicators")
    print("3. Positive indicators")
    print("4. Scoring values")
    print("5. LLM settings")
    print("6. Logging settings")
    print("7. Save and exit")
    
    while True:
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            print("\nCurrent vision analysis prompt:")
            print(config["prompts"]["vision_analysis"])
            new_prompt = input("\nEnter new prompt (or press Enter to keep current): ").strip()
            if new_prompt:
                config["prompts"]["vision_analysis"] = new_prompt
                print("✅ Prompt updated!")
        
        elif choice == "2":
            print("\nCurrent negative indicators:")
            print(config["evaluation"]["negative_indicators"])
            new_indicators = input("\nEnter new indicators (comma-separated): ").strip()
            if new_indicators:
                config["evaluation"]["negative_indicators"] = [x.strip() for x in new_indicators.split(",")]
                print("✅ Negative indicators updated!")
        
        elif choice == "3":
            print("\nCurrent positive indicators:")
            print(config["evaluation"]["positive_indicators"])
            new_indicators = input("\nEnter new indicators (comma-separated): ").strip()
            if new_indicators:
                config["evaluation"]["positive_indicators"] = [x.strip() for x in new_indicators.split(",")]
                print("✅ Positive indicators updated!")
        
        elif choice == "4":
            print("\nCurrent scoring values:")
            print(f"Good score: {config['evaluation']['scoring']['good_score']}")
            print(f"Bad score: {config['evaluation']['scoring']['bad_score']}")
            print(f"Neutral score: {config['evaluation']['scoring']['neutral_score']}")
            
            new_good = input("Enter new good score (0.0-1.0): ").strip()
            if new_good:
                config["evaluation"]["scoring"]["good_score"] = float(new_good)
            
            new_bad = input("Enter new bad score (0.0-1.0): ").strip()
            if new_bad:
                config["evaluation"]["scoring"]["bad_score"] = float(new_bad)
            
            new_neutral = input("Enter new neutral score (0.0-1.0): ").strip()
            if new_neutral:
                config["evaluation"]["scoring"]["neutral_score"] = float(new_neutral)
            
            print("✅ Scoring values updated!")
        
        elif choice == "5":
            print("\nCurrent LLM settings:")
            print(f"Model: {config['llm_settings']['model']}")
            print(f"Temperature: {config['llm_settings']['temperature']}")
            print(f"Timeout: {config['llm_settings']['timeout']}")
            
            new_model = input("Enter new model name: ").strip()
            if new_model:
                config["llm_settings"]["model"] = new_model
            
            new_temp = input("Enter new temperature (0.0-1.0): ").strip()
            if new_temp:
                config["llm_settings"]["temperature"] = float(new_temp)
            
            new_timeout = input("Enter new timeout (seconds): ").strip()
            if new_timeout:
                config["llm_settings"]["timeout"] = int(new_timeout)
            
            print("✅ LLM settings updated!")
        
        elif choice == "6":
            print("\nCurrent logging settings:")
            print(f"Show LLM responses: {config['logging']['show_llm_responses']}")
            print(f"Show evaluation details: {config['logging']['show_evaluation_details']}")
            
            show_responses = input("Show LLM responses? (y/n): ").strip().lower()
            if show_responses in ['y', 'yes']:
                config["logging"]["show_llm_responses"] = True
            elif show_responses in ['n', 'no']:
                config["logging"]["show_llm_responses"] = False
            
            show_details = input("Show evaluation details? (y/n): ").strip().lower()
            if show_details in ['y', 'yes']:
                config["logging"]["show_evaluation_details"] = True
            elif show_details in ['n', 'no']:
                config["logging"]["show_evaluation_details"] = False
            
            print("✅ Logging settings updated!")
        
        elif choice == "7":
            # Save configuration
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ Configuration saved!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1-7.")

if __name__ == "__main__":
    edit_config()
