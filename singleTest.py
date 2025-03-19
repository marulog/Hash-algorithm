import hashlib
import blake3
import xxhash
import time
import psutil
import os

# 테스트할 해시 알고리즘 목록
HASH_ALGORITHMS = {
    "sha2": lambda data: hashlib.sha256(data).hexdigest(),
    "sha3": lambda data: hashlib.sha3_256(data).hexdigest(),
    "blake2": lambda data: hashlib.blake2b(data).hexdigest(),
    "blake3": lambda data: blake3.blake3(data).hexdigest(),
    "xxh3": lambda data: xxhash.xxh3_64(data).hexdigest(),
    "md5": lambda data: hashlib.md5(data).hexdigest(),
}

# 테스트할 파일 경로
FILE_PATH = "upload/10MB.bin"

def get_system_info():
    """현재 CPU 개수와 총 메모리 크기 출력"""
    cpu_count = os.cpu_count()
    total_memory = psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB 단위 변환
    print(f"🖥 현재 CPU 개수: {len(os.sched_getaffinity(0))} 개")
    print(f"💾 총 메모리 크기: {total_memory:.2f} GB")
    print("=" * 50)

def measure_performance(hash_name, hash_func, file_path):
    """해싱 속도, CPU 사용량, 전력 소비량, 발열 측정"""

    # 파일 로드
    with open(file_path, "rb") as f:
        data = f.read()

    process = psutil.Process(os.getpid())

    # 초기 메모리 및 CPU 사용량 측정
    start_cpu = process.cpu_percent(interval=None)
    start_mem = process.memory_full_info().rss / 1024 / 1024  # MB
    start_time = time.time()

    # 해싱 실행
    hash_result = hash_func(data)

    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)
    end_mem = process.memory_full_info().rss / 1024 / 1024  # MB

    # 성능 측정
    hash_speed = end_time - start_time  # 해싱 속도
    cpu_usage = end_cpu - start_cpu  # CPU 사용량
    memory_usage = end_mem - start_mem  # 메모리 사용량
    power_consumption = estimate_power(cpu_usage)  # 전력 소비량
    temperature = estimate_temperature(cpu_usage)  # CPU 온도

    # 결과 출력
    print(f"🔍 {hash_name.upper()} 테스트 결과")
    print(f" - 해싱 속도: {hash_speed:.5f} 초")
    print(f" - CPU 사용량: {cpu_usage:.2f}%")
    print(f" - 메모리 사용량: {memory_usage:.2f} MB")
    print(f" - 전력 소비량: {power_consumption:.2f} W")
    print(f" - CPU 온도: {temperature:.2f}°C")
    print("-" * 50)

    return {
        "hash": hash_name,
        "speed": hash_speed,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "power": power_consumption,
        "temperature": temperature
    }

def estimate_power(cpu_usage):
    """CPU 사용량 기반 전력 소비량 추정"""
    base_power = 10  # 기본 소비 전력 (EC2 Graviton3 가정)
    power_factor = 0.6  # CPU 사용률 1%당 추가 소비 전력
    return base_power + (cpu_usage * power_factor)

def estimate_temperature(cpu_usage):
    """CPU 부하 기반 온도 추정"""
    base_temp = 35  # 기본 온도 (°C)
    temp_factor = 0.5  # CPU 사용률 1%당 온도 상승 (가정)
    return base_temp + (cpu_usage * temp_factor)

if __name__ == "__main__":
    print("🔹 싱글코어 해싱 성능 테스트 시작")
    
    # 시스템 정보 출력
    get_system_info()

    # 싱글코어 모드로 실행 (CPU 1개만 사용)
    # os.sched_setaffinity(0, {0}) -> 일단 명령어로 실행

    # 모든 해시 알고리즘 테스트 실행
    results = []
    for name, func in HASH_ALGORITHMS.items():
        results.append(measure_performance(name, func, FILE_PATH))

    # 테스트 결과 출력
    print("\n📊 전체 테스트 결과")
    for result in results:
        print(result)
