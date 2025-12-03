import numpy as np
import random
import time 
#创建一个100*100的矩阵,每个位置有两个随机数[a,b]，使用多次运行SEMO算法寻找非支配解集，并计算覆盖率
"""
1. 生成一个100x100的矩阵,每个位置有两个随机数[a,b]
2. 实现Pareto前沿点的查找函数
3. 实现SEMO算法寻找非支配解集
4. 计算SEMO找到的非支配解集与真实Pareto前沿点的覆盖率
"""
def generate_matrix(rows, cols, value_range=(0, 100), decimals=2):
    """
    生成一个 (rows x cols x 2) 的矩阵。
    每个位置有两个随机数：[a, b]
    随机数的取值范围是 value_range，保留小数点后 decimals 位。
    例如，value_range=(0, 100)，decimals=2，则生成的数值可能是 23.45, 67.89 等等。
    返 回值：numpy 数组，形状为 (rows, cols, 2)
    """
    mat = np.random.rand(rows, cols, 2) * (value_range[1] - value_range[0]) + value_range[0]
    return np.round(mat, decimals)

def update_population(population, cand, mat):
    cr, cc = cand
    ca, cb = mat[cr, cc]

    # 0) 若已有等值点，直接忽略（去重）
    for (r, c) in population:
        a, b = mat[r, c]
        if a == ca and b == cb:
            return False

    # 1) 若 cand 被任何现有点严格支配 → 丢弃
    for (r, c) in population:
        a, b = mat[r, c]
        if dominates_val(a, b, ca, cb):
            return False

    # 2) 移除被 cand 严格支配的点
    new_pop = []
    for (r, c) in population:
        a, b = mat[r, c]
        if dominates_val(ca, cb, a, b):
            continue
        new_pop.append((r, c))

    new_pop.append(cand)
    population[:] = new_pop
    return True

def pareto_best_points(mat):
    """
    使用与 update_population 相同的档案更新规则，
    扫描整张矩阵得到真实非支配解集合（双目标最大化）。
    返回 [(r, c, a, b)]，按 a 降序、b 降序排序。
    """
    rows, cols, _ = mat.shape
    archive = []  # 与 SEMO 的 population 结构一致：[(r, c), ...]

    # 逐点尝试入档（全局后滤）
    for r in range(rows):
        for c in range(cols):
            update_population(archive, (r, c), mat)

    # 排序：a 降序，b 降序
    archive.sort(key=lambda rc: (-mat[rc[0], rc[1], 0], -mat[rc[0], rc[1], 1]))

    # 组装返回格式 (r, c, a, b)
    return [(r, c, mat[r, c, 0], mat[r, c, 1]) for (r, c) in archive]

def dominates_val(a1, b1, a2, b2):
    """严格支配：双目标最大化"""
    return (a1 >= a2 and b1 >= b2) and (a1 > a2 or b1 > b2)


# 4dir SEMO 变异与停滞检测相关函数
def mutate_neighbor(r, c, rows, cols):
    moves = [(1,0), (-1,0), (0,1), (0,-1)]
    dr, dc = random.choice(moves)
    nr = r + dr
    nc = c + dc
    # 环绕处理（wrap-around）
    if nr < 0:
        nr = rows - 1
    elif nr >= rows:
        nr = 0

    if nc < 0:
        nc = cols - 1
    elif nc >= cols:
        nc = 0
    return (nr, nc)

# 8dir SEMO 变异函数
def mutate_neighbor_eight(r, c, rows, cols):
    moves = [(1,0), (-1,0), (0,1), (0,-1),
             (1,1), (-1,-1), (1,-1), (-1,1)]
    dr, dc = random.choice(moves)
    nr = r + dr
    nc = c + dc

    if nr < 0:
        nr = rows - 1
    elif nr >= rows:
        nr = 0

    if nc < 0:
        nc = cols - 1
    elif nc >= cols:
        nc = 0

    return (nr, nc)

