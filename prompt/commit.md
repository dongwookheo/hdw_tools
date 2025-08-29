# Git Commit Message Convention

이 문서는 Chris Beams의 블로그 포스트 [How to Write a Git Commit Message](https://cbea.ms/git-commit/)를 기반으로 작성된 Git 커밋 메시지 작성 가이드입니다.
일관되고 명확한 커밋 메시지는 프로젝트의 유지보수성을 높이고, 동료 개발자(그리고 미래의 나 자신)와의 소통을 원활하게 하는 가장 중요한 도구입니다.

## 커밋 메시지 구조

잘 작성된 커밋 메시지는 **제목(Subject)**, **본문(Body)**, 그리고 필요한 경우 **꼬리말(Footer)** 세 부분으로 구성됩니다.

```
<제목: 50자 이내의 요약>

<본문: '무엇을', '왜' 변경했는지에 대한 상세 설명. 한 줄에 72자 권장>

<꼬리말: 이슈 트래커 ID 등 참조 정보>
```

-----

## 7가지 핵심 규칙

### 1\. 제목과 본문은 한 줄의 공백으로 분리하세요 (Separate subject from body with a blank line)

  - 제목과 본문 사이의 빈 줄은 Git이 두 요소를 명확하게 구분하는 데 필수적입니다.
  - 이 규칙을 지켜야 `git log --oneline`, `git shortlog`와 같은 명령어에서 제목만 깔끔하게 표시됩니다.
  - 간단한 변경이라 본문이 필요 없다면 이 규칙은 적용되지 않습니다.

### 2\. 제목은 50자 이내로 제한하세요 (Limit the subject line to 50 characters)

  - 50자는 변경 사항을 간결하게 요약하기에 충분한 길이이며, 가독성을 해치지 않습니다.
  - GitHub 등 대부분의 Git UI는 50자가 넘는 제목을 잘라서 표시하므로, 핵심 내용이 잘리지 않도록 50자 내로 작성하는 것을 목표로 합니다. (최대 72자를 넘지 않도록 합니다.)
  - 만약 제목을 요약하기 어렵다면, 한 번에 너무 많은 변경 사항을 커밋하려는 것일 수 있습니다. (Atomic Commits 지향)

### 3\. 제목 첫 글자는 대문자로 작성하세요 (Capitalize the subject line)

  - 문장의 시작을 알리는 관례적인 규칙입니다.
  - **Good**: `Add user authentication feature`
  - **Bad**: `add user authentication feature`

### 4\. 제목 끝에 마침표를 찍지 마세요 (Do not end the subject line with a period)

  - 제목은 완전한 문장이 아닌 요약문이므로 마침표는 불필요합니다.
  - 제한된 공간(50자)을 효율적으로 사용하기 위함이기도 합니다.
  - **Good**: `Open the pod bay doors`
  - **Bad**: `Open the pod bay doors.`

### 5\. 제목은 명령문(Imperative mood)으로 작성하세요 (Use the imperative mood in the subject line)

  - "무엇을 했다" (과거형)가 아니라, "무엇을 하라" (명령형) 스타일로 작성합니다.
  - 이는 Git이 `git merge`, `git revert` 시 자동으로 생성하는 커밋 메시지 스타일과 일치시켜 일관성을 유지합니다.
  - **올바른지 확인하는 쉬운 방법:**
      - `If applied, this commit will <your subject line>` 라는 문장이 자연스럽게 완성되어야 합니다.
      - (O) `If applied, this commit will **Refactor** subsystem X for readability`
      - (O) `If applied, this commit will **Update** getting started documentation`
      - (X) `If applied, this commit will **Fixed** bug with Y`
      - (X) `If applied, this commit will **Changing** behavior of X`

### 6\. 본문은 72자마다 줄바꿈하세요 (Wrap the body at 72 characters)

  - Git은 텍스트를 자동으로 줄바꿈하지 않습니다.
  - 터미널에서 `git log`를 봤을 때, 들여쓰기 공간을 고려해도 전체 라인이 80자를 넘어가지 않아 가독성이 크게 향상됩니다.

### 7\. 본문을 사용하여 '무엇을'과 '왜'를 설명하세요 ('어떻게'가 아닌) (Use the body to explain *what* and *why* vs. *how*)

  - 코드 자체는 '어떻게(How)' 변경되었는지를 보여줍니다.
  - 커밋 메시지의 본문은 \*\*코드를 보지 않고도 이해할 수 있는 맥락(Context)\*\*을 제공해야 합니다.
      - 이 변경 전에는 어떤 문제가 있었는가?
      - **무엇을** 변경하여 그 문제를 해결했는가?
      - **왜** 이런 방식을 선택했는가?
  - 이 커밋이 가져올 수 있는 부수 효과나 다른 비직관적인 결과가 있다면 이곳에 설명합니다.

-----

## 종합 예시

```
50자 이내로 변경 사항 요약

필요하다면 더 자세한 설명을 작성합니다. 한 줄에 72자 정도에서
줄바꿈을 해주는 것이 좋습니다. 첫 번째 줄은 제목, 그리고 한 줄을
비우고 시작하는 이 부분이 본문이 됩니다. 이 빈 줄은 매우 중요하며,
`log`, `shortlog`, `rebase` 같은 도구들이 메시지를 올바르게
인식하기 위해 반드시 필요합니다.

이 커밋이 해결하려는 문제를 설명합니다. '어떻게'보다는 '왜' 이 변경을
만들었는지에 초점을 맞춥니다. (코드가 '어떻게'를 설명합니다).
이 변경으로 인한 부수 효과나 예상치 못한 결과가 있나요?
이곳에 설명하기 가장 좋은 장소입니다.

단락 추가는 빈 줄로 구분합니다.

 - 글머리 기호(Bullet points)를 사용하는 것도 좋습니다.
 - 보통 하이픈(-)이나 별표(*)를 사용하며, 한 칸을 띄웁니다.

이슈 트래커를 사용한다면, 아래와 같이 꼬리말(Footer)에 참조를
추가할 수 있습니다.

Resolves: #123
See also: #456, #789
```
