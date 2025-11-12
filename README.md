# Rule-based Autoformalization (RBA)

## Code: [WIP...]

## Test with ChatGPT

- **VanillaAF** 결과는 이미 있는 것을 적극적으로 활용하여 효율적인 것 같아보이는 코드들을 다양한 모습으로 만들어내지만 broken되는 경우도 나옴.
- **RBA** 결과는 기존의 라이브러리에 있는 구조들을 덜 활용하는 것처럼 보이나 상대적으로 일관된 구조와 덜 broken되는 구조로 나옴

### [Test1] Metric space

```
Object name: MetricSpace
Description: "A metric space is a set with a distance function"
```

- RBA result: https://chatgpt.com/share/68ffa6a4-ea64-8011-bfef-91666c107806
```
import Mathlib

namespace Scratch

class MetricSpace (α : Type*) where
  dist : α → α → ℝ
  dist_nonneg : ∀ x y : α, 0 ≤ dist x y
  dist_eq_zero_iff : ∀ x y : α, dist x y = 0 ↔ x = y
  dist_symm : ∀ x y : α, dist x y = dist y x
  dist_triangle : ∀ x y z : α, dist x z ≤ dist x y + dist y z

end Scratch

```
- Vanilla result: https://chatgpt.com/share/68ffa748-54ec-8011-a2af-1ab32c067e28
```
import Mathlib

namespace User

class MetricSpace (α : Type*) where
  dist : α → α → ℝ
  dist_nonneg : ∀ x y, 0 ≤ dist x y
  dist_eq_zero_iff : ∀ x y, dist x y = 0 ↔ x = y
  dist_symm : ∀ x y, dist x y = dist y x
  dist_triangle : ∀ x y z, dist x z ≤ dist x y + dist y z

end User
```

### [Test2] Linear Functional

```
Object name: LinearFunctional
Description: "A linear functional is a special type of linear map that takes a vector from a vector space and outputs a scalar (a number)."
```

- RBA result: https://chatgpt.com/share/68ffa7f3-ebb8-8011-97f7-ba0069da2eea
```
import Mathlib

structure LinearFunctional (R : Type _) (V : Type _) [Semiring R] [AddCommMonoid V] [Module R V] where
  to_fun : V → R
  map_add : ∀ x y : V, to_fun (x + y) = to_fun x + to_fun y
  map_smul : ∀ a : R, ∀ x : V, to_fun (a • x) = a • to_fun x
```

- Vanilla result: https://chatgpt.com/share/68ffa840-b544-8011-bd05-7a2f67e7b70c
```
import Mathlib

/-- A linear functional is a special type of linear map that takes a vector from a vector space
and outputs a scalar (a number). -/
abbrev LinearFunctional (𝕜 : Type*) (V : Type*)
    [Semiring 𝕜] [AddCommMonoid V] [Module 𝕜 V] :=
  V →ₗ[𝕜] 𝕜
```

### [Test3] Fourier Transform

```
Object name: FourierTransform
Description: "The Fourier transform is a mathematical operation that converts a function from the time (or spatial) domain into the frequency domain. For a function \( f \in L^1(\mathbb{R}) \), the Fourier transform \( \hat{f} : \mathbb{R} \to \mathbb{C} \) is defined by
\[ \hat{f}(\xi) = \int_{-\infty}^{\infty} f(x)\, e^{-2\pi i x \xi}\, dx. \]"
```

- RBA result: https://chatgpt.com/share/68ffa883-f4e8-8011-8a81-c2c8bc4842da
```
Output:
{
"is_expressible": false,
"lean4_type": null,
"confidence": 0.95,
"reasoning": "The Fourier transform here is a function/operator mapping L1(ℝ) to functions ℝ → ℂ, not a data type or interface. In Lean it would be a `def`/constant (possibly with lemmas), not an `inductive`, `structure`, or `class`."
}
```

- Vanilla result: https://chatgpt.com/share/68ffa8b3-233c-8011-93dd-fbc1458c0ebd
```
import Mathlib

noncomputable section

def FourierTransform (f : ℝ → ℂ) : ℝ → ℂ :=
  fun ξ => ∫ x : ℝ, f x * Complex.exp (-2 * Real.pi * Complex.I * ((x : ℂ) * (ξ : ℂ)))
```

### [Test4] Topological Vector Space

```
Object name: TVS
Description: "
**Definition (Topological Vector Space):** A **topological vector space (TVS)** is a vector space ( V ) over a field ( \mathbb{K} \in {\mathbb{R}, \mathbb{C}} ) equipped with a topology ( \tau ) such that: 1. The vector addition map [ * : V \times V \to V, \quad (x, y) \mapsto x + y ] is continuous with respect to the product topology on ( V \times V ). 2. The scalar multiplication map [ \cdot : \mathbb{K} \times V \to V, \quad (\alpha, x) \mapsto \alpha x ] is continuous.

**Brief Explanation:** A topological vector space is a vector space where the operations of addition and scalar multiplication behave continuously with respect to the given topology. This allows the combination of algebraic and topological methods, enabling concepts like convergence, continuity, and compactness to be studied in linear spaces.
"
```

- RBA result: https://chatgpt.com/share/68ffa8fc-423c-8011-adb7-0af51c333a45
```
import Mathlib

class TVS (K V : Type*) [Field K] [TopologicalSpace K] [AddCommGroup V] [Module K V] [TopologicalSpace V] : Prop where
  continuous_add : Continuous (fun p : V × V => p.1 + p.2)
  continuous_smul : Continuous (fun p : K × V => p.1 • p.2)
```

- Vanilla result: https://chatgpt.com/share/68ffa931-31a4-8011-bc4a-f4cc7ad72340
```
import Mathlib

universe u v

structure TVS (𝕂 : Type u) (V : Type v)
    [IsROrC 𝕂] [TopologicalSpace 𝕂] [TopologicalSpace V] [Module 𝕂 V] where
  continuous_add : Continuous (fun p : V × V => p.1 + p.2)
  continuous_smul : Continuous (fun p : 𝕂 × V => p.1 • p.2)
```







