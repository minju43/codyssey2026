import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

EPSILON = 1e-9
BENCHMARK_ITERATIONS = 10

# 1. 라벨 정규화 및 유틸리티
def normalize_label(raw_label: Any) -> Optional[str]:
    """다양한 표기(+, cross, x, X 등)를 표준 라벨('Cross', 'X')로 정규화"""
    if not isinstance(raw_label, str):
        return None
    cleaned = raw_label.strip().lower()
    if cleaned in ("+", "cross"):
        return "Cross"
    if cleaned in ("x",):
        return "X"
    return None


def validate_matrix(matrix: Any, expected_size: Optional[int] = None) -> Tuple[bool, str, int]:
    """2차원 정사각 행렬 여부 및 숫자 타입 검증"""
    if not isinstance(matrix, list) or len(matrix) == 0:
        return False, "데이터가 비어 있거나 리스트 형식이 아닙니다.", 0

    n = len(matrix)
    if expected_size is not None and n != expected_size:
        return False, f"행 크기 불일치 (기대: {expected_size}, 실제: {n})", n

    for r_idx, row in enumerate(matrix):
        if not isinstance(row, list) or len(row) != n:
            actual_cols = len(row) if isinstance(row, list) else -1
            return False, f"{r_idx + 1}행 열 크기 불일치 (기대: {n}, 실제: {actual_cols})", n
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return False, f"{r_idx + 1}행에 숫자가 아닌 값이 포함되어 있습니다.", n

    return True, "OK", n


def generate_pattern(n: int, label: str) -> List[List[float]]:
    """[보너스] N×N 크기의 Cross 또는 X 표준 패턴/필터 자동 생성"""
    norm = normalize_label(label)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    mid = n // 2

    if norm == "Cross":
        for i in range(n):
            matrix[mid][i] = 1.0
            matrix[i][mid] = 1.0
    elif norm == "X":
        for i in range(n):
            matrix[i][i] = 1.0
            matrix[i][n - 1 - i] = 1.0
    else:
        raise ValueError(f"지원하지 않는 라벨입니다: {label}")
    return matrix

# 2. MAC 연산 및 판정 엔진 (외부 라이브러리 미사용)
def mac_2d(pattern: List[List[float]], filt: List[List[float]]) -> float:
    """2차원 중첩 반복문 기반 MAC(Multiply-Accumulate) 연산"""
    n = len(pattern) #배열의 한 변 길이 계산
    total = 0.0
    for i in range(n): # 모든 칸 방문
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def flatten_matrix(matrix: List[List[float]]) -> List[float]:
    """[보너스] 2차원 배열을 길이 N^2의 1차원 배열로 평탄화"""
    flat: List[float] = []
    for row in matrix:
        for val in row:
            flat.append(val)
    return flat

def mac_1d(flat_pattern: List[float], flat_filt: List[float]) -> float:
    """[보너스] 1차원 배열 단일 루프 기반 MAC 연산"""
    total = 0.0
    for i in range(len(flat_pattern)):
        total += flat_pattern[i] * flat_filt[i]
    return total

def decide_winner( # 두 필터의 점수 중 무엇이 더 높은지 판정
    score_a: float,
    score_b: float,
    label_a: str = "A",
    label_b: str = "B",
    undecided_label: str = "UNDECIDED",
    eps: float = EPSILON,
) -> str:
    """허용오차(epsilon) 기반 점수 비교 및 판정"""
    if abs(score_a - score_b) < eps: # 부동소수점 오차를 없애기 위해 점수 차가 10억분의 1보다 작으면 동점(UNDDECIDED/판정불가)
        return undecided_label
    return label_a if score_a > score_b else label_b

def measure_mac_time_ms(
    pattern: List[List[float]],
    filter_a: List[List[float]],
    filter_b: List[List[float]],
    iterations: int = BENCHMARK_ITERATIONS,
) -> float:
    """I/O를 제외한 순수 MAC 연산(두 필터 계산 기준) 평균 소요 시간(ms) 측정"""
    start = time.perf_counter()
    for _ in range(iterations):
        mac_2d(pattern, filter_a)
        mac_2d(pattern, filter_b)
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return elapsed_ms / iterations


# 3. 모드 1: 사용자 입력 (3×3)
def read_matrix_from_console(name: str, size: int = 3) -> List[List[float]]:
    """콘솔에서 size×size 행렬을 입력받고 행/열 및 숫자 파싱 검증 수행"""
    while True:
        print(f"{name} ({size}줄 입력, 공백 구분)")
        matrix: List[List[float]] = []
        valid = True

        for row_idx in range(size):
            raw_line = input(f"  {row_idx + 1}행 > ").strip()
            tokens = raw_line.split() # 공백 기준 조각을 나눴을 때 개수가 3개가 아니라면 valid = False로 변경, break로 빠져나가서 처음부터 다시 입력받음
            if len(tokens) != size:
                print(f"입력 형식 오류: 각 줄에 {size}개의 숫자를 공백으로 구분해 입력하세요.\n")
                valid = False
                break
            try:
                row = [float(tok) for tok in tokens]
                matrix.append(row)
            except ValueError:
                # str이 입력되어 ValueError가 발생하면 프로그램이 죽지 않고 잡아서 재입력을 유도
                print(f"입력 형식 오류: 숫자만 입력해야 합니다. 각 줄에 {size}개의 숫자를 입력하세요.\n")
                valid = False
                break

        if valid:
            return matrix


