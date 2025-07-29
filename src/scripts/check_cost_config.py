#!/usr/bin/env python3
"""
Cost configuration checker and validator
Run this script to verify your cost settings are properly configured
"""

import os
import sys

# Add the project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import src.config.settings as settings
    from src.utils.cost_calculator import cost_calculator
    from src.utils.logger import logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def main():
    """
    Main function to check cost configuration
    """
    print("🔍 AI Agent Teaching System - Cost Configuration Checker")
    print("=" * 60)

    # Validate configuration
    print("\n📋 Validating Cost Configuration...")
    if cost_calculator.validate_cost_config():
        print("✅ Cost configuration is valid!")
    else:
        print("❌ Cost configuration has errors!")
        return False

    # Show cost summary
    print("\n💰 Current Cost Configuration:")
    summary = cost_calculator.get_cost_summary()

    print("\n🔧 Provider Costs (USD per 1K tokens):")
    for provider, costs in summary["providers"].items():
        print(f"  {provider.upper()}:")
        print(f"    Input:  ${costs['input_cost_per_1k']:.6f}")
        print(f"    Output: ${costs['output_cost_per_1k']:.6f}")

    print("\n⚙️  Settings:")
    print(f"  Cost Alert Threshold: ${summary['settings']['cost_alert_threshold']:.2f}")
    print(f"  Cost Tracking Enabled: {summary['settings']['cost_tracking_enabled']}")

    # Test cost calculation
    print("\n🧮 Test Cost Calculations:")
    test_cases = [
        ("gemini", 1000, 500),
        ("ollama", 1000, 500),
        ("openai", 1000, 500),
        ("claude", 1000, 500),
    ]

    for provider, input_tokens, output_tokens in test_cases:
        cost = cost_calculator.calculate_request_cost(
            provider, input_tokens, output_tokens
        )
        print(
            f"  {provider.upper()} ({input_tokens} in, {output_tokens} out): ${cost['total_cost']:.6f}"
        )

    print("\n🎯 Configuration Tips:")
    print("  • Ollama is free for local deployment")
    print("  • Gemini offers competitive pricing for cloud usage")
    print("  • Set COST_ALERT_THRESHOLD to monitor daily spending")
    print("  • Use .env file to customize pricing per your agreements")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