#4dir 邻居支配检测函数
def all_neighbors_dominated(population, mat, rows, cols):
    """
    检查当前 population 的所有邻居是否都已经被 population 中的点支配：
    对于 population 中每个点 (r,c) 的四邻域，如果每个邻居要么在 population 里，
    要么被 population 中某个点严格支配，则返回 True。
    """
    moves = [(1,0), (-1,0), (0,1), (0,-1)]

    for (r, c) in population:
        for dr, dc in moves:
            nr = (r + dr) % rows
            nc = (c + dc) % cols
            a_n, b_n = mat[nr, nc]

            dominated = False
            for (pr, pc) in population:
                a_p, b_p = mat[pr, pc]
                # 自己在种群中，或者被某个点严格支配，都算“被覆盖”
                if (pr == nr and pc == nc) or dominates_val(a_p, b_p, a_n, b_n):
                    dominated = True
                    break

            # 只要发现一个邻居没有被任何档案点支配，就还没“全体邻居被支配”
            if not dominated:
                return False

    return True
#8dir 邻居支配检测函数
def all_neighbors_dominated_eight(population, mat, rows, cols):
    moves = [(1,0), (-1,0), (0,1), (0,-1),
             (1,1), (-1,-1), (1,-1), (-1,1)]

    for (r, c) in population:
        for dr, dc in moves:
            nr = (r + dr) % rows
            nc = (c + dc) % cols
            a_n, b_n = mat[nr, nc]

            dominated = False
            for (pr, pc) in population:
                a_p, b_p = mat[pr, pc]
                if (pr == nr and pc == nc) or dominates_val(a_p, b_p, a_n, b_n):
                    dominated = True
                    break

            if not dominated:
                return False

    return True

def run_semo(mat, iterations):
    rows, cols, _ = mat.shape

    # 当前“位置”的索引（注意：是索引，不是目标值）
    cur_r = random.randrange(rows)
    cur_c = random.randrange(cols)
    population = [(cur_r, cur_c)]
    a, b = mat[cur_r, cur_c]
    print(f"\n========== SEMO 初始点 ==========")
    print(f"({cur_r:2d},{cur_c:2d}) -> a={a:7.2f}, b={b:7.2f}")

    # 迭代搜索，每次从 population 随机选择一个父节点，变异到邻居，尝试加入档案
    for _ in range(iterations):
        # 先从population选择一个父节点
        parent_r, parent_c = random.choice(population)

        # 从父节点随机走到四邻域的一个邻居（wrap-around）
        child_r, child_c = mutate_neighbor(parent_r, parent_c, rows, cols)

        # 尝试加入档案
        update_population(population, (child_r, child_c), mat)

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0], -mat[rc[0], rc[1], 1]))
    return population

def run_semo_eight(mat, iterations):
    rows, cols, _ = mat.shape

    cur_r = random.randrange(rows)
    cur_c = random.randrange(cols)
    population = [(cur_r, cur_c)]

    for _ in range(iterations):
        parent_r, parent_c = random.choice(population)
        child_r, child_c = mutate_neighbor_eight(parent_r, parent_c, rows, cols)
        update_population(population, (child_r, child_c), mat)

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0],
                                    -mat[rc[0], rc[1], 1]))
    return population

def semo_coverage_rate(semo_pop, true_front):
    true_coords = {(r, c) for (r, c, a, b) in true_front}
    semo_coords = set(semo_pop)
    hit = len(true_coords & semo_coords)
    total = len(true_coords)
    rate = hit / total if total > 0 else 0.0
    return hit, total, rate

def run_semo_with_stagnation(mat, iterations):
    rows, cols, _ = mat.shape
    cur_r = random.randrange(rows)
    cur_c = random.randrange(cols)
    population = [(cur_r, cur_c)]

    # 默认认为一直跑到 iterations 才“停滞”
    stagnation_steps = iterations

    for step in range(iterations):
        parent_r, parent_c = random.choice(population)
        child_r, child_c = mutate_neighbor(parent_r, parent_c, rows, cols)
        update_population(population, (child_r, child_c), mat)

        # ✅ 检查：当前 population 的所有邻居是否都已经被 population 支配
        if all_neighbors_dominated(population, mat, rows, cols):
            stagnation_steps = step + 1   # 第几次迭代达到“所有邻居被支配”
            break

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0],
                                    -mat[rc[0], rc[1], 1]))
    return population, stagnation_steps

