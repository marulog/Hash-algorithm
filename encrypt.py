from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# AES-256 암호화를 위한 키와 IV 생성
KEY = os.urandom(32)  # 256-bit 키
IV = os.urandom(16)   # 128-bit IV (초기 벡터)

# 암호화 함수 (AES-256 CBC)
def encrypt_file(input_filename, output_filename):
    try:
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(input_filename, "rb") as f:
            data = f.read()

        # 패딩 추가 (AES는 블록 크기가 16바이트이므로 맞춰줘야 함)
        padding_length = 16 - (len(data) % 16)
        data += bytes([padding_length] * padding_length)

        encrypted_data = encryptor.update(data) + encryptor.finalize()

        with open(output_filename, "wb") as f:
            f.write(IV + encrypted_data)  # IV 포함하여 저장
        
        print(f"✅ 암호화 완료: {output_filename}")

    except Exception as e:
        print(f"❌ 파일 암호화 중 오류 발생: {e}")

# 테스트할 파일 크기 (10MB, 100MB, 1000MB)
file_sizes = [10, 100, 1000]

# upload 폴더 생성 (디버깅 출력 추가)
upload_dir = "upload"
if not os.path.exists(upload_dir):
    print(f"⚠️ 'upload/' 디렉토리 없음. 생성 중...")
    os.makedirs(upload_dir, exist_ok=True)
print(f"✅ 'upload/' 디렉토리 확인 완료.")

# 암호화 실행 (파일 생성 확인 포함)
for size in file_sizes:
    bin_filename = f"upload/{size}MB.bin"
    enc_filename = f"upload/{size}MB.enc"

    # 랜덤 바이너리 파일 생성
    try:
        with open(bin_filename, "wb") as f:
            f.write(os.urandom(size * 1024 * 1024))
        print(f"✅ 파일 생성 완료: {bin_filename}")
    except Exception as e:
        print(f"❌ 파일 생성 중 오류 발생: {e}")

    # 암호화하여 .enc 파일 생성
    encrypt_file(bin_filename, enc_filename)
