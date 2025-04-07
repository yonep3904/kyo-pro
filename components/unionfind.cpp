
/*
Usage:
  UnionFind uf(n);
  uf.unite(x, y); // xとyを併合
  uf.same(x, y);  // xとyが同じ集合に属するか
  uf.find(x);     // xの根を返す
  uf.size(x);     // xが属する集合のサイズを返す

Example:
  UnionFind uf(N);
  uf.unite(0, 1);
  uf.unite(1, 2);
  bool res = uf.same(0, 2);  // true
  int sz = uf.size(0);       // 3
  int root = uf.find(0);     // 0の根を返す
*/

#include <vector>
class UnionFind {
private:
    // parent[i] : iの親, sz[i] : iが根のときの集合サイズ
    std::vector<int> parent, sz;

public:
    UnionFind(int n) : parent(n, -1), sz(n, 1) {}

    int find(int x) {
        if (parent[x] == -1) return x;
        return parent[x] = find(parent[x]);  // 経路圧縮
    }

    bool same(int x, int y) {
        return find(x) == find(y);
    }

    bool unite(int x, int y) {
        x = find(x);
        y = find(y);
        if (x == y) return false;

        if (sz[x] < sz[y]) std::swap(x, y);  // サイズが大きい方に併合
        parent[y] = x;
        sz[x] += sz[y];
        return true;
    }

    int size(int x) {
        return sz[find(x)];
    }
};