def run_semo_with_stagnation_eight(mat, iterations):
    rows, cols, _ = mat.shape

    cur_r = random.randrange(rows)
    cur_c = random.randrange(cols)
    population = [(cur_r, cur_c)]

    stagnation_steps = iterations

    for step in range(iterations):
        parent_r, parent_c = random.choice(population)
        child_r, child_c = mutate_neighbor_eight(parent_r, parent_c, rows, cols)
        update_population(population, (child_r, child_c), mat)

        if all_neighbors_dominated_eight(population, mat, rows, cols):
            stagnation_steps = step + 1
            break

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0],
                                    -mat[rc[0], rc[1], 1]))
    return population, stagnation_steps

def run_semo_with_start(mat, iterations, start_r, start_c):
    rows, cols, _ = mat.shape
    population = [(start_r, start_c)]

    for _ in range(iterations):
        parent_r, parent_c = random.choice(population)
        child_r, child_c = mutate_neighbor(parent_r, parent_c, rows, cols)
        update_population(population, (child_r, child_c), mat)

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0],
                                    -mat[rc[0], rc[1], 1]))
    return population

def run_semo_eight_with_start(mat, iterations, start_r, start_c):
    rows, cols, _ = mat.shape
    population = [(start_r, start_c)]

    for _ in range(iterations):
        parent_r, parent_c = random.choice(population)
        child_r, child_c = mutate_neighbor_eight(parent_r, parent_c, rows, cols)
        update_population(population, (child_r, child_c), mat)

    population.sort(key=lambda rc: (-mat[rc[0], rc[1], 0],
                                    -mat[rc[0], rc[1], 1]))
    return population

