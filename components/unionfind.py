
# Usage:
#  UnionFind uf(n);
#  uf.unite(x, y); # xとyを併合
#  uf.same(x, y);  # xとyが同じ集合に属するか
#  uf.find(x);     # xの根を返す
#  uf.size(x);     # xが属する集合のサイズを返す

# Example:
#  UnionFind uf(N);
#  uf.unite(0, 1);
#  uf.unite(1, 2);
#  bool res = uf.same(0, 2);  # true
#  int sz = uf.size(0);       # 3
#  int root = uf.find(0);     # 0の根を返す

class UnionFind:
    def __init__(self, n):
        self.parent = [-1] * n
        self.size_ = [1] * n

    def find(self, x):
        if self.parent[x] == -1:
            return x
        self.parent[x] = self.find(self.parent[x])  # 経路圧縮
        return self.parent[x]

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def unite(self, x, y):
        x = self.find(x)
        y = self.find(y)
        if x == y:
            return False

        if self.size_[x] < self.size_[y]:
            x, y = y, x
        self.parent[y] = x
        self.size_[x] += self.size_[y]
        return True

    def size(self, x):
        return self.size_[self.find(x)]
