@echo off
chcp 65001 >nul
echo ==========================================
echo   Agentic Teaching System - Interactive
echo ==========================================
echo.
echo Starting interactive chat mode...
echo You can ask questions directly, system will route to appropriate teacher
echo Type 'quit' or 'exit' to stop
echo.

echo Example questions:
echo   - What is the difference between "their", "there", and "they're"?
echo   - What are Chinese idioms? Give me some examples.
echo   - How can I improve my writing skills?
echo   - Explain Li Bai's poetry
echo.

docker exec -it agentic-app python -c "
import sys
sys.path.append('/app')

from producer.producer import StudentProducer
import time

def interactive_chat():
    print('AI Teaching System Ready!')
    print('Type your questions below (quit to exit):')
    print()
    
    producer = StudentProducer()
    
    while True:
        try:
            question = input('Your question: ').strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print('Goodbye!')
                break
                
            if not question:
                continue
                
            if question.lower() == 'status':
                print('System Status: All services running')
                continue
                
            print(f'Sending: {question}')
            
            # Send question
            producer.send_question(question)
            print('Question sent to AI teacher!')
            print('Processing... (responses appear in system logs)')
            print()
            
        except KeyboardInterrupt:
            print('\nGoodbye!')
            break
        except Exception as e:
            print(f'Error: {e}')
            print()

if __name__ == '__main__':
    interactive_chat()
"

pause
