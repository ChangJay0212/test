#!/usr/bin/env python3
"""
測試 Ollama 引擎的工具功能
"""
import sys
sys.path.append('/app')

from llm_engines.factory import LLMEngineFactory
from tools.web_search import WebSearchTool

def test_ollama_tools():
    """測試 Ollama 引擎與工具的整合"""
    
    print("🧪 測試 Ollama 引擎工具功能")
    print("=" * 50)
    
    try:
        # 1. 創建 Ollama 引擎
        print("📋 步驟 1: 創建 Ollama 引擎...")
        engine = LLMEngineFactory.create_for_agent('english_teacher')
        print(f"✅ 引擎類型: {type(engine).__name__}")
        print(f"✅ 模型名稱: {engine.model_name}")
        print()
        
        # 2. 創建測試工具
        print("📋 步驟 2: 創建測試工具...")
        web_search = WebSearchTool()
        
        # 模擬工具定義
        tools = [
            {
                "name": "web_search",
                "description": "Search the web for current information about any topic"
            },
            {
                "name": "calculator", 
                "description": "Perform mathematical calculations"
            },
            {
                "name": "weather_check",
                "description": "Get current weather information for any location"
            }
        ]
        
        print(f"✅ 可用工具數量: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        print()
        
        # 3. 測試基本工具格式化
        print("📋 步驟 3: 測試工具格式化...")
        formatted_tools = engine._format_tools_for_prompt(tools)
        print("✅ 格式化後的工具描述:")
        print(formatted_tools)
        print()
        
        # 4. 測試無工具的響應
        print("📋 步驟 4: 測試無工具的響應...")
        no_tools_response = engine.generate_with_tools(
            "What is 2 + 2?", 
            [],  # 空工具列表
            temperature=0.3,
            max_tokens=100
        )
        print("✅ 無工具響應:")
        print(f"   {no_tools_response[:150]}...")
        print()
        
        # 5. 測試有工具的簡單問題
        print("📋 步驟 5: 測試有工具的簡單數學問題...")
        math_response = engine.generate_with_tools(
            "What is 15 * 23? Please calculate this for me.",
            tools,
            temperature=0.3,
            max_tokens=200
        )
        print("✅ 數學問題響應:")
        print(f"   {math_response}")
        print()
        
        # 6. 測試需要網路搜尋的問題
        print("📋 步驟 6: 測試需要網路搜尋的問題...")
        search_response = engine.generate_with_tools(
            "What is the current weather in Tokyo today?",
            tools,
            temperature=0.5,
            max_tokens=300
        )
        print("✅ 天氣查詢響應:")
        print(f"   {search_response}")
        print()
        
        # 7. 測試複雜的多工具場景
        print("📋 步驟 7: 測試複雜的多工具場景...")
        complex_response = engine.generate_with_tools(
            "I need to calculate 25% of 480, and then search for information about investment strategies for that amount of money.",
            tools,
            temperature=0.7,
            max_tokens=400
        )
        print("✅ 複雜查詢響應:")
        print(f"   {complex_response}")
        print()
        
        # 8. 獲取使用統計
        print("📋 步驟 8: 檢查使用統計...")
        stats = engine.get_cost_statistics()
        print("✅ 引擎使用統計:")
        print(f"   總請求次數: {stats['total_requests']}")
        print(f"   總 token 數: {stats['total_tokens']}")
        print(f"   平均每請求 token: {stats['average_tokens_per_request']:.1f}")
        print(f"   總成本: ${stats['total_cost']:.6f} (免費)")
        print()
        
        print("🎉 所有工具測試完成!")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ollama_tools()
    if success:
        print("\n✅ 工具功能測試通過!")
    else:
        print("\n❌ 工具功能測試失敗!")
        sys.exit(1)
