import sys
import json
import os
import random
import datetime

class Quiz:
    def __init__(self, question, choices, answer, hint="제공된 힌트가 없습니다."):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint
        
    def display(self, index):
        print("\n========================================")
        print(f"[문제 {index}]")
        print(self.question)
        for i, choices in enumerate(self.choices, 1):
            print(f"{i}. {choices}")
        print("========================================")
    
    def check_answer(self, user_answer):
        return self.answer == user_answer
    
    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint
        }
        
class QuizGame:
    def __init__(self):
        self.best_score = 0
        self.quizzes = []
        self.history = []
        
        if not self.load_data():
            self.quizzes = [
            Quiz(
                "세계에서 가장 넓은 면적을 가진 나라는?", 
                ["미국", "캐나다", "중국", "러시아"], 
                4, 
                "유라시아 대륙 북부에 걸쳐 있는, 가장 영토가 넓은 국가입니다."
            ),
            Quiz(
                "태양계 행성 중 가장 크기가 큰 행성은?", 
                ["지구", "화성", "목성", "토성"], 
                3, 
                "표면에 '대적점'이라는 커다란 붉은 점이 있는 가스 행성입니다."
            ),
            Quiz(
                "조선 제4대 왕으로 훈민정음을 창제한 인물은?", 
                ["태조", "태종", "세종", "정조"], 
                3, 
                "우리나라 만 원짜리 지폐에 그려져 있는 인물입니다."
            ),
            Quiz(
                "컴퓨터 데이터 용량 단위에서 1바이트(Byte)는 몇 비트(Bit)일까요?", 
                ["4비트", "8비트", "16비트", "32비트"], 
                2, 
                "2의 3제곱과 같은 숫자입니다."
            ),
            Quiz(
                "화학 원소기호 'O'가 나타내는 원소는 무엇일까요?", 
                ["수소", "산소", "탄소", "질소"], 
                2, 
                "우리가 숨을 쉴 때 반드시 필요한 기체입니다."
            )
        ]
            self.save_data()
            
    def play_quiz(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해 주세요. 😅")
            return
        
        while True:
            try:
                count_str = input(f"\n문제 개수를 골라 주세요. (1-{len(self.quizzes)}, 취소: 0): ").strip()
                if not count_str:
                    continue
                play_count = int(count_str)
                
                if play_count == 0:
                    print("🖐 퀴즈 풀기를 취소합니다.")
                    return
                if 1 <= play_count <= len(self.quizzes):
                    break
                print(f"1에서 {len(self.quizzes)} 사이의 숫자를 입력하세요.")
            
            except ValueError:
                print("숫자를 입력하세요")
                
        print(f"\n📑 퀴즈를 시작합니다! 문제의 개수는 {play_count} 개입니다.")
        correct_count = 0
        selected_quizzes = random.sample(self.quizzes, play_count)
        
        for i, quiz in enumerate(selected_quizzes, 1):
            quiz.display(i)
            hint_used = False
            while True:
                
                try:
                    user_input = input("정답 입력 (1-4, 힌트: h): ").strip()
                    
                    if not user_input:
                        print("⚠️ 빈 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                        continue
                    
                    if user_input == 'h':
                        print(f"{quiz.hint}")
                        hint_used = True
                        continue
                    
                    user_answer = int(user_input)
                    
                    if user_answer < 1 or user_answer > 4:
                        print("⚠️ 1-4 사이의 숫자를 입력하세요.")
                        continue
                    break
                
                except ValueError:
                    print("⚠️ 잘못된 입력입니다. 숫자 또는 h를 입력하세요.")
            
            if quiz.check_answer(user_answer):
                if hint_used:
                    print("\n⭕ 정답입니다! +0.5")
                    correct_count += 0.5
                else:
                    print("\n⭕ 정답입니다! +1")
                    correct_count += 1.0
            else:
                print("\n❌ 오답입니다. +0")
        #결과 출력 및 최고 점수 갱신
        score_percent = int((correct_count / play_count) * 100)
        print("\n========================================")
        print(f"🗒 결과: {play_count} 문제 중 {correct_count} 문제 정답! ({score_percent}점)")
        
        if correct_count > self.best_score:
            print("😲 새로운 최고 점수입니다!")
            self.best_score = correct_count
        print("========================================")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({"date": now, "played": play_count, "score": correct_count})
        self.save_data()
        
        
    def add_quiz(self):
        print("\n➕ 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()
        if not question:
            print("⚠️ 빈 입력은 허용하지 않습니다. 추가를 취소합니다.")
            return
        choices = []
        
        for i in range(1, 5):
            while True:
                choice = input(f"선택지 {i}: ").strip()
                if choice:
                    choices.append(choice)
                    break
                print("⚠️ 빈 입력은 허용되지 않습니다. 다시 입력해 주세요.")
            
        while True:
            try:
                ans_str = input("정답 번호 (1-4): ").strip()
                if not ans_str:
                    print("빈 입력입니다.")
                    continue
                answer = int(ans_str)
                if answer < 1 or answer > 4:
                    print("1-4 사이의 숫자를 입력하세요.")
                    continue
                break
            except ValueError:
                print("잘못된 입력입니다. 숫자를 입력하세요.")
            
        hint = input("힌트를 입력하세요 (없으면 엔터): ").strip()
        if not hint:
            hint = "제공된 힌트가 없습니다."  
        
        self.quizzes.append(Quiz(question, choices, answer, hint))
        print("\n 퀴즈가 성공적으로 추가됐습니다.")
        self.save_data()
        
    def delete_quiz(self):
        self.show_quizzes()
        if not self.quizzes:
            return
        while True:
            try:
                del_str = input("\n삭제할 퀴즈 번호를 입력하세요 (취소: 0): ").strip()
                if not del_str:
                    continue
                del_idx = int(del_str)
                
                if del_idx == 0:
                    print("취소했습니다.")
                    return
                if 1 <= del_idx <= len(self.quizzes):
                    deleted = self.quizzes.pop(del_idx - 1)
                    self.save_data()
                    return
                else:
                    print("⚠️ 목록에 없는 번호입니다.")
            except ValueError:
                print("⚠️ 숫자를 입력하세요.")
                    
            
    def show_quizzes(self):
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다")
            return
        print(f"🗒 \n등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("========================================")
        for i, quiz in enumerate(self.quizzes, 1):
            print(f"[{i}] {quiz.question}")
        print("========================================")
            
    def show_score(self):
        print("\n========================================")
        print(f"🎮 최고 점수: {self.best_score}점")
        print("========================================")
        print("🗒 최근 플레이 기록")
        if not hasattr(self, 'history') or not self.history:
            print("아직 플레이 기록이 없습니다.")
        else:
            for record in self.history[-5:]:
                played = record.get('played', 0)
                score = record.get('score', 0)
                percent = int((score / played) * 100) if played > 0 else 0
                print(f"- {record.get('date', '기록 없음')} | {played}문제 중 {score}점 ({percent}%)")
                print("========================================")
    
    def display_menu(self):
        print("\n========================================")
        print("        🎮 상식 퀴즈 🎮")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 퀴즈 삭제")
        print("6. 종료")
        print("========================================")

    def save_data(self):
        try:
            data = {
                "quizzes": [quiz.to_dict() for quiz in self.quizzes],
                "best_score": self.best_score,
                "history": self.history
            }
            with open("state.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ 데이터 저장 중 오류가 발생했습니다: {e}")
    
    def load_data(self):
        if not os.path.exists("state.json"):
            return False
        
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = data.get("history", [])
                
            self.best_score = data.get("best_score", 0)
            self.history = data.get("history", [])
            self.quizzes = []
            for q in data.get("quizzes", []):
                hint = q.get("hint", "제공된 힌트가 없습니다.")
                self.quizzes.append(Quiz(q["question"], q["choices"], q["answer"], hint))
            print("🎮 저장된 데이터를 불러왔습니다.")
            return True
        except (json.JSONDecodeError, KeyError) as e:
            print("⚠️ 데이터 파일이 손상되었습니다. 기본 데이터로 시작합니다.")
            return False
    
    def run(self):
        while True:
            self.display_menu()
            try:
                # 1. 입력 앞뒤 공백 제거
                choice_str = input("선택: ").strip()
                
                # 2. 빈 입력(그냥 Enter) 처리
                if not choice_str:
                    print("⚠️ 빈 입력입니다. 1-6 사이의 숫자를 입력하세요.")
                    continue
                
                # 3. 숫자 변환 (문자열 입력 시 ValueError 발생)
                choice = int(choice_str)
                
                # 4. 허용 범위 밖 숫자 예외 처리
                if choice < 1 or choice > 6:
                    print("⚠️ 잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요.")
                    continue
                
                # 메뉴 분기 (구현 예정)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.show_quizzes()
                elif choice == 4:
                    self.show_score()
                elif choice == 5:
                    self.delete_quiz()
                elif choice == 6:
                    print("🖐 게임을 종료합니다. 안녕히 가세요!")
                    break

            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-6 사이의 숫자를 입력하세요.")
            except (KeyboardInterrupt, EOFError):
                # Ctrl+C 또는 입력 스트림 종료 시 안전하게 종료
                print("\n⚠️ 비정상 종료 감지! 데이터를 안전하게 보존하고 종료합니다.")
                self.save_data()
                sys.exit(0)

if __name__ == "__main__":
    game = QuizGame()
    game.run()