def run_mode_user_input() -> None:
    # 위 함수들을 순서대로 호출
    size = 3
    print("\n---------------------------------------")
    print(" [1] 필터 입력")
    print("---------------------------------------")
    filter_a = read_matrix_from_console("필터 A", size)
    print()
    filter_b = read_matrix_from_console("필터 B", size)

    print("\n[저장 확인] 필터 A, 필터 B (3×3) 저장 완료")

    print("\n---------------------------------------")
    print(" [2] 패턴 입력")
    print("---------------------------------------")
    pattern = read_matrix_from_console("패턴", size)

    # MAC 연산 및 시간 측정
    score_a = mac_2d(pattern, filter_a)
    score_b = mac_2d(pattern, filter_b)
    avg_ms = measure_mac_time_ms(pattern, filter_a, filter_b, BENCHMARK_ITERATIONS)
    verdict = decide_winner(score_a, score_b, "A", "B", "판정 불가")

    print("\n---------------------------------------")
    print(" [3] MAC 결과")
    print("---------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/{BENCHMARK_ITERATIONS}회): {avg_ms:.4f} ms")
    if verdict == "판정 불가":
        print(f"판정: 판정 불가 (|A - B| < {EPSILON})")
    else:
        print(f"판정: {verdict}")

    print("\n---------------------------------------")
    print(f" [4] 성능 분석 (평균/{BENCHMARK_ITERATIONS}회)")
    print("---------------------------------------")
    print(f"{'크기':<10}{'평균 시간(ms)':<16}{'연산 횟수(N²)'}")
    print("-" * 40)
    print(f"{'3×3':<10}{avg_ms:<16.4f}{size * size}")


# ==========================================
# 4. 모드 2: data.json 일괄 분석 및 성능 평가
# ==========================================
def extract_size_from_key(key: str) -> Optional[int]:
    """'size_5_1' 또는 'size_13' 형태의 키에서 정수 N 추출"""
    parts = key.strip().split("_")
    if len(parts) >= 2 and parts[0].lower() == "size":
        try:
            return int(parts[1])
        except ValueError:
            return None
    return None


