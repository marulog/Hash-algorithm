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
    "sha2": hashlib.sha256,
    "sha3": hashlib.sha3_256,
    "blake2": hashlib.blake2b,
    "blake3": blake3.blake3,
    "md5": hashlib.md5,
}

# 테스트할 파일 경로
FILE_PATH = "upload/1000MB.enc"
BLOCK_SIZE = 64 * 1024  # 64KB 블록 단위로 읽기

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
    """현재 CPU 개수와 시스템 메모리 사용량 출력"""
    cpu_count = len(os.sched_getaffinity(0))
    total_memory = psutil.virtual_memory().total / 1024 / 1024 / 1024  # GB 변환
    used_memory = psutil.virtual_memory().used / 1024 / 1024 / 1024  # GB 변환
    available_memory = psutil.virtual_memory().available / 1024 / 1024 / 1024  # GB 변환
    process_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB 변환

    print(f"🖥 현재 CPU 개수: {cpu_count} 개")
    print(f"💾 총 시스템 메모리 크기: {total_memory:.2f} GB")
    print(f"📌 사용 중인 시스템 메모리: {used_memory:.2f} GB")
    print(f"🔄 사용 가능한 메모리: {available_memory:.2f} GB")
    print(f"⚡ 현재 프로세스 메모리 사용량: {process_memory:.2f} MB")
    print("=" * 50)

def measure_performance(hash_name, hash_func, file_path, runs=10):
    """해싱 성능을 여러 번 실행하여 평균값을 반환"""
    process = psutil.Process(os.getpid())

    speeds, cpu_usages, memory_usages, powers, temperatures = [], [], [], [], []

    for _ in range(runs):
        # 해시 객체 생성
        hasher = hash_func()

        start_cpu = process.cpu_percent(interval=0.1)
        start_mem = process.memory_info().rss / 1024 / 1024  # MB 변환
        start_time = time.time()

        # 파일을 64KB 블록 단위로 읽어서 해싱
        with open(file_path, "rb") as f:
            while chunk := f.read(BLOCK_SIZE):
                hasher.update(chunk)

        end_time = time.time()
        end_cpu = process.cpu_percent(interval=0.1)
        end_mem = process.memory_info().rss / 1024 / 1024  # MB 변환

        # CPU 사용량이 음수로 나오면 0으로 보정
        cpu_usage = max(0, end_cpu - start_cpu)

        # 메모리 사용량이 음수로 나오면 0으로 보정
        memory_usage = max(0, end_mem - start_mem)

        # 성능 측정
        speeds.append(end_time - start_time)  # 속도 (초)
        cpu_usages.append(cpu_usage)  # CPU 사용량 (%)
        memory_usages.append(memory_usage)  # 메모리 사용량 (MB)
        powers.append(estimate_power(cpu_usage))  # 전력 사용량 (W)
        temperatures.append(estimate_temperature(cpu_usage))  # 온도 (°C)

    # 평균값 계산 (np.float64 → float 변환 추가)
    return {
        "hash": hash_name,
        "speed": float(np.mean(speeds)),  
        "cpu_usage": float(np.mean(cpu_usages)),  
        "memory_usage": float(np.mean(memory_usages)),  
        "power": float(np.mean(powers)),  
        "temperature": float(np.mean(temperatures))  
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
