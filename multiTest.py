import hashlib
import blake3
import xxhash
import time
import psutil
import os
import multiprocessing

# 파일 경로
FILE_PATH = "upload/10MB.bin"

# 해싱 알고리즘 별 함수 정의 (lambda 사용 X)
def hash_sha2(data): return hashlib.sha256(data).hexdigest()
def hash_sha3(data): return hashlib.sha3_256(data).hexdigest()
def hash_blake2(data): return hashlib.blake2b(data).hexdigest()
def hash_blake3(data): return blake3.blake3(data).hexdigest()
def hash_xxh3(data): return xxhash.xxh3_64(data).hexdigest()
def hash_md5(data): return hashlib.md5(data).hexdigest()

# 해시 함수 매핑
HASH_ALGORITHMS = {
    "sha2": hash_sha2,
    "sha3": hash_sha3,
    "blake2": hash_blake2,
    "blake3": hash_blake3,
    "xxh3": hash_xxh3,
    "md5": hash_md5,
}

def get_system_info():
    """현재 CPU 개수와 총 메모리 크기 출력"""
    cpu_count = os.cpu_count()
    total_memory = psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB 변환
    print(f"🖥 현재 CPU 개수: {len(os.sched_getaffinity(0))} 개")
    print(f"💾 총 메모리 크기: {total_memory:.2f} GB")
    print("=" * 50)

def measure_performance(hash_name, hash_func, file_path):
    """해싱 속도, CPU 사용량, 전력 소비량, 발열 측정"""
    with open(file_path, "rb") as f:
        data = f.read()

    process = psutil.Process(os.getpid())

    # 초기 메모리 및 CPU 사용량 측정
    start_cpu = process.cpu_percent(interval=None)
    start_mem = process.memory_full_info().rss / 1024 / 1024  # MB
    start_time = time.time()

    # 해싱 실행 (멀티코어 최적화: 같은 데이터 10번 해싱)
    for _ in range(10):  
        hash_result = hash_func(data)

    end_time = time.time()
    end_cpu = process.cpu_percent(interval=None)
    end_mem = process.memory_full_info().rss / 1024 / 1024  # MB

    # 성능 측정
    hash_speed = (end_time - start_time) / 10  # 평균 해싱 속도
    cpu_usage = (end_cpu - start_cpu) / 10  # 평균 CPU 사용량
    memory_usage = end_mem - start_mem  # 메모리 사용량 차이 측정
    power_consumption = estimate_power(cpu_usage)  # 전력 소비량
    temperature = estimate_temperature(cpu_usage)  # CPU 온도

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

def run_tests():
    """멀티코어(병렬 처리)로 해시 함수 성능 테스트 실행"""
    print("🔹 멀티코어 해싱 성능 테스트 시작")

    # 시스템 정보 출력
    get_system_info()

    # 병렬 실행 (CPU 코어 수만큼 프로세스 사용)
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(measure_performance, [(name, func, FILE_PATH) for name, func in HASH_ALGORITHMS.items()])

    # 결과 출력
    print("\n📊 전체 테스트 결과")
    for result in results:
        print(f"🔍 {result['hash'].upper()} 결과: {result}")

if __name__ == "__main__":
    run_tests()
