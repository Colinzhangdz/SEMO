# SEMO算法：二维随机矩阵上的多目标进化搜索

一个最小可复现的 **SEMO（Simple Evolutionary Multi-Objective）** 算法实现示例。  
每个矩阵格点 `(r, c)` 存储一对随机目标值 `[a, b]`（范围 `[0, 100]`）。  
程序生成随机矩阵、计算真实 Pareto 前沿、运行 SEMO（四邻域变异+环绕边界），并计算 SEMO 找到的非支配解集对真实前沿的**覆盖率**。

---

## ✳ 功能说明
- 随机生成二维 `[a, b]` 目标矩阵  
- 统一的 **支配关系** 与 **档案更新规则**（用于真实前沿与 SEMO）  
- 四邻域（上下左右）变异，环绕处理（wrap-around）  
- 覆盖率计算（命中数 / 真实前沿点数）  
- 打印矩阵、SEMO非支配解、真实Pareto前沿与覆盖率统计

---

## 💻 环境需求
- Python 3.8 及以上  
- `numpy` 库  

安装依赖：
```powershell
python -m pip install numpy
```
或（使用你当前的解释器路径）：
```powershell
& C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install numpy
```

---

## 🚀 运行方法
```powershell
python SEMO.py
```
或（在你的路径下运行）：
```powershell
& C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe C:\Users\83924\OneDrive\Documents\GitHub\SEMO\SEMO.py
```

---

## ⚙ 参数配置
在 `__main__` 部分可修改以下参数：
```python
interation_time = 1000  # SEMO迭代次数
rows, cols = 10, 10     # 矩阵大小
runs = 10000            # 重复运行次数（目前注释掉）
```

---

## 🧠 算法原理
- **严格支配（双目标最大化）**  
  `(a1, b1)` 严格支配 `(a2, b2)` 当且仅当  
  `a1 >= a2 and b1 >= b2` 且 `(a1 > a2 or b1 > b2)`。

- **档案更新规则**  
  1. 若候选点被档案中任一点支配 → 丢弃  
  2. 移除被候选点支配的档案点  
  3. 插入候选点（并去除等值重复）

- **变异**  
  从档案随机选父节点 → 随机移动到四邻域 → 环绕越界处理。

---

## 📊 输出内容
- 随机生成的 `[a, b]` 矩阵  
- SEMO 初始点与最终非支配集合  
- 真实 Pareto 前沿  
- 覆盖率结果

---

## 🛠 常见问题
- **`pip` 不被识别**  
  使用完整命令：
  ```powershell
  & C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install numpy
  ```
- **VS Code 解释器不一致**  
  使用快捷键 `Ctrl+Shift+P` → 搜索 **Python: Select Interpreter** → 选择正确路径。

---


# SEMO on Random 2D Objective Grid

A minimal and reproducible implementation of the **Simple Evolutionary Multi-Objective (SEMO)** algorithm on a 2-objective grid.  
Each cell `(r, c)` stores a random pair `[a, b]` within `[0, 100]`.  
The script generates a random matrix, computes the true Pareto front, runs SEMO with 4-neighbour mutation and wrap-around, and measures the coverage ratio.

---

## ✳ Features
- Random 2D matrix generator for `[a, b]`
- Unified dominance and archive-update rules
- 4-neighbour mutation with toroidal wrapping
- Coverage metric (hits / true Pareto front size)
- Verbose printing of the matrix, SEMO archive, and true Pareto front

---

## 💻 Requirements
- Python 3.8+
- `numpy`

Install dependencies:
```bash
python -m pip install numpy
```
Or, using your current interpreter:
```powershell
& C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install numpy
```

---

## 🚀 Run
```bash
python SEMO.py
```
or:
```powershell
& C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe C:\Users\83924\OneDrive\Documents\GitHub\SEMO\SEMO.py
```

---

## ⚙ Configuration
Edit in `__main__`:
```python
interation_time = 1000  # SEMO iterations
rows, cols = 10, 10     # grid size
runs = 10000            # repeated runs (commented out)
```

---

## 🧠 Algorithm Overview
- **Dominance (maximize both a, b)**  
  `(a1, b1)` dominates `(a2, b2)` if `(a1 >= a2 and b1 >= b2)` and `(a1 > a2 or b1 > b2)`.
- **Archive Update**  
  1. Discard if dominated.  
  2. Remove dominated members.  
  3. Insert candidate (no duplicates).  
- **Mutation**  
  Pick a random archive parent → move to one of 4 neighbours → wrap-around.

---

## 📊 Output
- Randomly generated `[a, b]` matrix  
- SEMO initial and final archive  
- True Pareto front  
- Coverage summary

---

## 🛠 Troubleshooting
- If `pip` not recognized:  
  ```powershell
  & C:\Users\83924\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install numpy
  ```
- Ensure correct interpreter in VS Code (`Ctrl+Shift+P` → “Python: Select Interpreter”).
