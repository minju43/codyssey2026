import sys

class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer
        
    def display(self, index):
        print("\n========================================")
        print(f"[문제 {index}]")
        print(self.question)
        for i, choices in enumerate(self.choices, 1):
            print(f"{i}. {choices}")
        print("========================================")
    
    def check_answer(self, user_answer):
        return self.answer == user_answer
class QuizGame:
    def __init__(self):
        # 나중에 state.json에서 데이터를 불러올 때 사용할 속성들
        
        self.best_score = 0
        self.quizzes = [
            Quiz("이 문제의 정답은 1번일 때, 정답은?", ["2", "1", "1번", "정답"], 1),
            Quiz("'우리 한 번 싸우면 이틀은 가니까' 다음에 이어질 가사는?", ["싸우지 말자", "싸우고 친구랑 놀러 갈게", "딱 세 번만 참으려 했는데", "네가 좀 참아 줘"], 3),
            Quiz("다음 중 가장 재미있는 게임은?", ["LOL", "발로란트", "크레이지아케이드", "오버워치"], 4),
            Quiz("코디세이 올인원 입학연수과정에서 동료학습평가 시 받아야 하는 PASS의 개수는?", ["1", "2", "3", "100"], 3),
            Quiz("충남대학교 컴퓨터융합학부에서 가장 귀여운 교수님은?", ["장진수 교수님", "이영석 교수님", "김기일 교수님", "조승범 교수님"], 1)
        ]
    def play_quiz(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해 주세요. 😅")
            return
        print(f"\n📑 퀴즈를 시작합니다! 문제의 개수는 {len(self.quizzes)}개입니다.")
        correct_count = 0
        
        for i, quiz in enumerate(self.quizzes, 1):
            quiz.display(i)
            while True:
                try:
                    user_input = input("정답 입력 (1-4): ").strip()
                    if not user_input:
                        print("빈 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                        continue
                    
                    user_answer = int(user_input)
                    if user_answer < 1 or user_answer > 4:
                        print("1-4 사이의 숫자를 입력하세요.")
                        continue
                    break
                except ValueError:
                    print("잘못된 입력입니다. 숫자를 입력하세요.")
            if quiz.check_answer(user_answer):
                print("정답입니다!")
                correct_count += 1
            else:
                print("오답입니다.")
        #결과 출력 및 최고 점수 갱신
        score_percent = int((correct_count / len(self.quizzes)) * 100)
        print("\n========================================")
        print(f"결과: {len(self.quizzes)} 문제 중 {correct_count} 문제 정답! ({score_percent}점)")
        
        if correct_count > self.best_score:
            print("새로운 최고 점수입니다!")
            self.best_score = correct_count
        print("========================================")
        

    def display_menu(self):
        print("\n========================================")
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("========================================")
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("========================================")

    def run(self):
        while True:
            self.display_menu()
            try:
                # 1. 입력 앞뒤 공백 제거
                choice_str = input("선택: ").strip()
                
                # 2. 빈 입력(그냥 Enter) 처리
                if not choice_str:
                    print("⚠️ 빈 입력입니다. 1-5 사이의 숫자를 입력하세요.")
                    continue
                
                # 3. 숫자 변환 (문자열 입력 시 ValueError 발생)
                choice = int(choice_str)
                
                # 4. 허용 범위 밖 숫자 예외 처리
                if choice < 1 or choice > 5:
                    print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
                    continue
                
                # 메뉴 분기 (구현 예정)
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    print("📌 퀴즈 추가 기능은 곧 추가됩니다.")
                elif choice == 3:
                    print("📋 퀴즈 목록 기능은 곧 추가됩니다.")
                elif choice == 4:
                    print("🏆 점수 확인 기능은 곧 추가됩니다.")
                elif choice == 5:
                    print("게임을 종료합니다. 안녕히 가세요!")
                    break

            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
            except (KeyboardInterrupt, EOFError):
                # Ctrl+C 또는 입력 스트림 종료 시 안전하게 종료
                print("\n⚠️ 비정상 종료 감지! 데이터를 안전하게 보존하고 종료합니다.")
                sys.exit(0)

if __name__ == "__main__":
    game = QuizGame()
    game.run()