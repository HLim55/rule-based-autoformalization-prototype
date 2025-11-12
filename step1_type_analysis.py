"""
Step 1: 타입 분석
자연어 설명을 분석하여 Lean4 타입(inductive/structure/class)으로 표현 가능한지 판단
"""

import json
import re
from typing import Optional
from huggingface_hub import InferenceClient
from common import Lean4Type, TypeAnalysisResult

class TypeAnalyzer:
    """타입 분석기"""
    
    def __init__(self, client: InferenceClient):
        """
        초기화
        
        Args:
            client: Hugging Face InferenceClient 인스턴스
        """
        self.client = client
    
    def analyze_type(self, description: str) -> TypeAnalysisResult:
        """
        자연어 설명을 분석하여 Lean4 타입으로 표현 가능한지 판단
        
        Args:
            description: 수학적 객체의 자연어 설명 (LaTeX 포함 가능)
            
        Returns:
            TypeAnalysisResult: 분석 결과
        """
        prompt = f"""
Instruction:

Analyze the following description of a mathematical object and determine whether it can be represented in Lean 4 as an `inductive`, `structure`, or `class` type.

Description:
{description}

Type definitions in Lean 4:
- inductive — General data types defined by constructors (possibly recursive or indexed). Used for objects built from base cases and constructors (e.g., natural numbers, lists, trees).
- structure — A single-constructor, non-recursive inductive type that groups named fields. Used for records or algebraic structures composed of components (e.g., a point with coordinates, a group with operations).
- class — A structure marked as a type class, providing an interface that can have multiple instances for different types (e.g., `Monoid`, `Group`, `Ring`).

---

### Examples

**Example 1**
Description: "The natural numbers are defined inductively with 0 and the successor function."
Output:
{{
  "is_expressible": true,
  "lean4_type": "inductive",
  "confidence": 0.95,
  "reasoning": "It is recursively defined with base case and constructor, typical of inductive types."
}}

**Example 2**
Description: "A group $(G, \\cdot)$ is a set $G$ together with a binary operation $\\cdot : G \\times G \\to G$ satisfying the following axioms:
1. $(x \\cdot y) \\cdot z = x \\cdot (y \\cdot z)$ for all $x, y, z \\in G$ (associativity);
2. there exists $e \\in G$ such that $e \\cdot x = x \\cdot e = x$ for all $x \\in G$ (identity);
3. for each $x \\in G$ there exists $x^{{-1}} \\in G$ such that $x \\cdot x^{{-1}} = x^{{-1}} \\cdot x = e$ (inverse)."
Output:
{{
  "is_expressible": true,
  "lean4_type": "class",
  "confidence": 0.95,
  "reasoning": "A group specifies a carrier type, operations, and laws, making it a canonical example of a Lean type class."
}}

**Example 3**
Description: "A monoid is a type with a binary operation and an identity element satisfying associativity."
Output:
{{
  "is_expressible": true,
  "lean4_type": "class",
  "confidence": 0.85,
  "reasoning": "A monoid is an abstract interface describing operations and laws over any type, suitable as a type class."
}}

**Example 4**
Description: "A real matrix of size $m \\times n$ is a function $A : \\{{1,\\dots,m\\}} \\times \\{{1,\\dots,n\\}} \\to \\mathbb{{R}}$, defined by $A = (a_{{ij}})$, where each entry $a_{{ij}} \\in \\mathbb{{R}}$."
Output:
{{
  "is_expressible": true,
  "lean4_type": "structure",
  "confidence": 0.9,
  "reasoning": "A matrix has fixed dimensions and components; it is naturally modeled as a structure or a dependent type indexed by size."
}}

**Example 5**
Description: "A binary operation * on a set G is a function * : G × G → G."
Output:
{{
  "is_expressible": false,
  "lean4_type": null,
  "confidence": 0.95,
  "reasoning": "It defines a function, not a data type or structure."
}}

**Example 6**
Description: "$\\mathbb{{R}}^2 = \\{{(x,y) : x,y \\in \\mathbb{{R}}\\}}$"
Output:
{{
  "is_expressible": true,
  "lean4_type": "structure",
  "confidence": 0.9,
  "reasoning": "Represents ordered pairs of real numbers, suitable as a structure with two fields."
}}

---

Respond strictly in the following JSON format:
{{
    "is_expressible": true/false,
    "lean4_type": "inductive" | "structure" | "class" | null,
    "confidence": 0.0–1.0,
    "reasoning": "Brief explanation of why this type best fits the description"
}}
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(messages, max_tokens=500)
            result_text = response.choices[0].message.content.strip()
            
            # JSON 추출 - 여러 패턴 시도
            result_data = None
            
            # 방법 1: JSON 코드 블록
            json_block_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_block_match:
                try:
                    result_data = json.loads(json_block_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # 방법 2: 중괄호 패턴
            if not result_data:
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        result_data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
            
            if result_data:
                
                lean4_type = None
                if result_data.get("lean4_type"):
                    lean4_type = Lean4Type(result_data["lean4_type"])
                
                return TypeAnalysisResult(
                    is_expressible=result_data.get("is_expressible", False),
                    lean4_type=lean4_type,
                    confidence=result_data.get("confidence", 0.0),
                    reasoning=result_data.get("reasoning", "")
                )
            else:
                # 디버깅을 위해 실제 응답 포함
                return TypeAnalysisResult(False, None, 0.0, f"JSON 파싱 실패. 응답: {result_text[:200]}...")
                
        except Exception as e:
            return TypeAnalysisResult(False, None, 0.0, f"오류 발생: {str(e)}")