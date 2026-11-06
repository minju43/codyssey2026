import sys

class QuizGame:
    def __init__(self):
        # 나중에 state.json에서 데이터를 불러올 때 사용할 속성들
        self.quizzes = []
        self.best_score = 0

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
                    print("📝 퀴즈 풀기 기능은 곧 추가됩니다.")
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