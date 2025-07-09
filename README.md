### **1. `pip freeze > requirements.txt`**
- **역할**: 현재 Python 환경에 설치된 패키지들의 목록과 버전을 `requirements.txt` 파일로 저장합니다.
- **사용 예시**: 다른 개발자와 협업하거나, 동일한 환경을 재현할 때 유용합니다. 
- **결과**: `requirements.txt` 파일에는 아래와 같은 형식으로 설치된 패키지 정보가 저장됩니다.
  ```txt
  numpy==1.24.3
  pandas==2.0.1
  requests==2.28.2
  ```
- **추가 팁**: 이 파일을 사용해 동일한 환경을 복원하려면 `pip install -r requirements.txt` 명령어를 사용합니다.

---

### **2. `conda env export > environment.yml`**
- **역할**: 현재 Conda 환경을 `environment.yml` 파일로 내보냅니다.
- **사용 예시**: Conda 환경을 다른 컴퓨터나 팀원이 재현할 수 있도록 설정 정보를 공유할 때 사용합니다.
- **결과**: `environment.yml` 파일에는 패키지 이름, 버전, 환경 이름, 그리고 Python 버전이 YAML 형식으로 저장됩니다.
  ```yaml
  name: my_env
  channels:
    - defaults
  dependencies:
    - numpy=1.24.3
    - pandas=2.0.1
    - python=3.9
  ```
- **추가 팁**: 이 파일을 기반으로 환경을 복원하려면 `conda env create -f environment.yml` 명령어를 사용합니다.
- **추가 팁**: ubuntu에서 사용하려면 `conda env export --no-builds > environment_ubuntu.yml`
---

### **3. `git config --global credential.helper store`**
- **역할**: Git에서 인증 정보를 저장소에 저장해, 인증을 반복적으로 입력할 필요 없도록 합니다.
- **작동 원리**: 첫 인증 시 입력한 사용자 이름과 비밀번호를 로컬에 저장하며, 이후 같은 저장소에 접근할 때 이를 재사용합니다.
- **주의 사항**: 민감한 정보가 평문으로 저장되므로, 보안에 민감한 환경에서는 사용을 피하는 것이 좋습니다. 대신 `credential.helper cache` 또는 SSH 키를 사용하는 것이 안전합니다.

---

### **4. `git add . && git commit -m 'update env files' && git push`**
- **역할**: Git의 기본적인 작업을 하나로 묶어 처리합니다.
  1. **`git add .`**: 현재 디렉토리의 변경된 모든 파일을 스테이징 영역에 추가합니다.
  2. **`git commit -m 'update env files'`**: 스테이징된 파일들을 커밋하고, 메시지로 `'update env files'`를 작성합니다.
  3. **`git push`**: 로컬 저장소의 변경 내용을 원격 저장소에 푸시합니다.
- **추가 팁**:
  - 각 명령을 나눠서 사용할 수도 있습니다.
  - 특정 파일만 추가하려면 `git add filename`을 사용하면 됩니다.