def run_mode_json_analysis(filepath: str = "data.json") -> None:
    if not os.path.exists(filepath):
        print(f"\n[오류] '{filepath}' 파일을 찾을 수 없습니다. 실행 경로를 확인해주세요.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"\n[오류] JSON 파일을 읽는 중 문제가 발생했습니다: {e}")
        return

    raw_filters = data.get("filters", {})
    raw_patterns = data.get("patterns", {})

    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")

    # normalized_filters[N] = {"Cross": matrix, "X": matrix}
    normalized_filters: Dict[int, Dict[str, List[List[float]]]] = {}

    if isinstance(raw_filters, dict):
        for size_key, filter_group in raw_filters.items():
            n = extract_size_from_key(size_key)
            if n is None or not isinstance(filter_group, dict):
                print(f"✗ {size_key}: 잘못된 필터 키 또는 구조")
                continue

            loaded_labels: Dict[str, List[List[float]]] = {}
            for raw_lbl, matrix in filter_group.items():
                std_lbl = normalize_label(raw_lbl)
                if std_lbl is None:
                    continue
                ok, msg, _ = validate_matrix(matrix, expected_size=n)
                if ok:
                    loaded_labels[std_lbl] = matrix
                else:
                    print(f"✗ {size_key} ({raw_lbl}): 검증 실패 - {msg}")

            if "Cross" in loaded_labels and "X" in loaded_labels:
                normalized_filters[n] = loaded_labels
                print(f"✓ {size_key:<8} 필터 로드 완료 (Cross, X)")
            else:
                print(f"✗ {size_key:<8} 필수 필터(Cross, X) 누락")

    print("\n---------------------------------------")
    print(" [2] 패턴 분석 (라벨 정규화 적용)")
    print("---------------------------------------")

    # patterns가 dict인 경우와 list인 경우 모두 대응
    pattern_items: List[Tuple[str, Any]] = []
    if isinstance(raw_patterns, dict):
        pattern_items = list(raw_patterns.items())
    elif isinstance(raw_patterns, list):
        for idx, item in enumerate(raw_patterns):
            case_id = item.get("id") or item.get("name") or f"case_{idx + 1}"
            pattern_items.append((case_id, item))

    total_count = 0
    pass_count = 0
    fail_cases: List[Tuple[str, str]] = []
    sample_inputs_by_size: Dict[int, List[List[float]]] = {}

    for case_id, item in pattern_items:
        total_count += 1
        print(f"--- {case_id} ---")

        if not isinstance(item, dict):
            reason = "스키마 오류: 패턴 항목이 객체(dict) 형식이 아님"
            print(f"판정: ERROR | FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        n = extract_size_from_key(case_id)
        if n is None:
            reason = f"키 규칙 오류: '{case_id}'에서 크기 N을 추출할 수 없음"
            print(f"판정: ERROR | FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        if n not in normalized_filters:
            reason = f"필터 누락: size_{n}에 해당하는 정상 필터가 없음"
            print(f"판정: ERROR | FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        matrix = item.get("input")
        ok, msg, _ = validate_matrix(matrix, expected_size=n)
        if not ok:
            reason = f"크기/데이터 불일치 ({msg})"
            print(f"판정: ERROR | FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        # 성능 측정용 샘플 저장
        if n not in sample_inputs_by_size:
            sample_inputs_by_size[n] = matrix

        raw_expected = item.get("expected")
        expected_label = normalize_label(raw_expected)
        if expected_label is None:
            reason = f"라벨 정규화 불가: expected='{raw_expected}'"
            print(f"판정: ERROR | FAIL ({reason})")
            fail_cases.append((case_id, reason))
            continue

        cross_filter = normalized_filters[n]["Cross"]
        x_filter = normalized_filters[n]["X"]

        cross_score = mac_2d(matrix, cross_filter)
        x_score = mac_2d(matrix, x_filter)
        verdict = decide_winner(cross_score, x_score, "Cross", "X", "UNDECIDED")

        print(f"Cross 점수: {cross_score}")
        print(f"X 점수: {x_score}")

        if verdict == expected_label:
            pass_count += 1
            print(f"판정: {verdict} | expected: {expected_label} | PASS")
        else:
            if verdict == "UNDECIDED":
                reason = f"동점(UNDECIDED) 처리 규칙 (|Cross - X| < {EPSILON}), expected={expected_label}"
            else:
                reason = f"오분류 (판정={verdict}, expected={expected_label})"
            fail_cases.append((case_id, reason))
            print(f"판정: {verdict} | expected: {expected_label} | FAIL ({reason})")

    # 3. 성능 분석 (3x3 포함, 5x5, 13x13, 25x25)
    print("\n---------------------------------------")
    print(f" [3] 성능 분석 (평균/{BENCHMARK_ITERATIONS}회)")
    print("---------------------------------------")
    print(f"{'크기':<10}{'평균 시간(ms)':<16}{'연산 횟수(N²)'}")
    print("-" * 40)

    target_sizes = sorted(set([3, 5, 13, 25] + list(normalized_filters.keys())))
    for n in target_sizes:
        if n in normalized_filters and n in sample_inputs_by_size:
            pat = sample_inputs_by_size[n]
            fa = normalized_filters[n]["Cross"]
            fb = normalized_filters[n]["X"]
        else:
            # 3x3 또는 JSON에 없는 크기는 패턴 생성기로 벤치마크 수행
            pat = generate_pattern(n, "Cross")
            fa = generate_pattern(n, "Cross")
            fb = generate_pattern(n, "X")

        avg_ms = measure_mac_time_ms(pat, fa, fb, BENCHMARK_ITERATIONS)
        print(f"{f'{n}×{n}':<10}{avg_ms:<16.4f}{n * n}")

    # 4. 보너스: 2D vs 1D 배열 메모리 접근 최적화 비교 (25x25 기준)
    bench_n = 25
    pat_2d = sample_inputs_by_size.get(bench_n, generate_pattern(bench_n, "Cross"))
    fa_2d = normalized_filters.get(bench_n, {}).get("Cross", generate_pattern(bench_n, "Cross"))
    fb_2d = normalized_filters.get(bench_n, {}).get("X", generate_pattern(bench_n, "X"))

    pat_1d = flatten_matrix(pat_2d)
    fa_1d = flatten_matrix(fa_2d)
    fb_1d = flatten_matrix(fb_2d)

    t_2d = measure_mac_time_ms(pat_2d, fa_2d, fb_2d, 100)
    start_1d = time.perf_counter()
    for _ in range(100):
        mac_1d(pat_1d, fa_1d)
        mac_1d(pat_1d, fb_1d)
    t_1d = ((time.perf_counter() - start_1d) * 1000.0) / 100

    print("\n---------------------------------------")
    print(" [보너스] 메모리 접근 최적화 비교 (25×25, 100회 평균)")
    print("---------------------------------------")
    print(f"2차원 중첩 리스트(2D) 평균 시간: {t_2d:.4f} ms")
    print(f"1차원 평탄화 리스트(1D) 평균 시간: {t_1d:.4f} ms")

    # 5. 결과 요약
    print("\n---------------------------------------")
    print(" [4] 결과 요약")
    print("---------------------------------------")
    print(f"총 테스트: {total_count}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {len(fail_cases)}개")

    if fail_cases:
        print("\n실패 케이스:")
        for cid, reason in fail_cases:
            print(f"- {cid}: {reason}")


# ==========================================
# 5. 메인 진입점
# ==========================================
def main() -> None:
    print("=== Mini NPU Simulator ===")
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")

    while True:
        choice = input("선택: ").strip()
        if choice == "1":
            run_mode_user_input()
            break
        elif choice == "2":
            run_mode_json_analysis("data.json")
            break
        else:
            print("잘못된 선택입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()