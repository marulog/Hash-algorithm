import hashlib
import blake3
import xxhash
import time
import psutil
import os
import resource
import numpy as np  # 평균 계산을 위한 라이브러리 추가

# 테스트할 해시 알고리즘 목록
HASH_ALGORITHMS = {
    "sha2": lambda data: hashlib.sha256(data).hexdigest(),
    "sha3": lambda data: hashlib.sha3_256(data).hexdigest(),
    "blake2": lambda data: hashlib.blake2b(data).hexdigest(),
    "blake3": lambda data: blake3.blake3(data).hexdigest(),
    # "xxh3": lambda data: xxhash.xxh3_64(data).hexdigest(),
    "md5": lambda data: hashlib.md5(data).hexdigest(),
}

# 테스트할 파일 경로
FILE_PATH = "upload/100MB.enc"

def limit_resources():
    """CPU를 1개로 제한하고 메모리를 1GB로 제한"""
    try:
        os.sched_setaffinity(0, {0})  # CPU 1개만 사용
        mem_limit = 1 * 1024 * 1024 * 1024  # 1GB 메모리 제한
        resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
        print("✅ CPU 1개 및 1GB 메모리 제한 설정 완료")
    except Exception as e:
        print(f"⚠️ 리소스 제한 설정 실패: {e}")

def get_system_info():
    """현재 CPU 개수와 총 메모리 크기 출력 + 프로세스 최대 메모리 제한 확인"""
    cpu_count = len(os.sched_getaffinity(0))
    total_memory = psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB 변환
    process_memory_limit = resource.getrlimit(resource.RLIMIT_AS)[0] / 1024 / 1024 / 1024  # GB 변환

    print(f"🖥 현재 CPU 개수: {cpu_count} 개")
    print(f"💾 총 시스템 메모리 크기: {total_memory:.2f} GB")
    print(f"🚫 현재 프로세스 최대 메모리 제한: {process_memory_limit:.2f} GB")
    print("=" * 50)

def measure_performance(hash_name, hash_func, file_path, runs=10):
    """해싱 성능을 여러 번 실행하여 평균값을 반환"""
    
    process = psutil.Process(os.getpid())

    # 파일 로드
    with open(file_path, "rb") as f:
        data = f.read()

    speeds, cpu_usages, memory_usages, powers, temperatures = [], [], [], [], []

    for _ in range(runs):
        start_cpu = process.cpu_percent(interval=None)
        start_mem = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()

        # 해싱 실행
        hash_result = hash_func(data)

        end_time = time.time()
        end_cpu = process.cpu_percent(interval=None)
        end_mem = process.memory_info().rss / 1024 / 1024  # MB

        # 성능 측정
        speeds.append(end_time - start_time)  # 속도 (초)
        cpu_usages.append(end_cpu - start_cpu)  # CPU 사용량 (%)
        memory_usages.append(end_mem - start_mem)  # 메모리 사용량 (MB)
        powers.append(estimate_power(cpu_usages[-1]))  # 전력 사용량 (W)
        temperatures.append(estimate_temperature(cpu_usages[-1]))  # 온도 (°C)

    # 평균값 계산
    return {
        "hash": hash_name,
        "speed": np.mean(speeds),
        "cpu_usage": np.mean(cpu_usages),
        "memory_usage": np.mean(memory_usages),
        "power": np.mean(powers),
        "temperature": np.mean(temperatures)
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

    # CPU 및 메모리 제한 설정
    limit_resources()

    # 시스템 정보 출력
    get_system_info()

    # 모든 해시 알고리즘 테스트 실행
    results = []
    for name, func in HASH_ALGORITHMS.items():
        result = measure_performance(name, func, FILE_PATH)
        results.append(result)

    # 테스트 결과 출력
    print("\n📊 전체 테스트 결과 (10회 평균)")
    for result in results:
        print(result)
