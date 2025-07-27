#!/usr/bin/env python3
import sys
sys.path.append('/app')

from llm_engines.factory import LLMEngineFactory

def process_question(question):
    try:
        # Simple routing logic
        question_lower = question.lower()
        
        if 'chinese' in question_lower or '中文' in question or '什麼' in question or '解釋' in question:
            agent_type = 'chinese_teacher'
            print('🔀 Routing to: Chinese Teacher')
        else:
            agent_type = 'english_teacher'
            print('🔀 Routing to: English Teacher')
        
        print()
        
        # Create engine and get response
        engine = LLMEngineFactory.create_for_agent(agent_type)
        response = engine.generate_response(question)
        
        print('🤖 AI Response:')
        print(response)
        return True
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        print('💡 Please check if all services are running properly.')
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
        process_question(question)
    else:
        print('❌ No question provided')
