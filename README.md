# hdw_tools
hdw_tools는 제가 이것저것 하다가 필요에 의해 작성했던 스크립트 및 도구 모음입니다.  
각 스크립트는 특정 목적을 가지며, 반복적인 작업을 간소화하는 데 초점을 맞춥니다.

---

## 스크립트 목록

### `check_tree.sh`: 디렉토리 구조 확인 스크립트

**주요 기능**  
- `check_tree.sh`는 지정된 디렉토리의 구조를 `tree` 형태로 보여주는 셸 스크립트입니다.  
- 각 디렉토리 레벨에서 동일한 확장자를 가진 파일의 출력 개수를 제한하여 복잡한 프로젝트 구조를 간결하게 파악하는 데 도움을 줍니다.  

**의존성**
```bash
sudo apt update && sudo apt install tree
```

  <br>
  <details>
  <summary><b>사용법 및 실행 예시</b></summary>
    
  1. 사용법

   ```bash
   ./check_tree.sh [OPTIONS] [PATH]
   ```

   - [PATH]
       - 구조를 확인할 디렉토리의 경로입니다.
       - 생략할 경우, 현재 디렉토리 (.)를 기준으로 실행됩니다.

   - [OPTIONS]
     - -n <개수>
         - 각 디렉토리에서 확장자별로 표시할 최대 파일 수를 지정합니다.
         - 예를 들어 -n 3으로 설정하면, 각 디렉토리마다 .py 파일은 최대 3개, .txt 파일은 최대 3개까지만 표시됩니다.
         - 기본값은 2입니다.
     - -h
         - 사용법 도움말을 표시합니다.

   2. 실행예시

  <img width="426" height="857" alt="Image" src="https://github.com/user-attachments/assets/8e5b8178-c5fb-4ca1-aec4-5a95bacff2af" />
  