if __name__ == "__main__":
    # 参数设置
    interation_time = 100000   # 每次 SEMO 的迭代次数
    rows, cols = 10, 10        # 矩阵大小
    runs = 10000               # 重复运行 SEMO 的次数

    # ========== 1. 生成矩阵并打印 ==========
    m = generate_matrix(rows, cols, (0, 100), 2)
    print("========== 随机生成的矩阵 ==========")
    for r in range(rows):
        for c in range(cols):
            a, b = m[r, c]
            print(f"[{a:6.2f}, {b:6.2f}]", end="  ")
        print()

    # ========== 2. 计算真实 Pareto 前沿 ==========
    real_front = pareto_best_points(m)

    print("\n========== 真实 Pareto 前沿 ==========")
    for (r, c, a, b) in real_front:
        print(f"({r:2d},{c:2d}) -> a={a:7.2f}, b={b:7.2f}")

    # 为后面覆盖率计算准备坐标集合
    true_coords = {(r, c) for (r, c, a, b) in real_front}
    total_true = len(true_coords)

    # ========== 3. 单次运行：同一起点的 4 邻居 vs 8 邻居 SEMO ==========
    start_r = random.randrange(rows)
    start_c = random.randrange(cols)
    a0, b0 = m[start_r, start_c]

    print("\n========== 统一 SEMO 起点 ==========")
    print(f"起点 = ({start_r:2d},{start_c:2d}) -> a={a0:7.2f}, b={b0:7.2f}")

    # 从同一起点分别运行 4 邻居 和 8 邻居 SEMO（不带停滞判断，只看最终档案）
    semo_pop_4 = run_semo_with_start(m, interation_time, start_r, start_c)
    semo_pop_8 = run_semo_eight_with_start(m, interation_time, start_r, start_c)

    print("\n========== 4 邻居 SEMO 最终非支配集合 ==========")
    for (r, c) in semo_pop_4:
        a, b = m[r, c]
        print(f"({r:2d},{c:2d}) -> a={a:7.2f}, b={b:7.2f}")

    print("\n========== 8 邻居 SEMO 最终非支配集合 ==========")
    for (r, c) in semo_pop_8:
        a, b = m[r, c]
        print(f"({r:2d},{c:2d}) -> a={a:7.2f}, b={b:7.2f}")

    # 单次覆盖率对比
    valid_hits_4 = sum(1 for (r, c) in semo_pop_4 if (r, c) in true_coords)
    cover_4 = valid_hits_4 / total_true if total_true > 0 else 0.0

    valid_hits_8 = sum(1 for (r, c) in semo_pop_8 if (r, c) in true_coords)
    cover_8 = valid_hits_8 / total_true if total_true > 0 else 0.0

    print("\n========== 单次运行覆盖情况（同一起点） ==========")
    print(f"4 邻居 SEMO 集合个数 = {len(semo_pop_4)}")
    print(f"4 邻居命中的真实 Pareto 点个数 = {valid_hits_4}")
    print(f"4 邻居单次覆盖率 = {cover_4:.4f} ({cover_4*100:.2f}%)")

    print(f"\n8 邻居 SEMO 集合个数 = {len(semo_pop_8)}")
    print(f"8 邻居命中的真实 Pareto 点个数 = {valid_hits_8}")
    print(f"8 邻居单次覆盖率 = {cover_8:.4f} ({cover_8*100:.2f}%)")

    # ========== 4. 多次运行：统计期望覆盖率 & 停滞步数 ==========
    coverage_list = []
    stagnation_list = []

    coverage_list_eight = []
    stagnation_list_eight = []

    print(f"\n开始进行 {runs} 次 SEMO 运行统计（带停滞判断）...")

    # 4 邻居：使用带“邻居停滞判断”的版本
    for i in range(runs):
        semo_pop, stagnation_steps = run_semo_with_stagnation(m, interation_time)
        _, _, rate = semo_coverage_rate(semo_pop, real_front)
        coverage_list.append(rate)
        stagnation_list.append(stagnation_steps)

    # 8 邻居：使用 8 方向邻居停滞判断版本
    for i in range(runs):
        semo_pop_eight, stagnation_steps_eight = run_semo_with_stagnation_eight(m, interation_time)
        _, _, rate_eight = semo_coverage_rate(semo_pop_eight, real_front)
        coverage_list_eight.append(rate_eight)
        stagnation_list_eight.append(stagnation_steps_eight)

    coverage_arr = np.array(coverage_list)
    stagnation_arr = np.array(stagnation_list)
    coverage_arr_eight = np.array(coverage_list_eight)
    stagnation_arr_eight = np.array(stagnation_list_eight)

    mean_cov = coverage_arr.mean()
    std_cov = coverage_arr.std()  # 总体标准差
    mean_stag = stagnation_arr.mean()
    std_stag = stagnation_arr.std()
    std_stag_eight = stagnation_arr_eight.std()

    mean_cov_eight = coverage_arr_eight.mean()
    std_cov_eight = coverage_arr_eight.std()
    mean_stag_eight = stagnation_arr_eight.mean()

    print("\n========== 多次运行统计结果 ==========")
    print(f"运行次数: {runs}")
    print("============== 4 neighbor 结果 ============")
    print(f"4 neighbor 平均覆盖率: {mean_cov:.4f} ({mean_cov*100:.2f}%)")
    print(f"4 neighbor 覆盖率标准差: {std_cov:.4f} ({std_cov*100:.2f} %)")
    print(f"4 neighbor 最少停滞步数: {stagnation_arr.min()}")
    print(f"4 neighbor 最多停滞步数: {stagnation_arr.max()}")
    print(f"4 neighbor 平均停滞步数: {mean_stag:.2f}")
    print(f"4 neighbor 停滞步数标准差: {std_stag:.2f}")
    print("=====================================")
    print("============== 8 neighbor 结果 ============")
    print(f"8 neighbor 平均覆盖率: {mean_cov_eight:.4f} ({mean_cov_eight*100:.2f}%)")
    print(f"8 neighbor 覆盖率标准差: {std_cov_eight:.4f} ({std_cov_eight*100:.2f} %)")
    print(f"8 neighbor 最少停滞步数: {stagnation_arr_eight.min()}")
    print(f"8 neighbor 最多停滞步数: {stagnation_arr_eight.max()}")
    print(f"8 neighbor 平均停滞步数: {mean_stag_eight:.2f}")
    print(f"8 neighbor 停滞步数标准差: {std_stag_eight:.2f}")
    print("=====================================") 