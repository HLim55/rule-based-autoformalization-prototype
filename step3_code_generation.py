"""
Step 3: Lean4 코드 생성
구성 요소들을 바탕으로 완전한 Lean4 정의를 생성
"""

import re
from typing import List
from huggingface_hub import InferenceClient
from common import Lean4Type, ComponentInfo, Lean4Definition

class CodeGenerator:
    """Lean4 코드 생성기"""
    
    def __init__(self, client: InferenceClient):
        """
        초기화
        
        Args:
            client: Hugging Face InferenceClient 인스턴스
        """
        self.client = client
    
    def generate_lean4_definition(self, name: str, lean4_type: Lean4Type, 
                                components: List[ComponentInfo], 
                                description: str) -> Lean4Definition:
        """
        Lean4 정의 생성
        
        Args:
            name: 객체 이름
            lean4_type: Lean4 타입
            components: 구성 요소들
            description: 원본 설명 (LaTeX 포함 가능)
            
        Returns:
            Lean4Definition: 생성된 정의
        """
        components_text = "\\n".join([
            f"- {comp.name}: {comp.type_annotation} -- {comp.description}"
            for comp in components
        ])
        
        prompt = f"""
You are a Lean 4 formalization expert.

Generate a complete and syntactically correct Lean 4 definition using the following information.

Object name: {name}
Type: {lean4_type.value}
Description: {description}

Components:
{components_text}

---

### Instructions
- Use the provided components to construct a valid Lean 4 `{lean4_type.value}` definition.
- Include necessary imports (e.g., `import Mathlib`).
- Use proper Lean 4 syntax and indentation.
- Each component becomes one line in the definition body.
- Do NOT include any explanation, markdown, or prose. Output ONLY a Lean 4 code block.

### Output format examples

**For structure:**
```lean
import Mathlib

structure Point2D where
  x : ℝ
  y : ℝ
```

**For class:**
```lean
import Mathlib

class Monoid (G : Type*) where
  mul : G → G → G
  one : G
  mul_assoc : ∀ a b c : G, mul (mul a b) c = mul a (mul b c)
  one_mul : ∀ a : G, mul one a = a
  mul_one : ∀ a : G, mul a one = a
```

**For inductive:**
```lean
import Mathlib

inductive BinaryTree (α : Type*) where
  | leaf : BinaryTree α
  | node : α → BinaryTree α → BinaryTree α → BinaryTree α
```
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages, max_tokens=1000)
            result_text = response.choices[0].message.content.strip()
            
            # ```lean 또는 ```lean4 코드 블록 추출
            code_match = re.search(r'```lean4?\\n(.*?)\\n```', result_text, re.DOTALL)
            if code_match:
                lean4_code = code_match.group(1).strip()
            else:
                # 코드 블록이 없으면 전체 텍스트 사용
                lean4_code = result_text
            
            # 의존성 추출 (import 문에서)
            dependencies = re.findall(r'import\\s+([^\\s\\n]+)', lean4_code)
            
            return Lean4Definition(
                name=name,
                type=lean4_type,
                components=components,
                lean4_code=lean4_code,
                dependencies=dependencies
            )
            
        except Exception as e:
            return Lean4Definition(
                name=name,
                type=lean4_type,
                components=components,
                lean4_code=f"-- 오류 발생: {str(e)}",
                dependencies=[]
            )