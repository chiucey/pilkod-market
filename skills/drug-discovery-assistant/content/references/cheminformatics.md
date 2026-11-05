# Cheminformatics Reference

## RDKit 基础操作

### 分子读取和写入

```python
from rdkit import Chem

# 从SMILES读取
mol = Chem.MolFromSmiles('CC(=O)OC1=CC=CC=C1C(=O)O')

# 从Mol Block读取
mol = Chem.MolFromMolBlock(mol_block)

# 转换为SMILES
smiles = Chem.MolToSmiles(mol)

# 转换为SMARTS
smart = Chem.MolToSmarts(mol)
```

### 分子指纹

```python
from rdkit.Chem import AllChem

# Morgan指纹 (ECFP)
fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)

# RDKit指纹
fp = Chem.RDKFingerprint(mol)
```

### 分子描述符

```python
from rdkit.Chem import Descriptors, Crippen

# 基本描述符
mw = Descriptors.MolWt(mol)
logp = Descriptors.MolLogP(mol)
tpsa = Descriptors.TPSA(mol)
hbd = Descriptors.NumHDonors(mol)
hba = Descriptors.NumHAcceptors(mol)

# LogP计算
logp = Crippen.MolLogP(mol)
```

## DeepChem 基础

### 数据加载

```python
import deepchem as dc

# 加载分子数据集
loader = dc.data.CSVLoader(tasks=["hERG_binding"], feature_field="smiles", id_field="id")
dataset = loader.create_dataset('hERG_data.csv')

# 分子特征化
featurizer = dc.feat.ConvMolFeaturizer()
features = featurizer.featurize(dataset.X)
```

### 模型训练

```python
# 图卷积模型
model = dc.models.GraphConvModel(n_tasks=1, mode='regression')
model.fit(dataset, nb_epoch=50)

# 预测
predictions = model.predict(test_dataset)
```

## 分子对接

### AutoDock Vina

```bash
# 准备受体
prepare_receptor -r protein.pdbqt -o protein_out.pdbqt

# 准备配体
prepare_ligand -l ligand.sdf -o ligand_out.pdbqt

# 运行对接
vina --receptor protein_out.pdbqt \
     --ligand ligand_out.pdbqt \
     --center_x 10 --center_y 20 --center_z 30 \
     --size_x 20 --size_y 20 --size_z 20 \
     --out result.pdbqt
```

### PyMOL 可视化

```python
# 分子结构渲染
cmd.fetch('1ABC')  # 加载PDB结构
cmd.show('sticks')  # 显示为棍状
cmd.color('cyan', 'chain A')  # 着色
```

## ADMET 预测

### 吸收

| 参数 | 说明 | 预测方法 |
|------|------|----------|
| Caco-2 | 肠吸收模型 | 机器学习 |
| MDCK | 肾小管渗透 | 实验数据 |
| 溶解度 | 水溶性 | 基于结构 |

### 代谢

| 参数 | 说明 |
|------|------|
| CYP抑制 | 代谢酶抑制 |
| CYP底物 | 代谢酶底物 |
| 代谢稳定性 | 肝微粒体稳定性 |

### 毒性

| 终点 | 说明 |
|------|------|
| hERG | 心脏毒性 |
| Ames | 致突变性 |
| DILI | 药物性肝损伤 |

### 预测规则 (Lipinski's Rule of 5)

- MW < 500
- LogP < 5
- HBD ≤ 5
- HBA ≤ 10

## QSAR 建模

### 数据准备

```python
import pandas as pd
from rdkit import Chem

# 读取数据
df = pd.read_csv('compounds.csv')

# 生成描述符
def calc_descriptors(smiles):
    mol = Chem.MolFromSmiles(smiles)
    return {
        'MW': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        # ... 更多描述符
    }
```

### 模型训练

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)
```

## 常用化学信息学库

| 库 | 语言 | 主要功能 |
|----|------|----------|
| RDKit | Python/C++ | 分子操作、描述符 |
| Open Babel | C++ | 格式转换 |
| DeepChem | Python | 深度学习 |
| CDK | Java | 分子指纹、描述符 |
| Indigo | C++ | 通用化学工具 |
| OCHEM | Web | 在线QSAR |

## 格式转换

| 格式 | 说明 | 扩展名 |
|------|------|--------|
| SMILES | 简化分子线性输入 | 字符串 |
| InChI | 国际化学标识符 | 字符串 |
| SDF | 结构数据文件 | .sdf |
| MOL | MDL Molfile | .mol |
| PDB | 蛋白质数据银行 | .pdb |
| PDBQT | AutoDock格式 | .pdbqt |
