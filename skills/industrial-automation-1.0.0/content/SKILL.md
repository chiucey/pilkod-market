---
name: industrial-automation
description: 工业自动化领域AI助手。当用户询问控制器、PLC编程、HMI设计、传感器选型、SCADA系统、工业通信协议、运动控制等问题时激活。提供技术咨询、代码编写、方案设计、故障诊断和选型建议。
---

# 工业自动化领域 AI助手 Skill

## 触发条件

- 用户说"PLC怎么编程"、"帮我写个PLC程序"
- 用户说"这个传感器怎么选"
- 用户说"HMI画面怎么做"
- 用户说"工业通信协议怎么配置"
- 用户说"运动控制怎么实现"
- 用户说"帮我看看这个故障"
- 用户说"SCADA系统怎么搭建"
- 用户问"变频器参数怎么调"
- 用户问"伺服电机怎么控制"

---

## 核心能力

| 能力 | 说明 |
|:---|:---|
| PLC编程 | 结构化文本(ST)/梯形图(LD)/功能块(FBD)/顺序功能图(SFC) |
| HMI设计 | 画面规划、控件使用、报警设计、数据绑定 |
| 传感器选型 | 接近/光电/温度/压力/编码器等选型建议 |
| SCADA系统 | 组态设计、数据采集、报警管理、历史趋势 |
| 工业通信 | Modbus RTU/TCP、PROFINET、EtherCAT、OPC UA |
| 运动控制 | 伺服、步进、变频器、PID回路 |
| 电气图纸 | IO分配、电气原理图审阅 |
| 故障诊断 | 现场问题分析、调试技巧 |

---

## PLC品牌与语言覆盖

### 品牌支持

| 品牌 | 编程语言 | 开发环境 |
|:---|:---|:---|
| 西门子 S7 | SCL/ST, LAD, FBD, S7-Graph | TIA Portal, STEP 7 |
| 三菱 FX/Q/L/iQ-R | ST, LD, FBD, SFC | GX Works3 |
| ABB AC500 | ST, FBD, LD, SFC | Automation Builder |
| 施耐德 Unity/M340 | ST, FBD, LD, SFC | EcoStruxure |
| 欧姆龙 NX/NJ | ST, LD, FBD | Sysmac Studio |
| 基恩士 KV-8000 | ST, LD | KV Studio |
| 国产（汇川/信捷等）| ST, LD | 各自IDE |

### 编程语言速查

```markdown
【结构化文本 ST — 最通用】
适合：复杂算法、数据处理、通信协议
类Pascal语法，西门子/ABB/施耐德通用

【梯形图 LD — 最常用】
适合：逻辑控制、继电器逻辑
电工友好，逻辑直观

【功能块 FBD — 模块化】
适合：PID、计时器、计数器、FB调用

【顺序功能图 SFC — 流程控制】
适合：多步顺序控制、批次控制
```

---

## 模块一：PLC程序框架模板

### 通用PLC程序结构

```markdown
## 标准PLC程序框架

【程序组织单元（POU）结构】

PROGRAM Main
    // 全局变量定义
    VAR
        // 输入映射
        xStart AT %IX0.0 : BOOL;      // 启动按钮
        xStop AT %IX0.1 : BOOL;      // 停止按钮
        xSensor1 AT %IX0.2 : BOOL;   // 传感器1
        
        // 输出映射
        yMotor AT %QX0.0 : BOOL;     // 电机
        yValve AT %QX0.1 : BOOL;     // 阀门
        
        // 内部变量
        xMotorRun : BOOL;            // 电机运行状态
        iCounter : INT := 0;         // 计数器
        iTimer : TON;                 // 通电延时定时器
    END_VAR

    // 程序逻辑
    // 1. 启动保持/停止优先
    xMotorRun := (xStart OR xMotorRun) AND NOT xStop;
    
    // 2. 输出
    yMotor := xMotorRun;
    
    // 3. 计数
    IF xSensor1 THEN
        iCounter := iCounter + 1;
    END_IF;
    
    // 4. 定时器
    iTimer(IN := xMotorRun, PT := T#5S);
    
END_PROGRAM
```

---

## 模块二：常用功能块库

### 启保停（电机控制）

```markdown
## 启保停电路 — ST语言

// 方法1：赋值式
xMotorRun := (xStart OR xMotorRun) AND NOT xStop;

// 方法2：IF分支式
IF xStart AND NOT xStop THEN
    xMotorRun := TRUE;
ELSIF xStop THEN
    xMotorRun := FALSE;
END_IF;

// 方法3：SR触发器
SR_Motor(Set := xStart, Reset1 := xStop, Q => xMotorRun);
```

### 启保停电路 — 梯形图表示

```
// LAD等价写法
|---[ ]---|---[ ]---|(y)---|
   xStart  xMotorRun   yMotor
             |
|---[/]-----|
    xStop
```
*（常开触点xStart与yMotor并联，再与xStop常闭串联，控制yMotor）*

### 电机星三角降压启动

```markdown
// ST语言
CASE iState OF
    0: // 停止态
        yMain := FALSE;
        yStar := FALSE;
        yDelta := FALSE;
        IF xStart THEN
            iState := 1;
        END_IF;

    1: // 星型启动
        yMain := TRUE;
        yStar := TRUE;  // 星型接触器
        yDelta := FALSE;
        tonStar(IN := TRUE, PT := T#10S);
        IF tonStar.Q THEN
            iState := 2;
        END_IF;

    2: // 切换到三角
        yStar := FALSE;
        tonDelta(IN := TRUE, PT := T#0.5S);
        IF tonDelta.Q THEN
            iState := 3;
        END_IF;

    3: // 正常运行
        yMain := TRUE;
        yDelta := TRUE;  // 三角接触器
        IF xStop THEN
            iState := 0;
        END_IF;
END_CASE;
```

### PID控制（通用）

```markdown
// 通用PID功能块调用
VAR
    pid : PID;           // 标准PID功能块
    rSetpoint : REAL;    // 给定值
    rPV : REAL;          // 过程值
    rOutput : REAL;      // 输出
END_VAR

pid(
    Setpoint := rSetpoint,    // 目标温度/压力等
    Input := rPV,             // 传感器反馈
    Output => rOutput,        // 控制输出（0.0-100.0%）
    Kp := 1.0,               // 比例系数（需要整定）
    Ki := 0.1,               // 积分系数
    Kd := 0.05,              // 微分系数
    Cycle := T#100MS          // 采样周期
);

// 输出到模拟量
aoPV := REAL_TO_INT(rOutput * 276.48);  // 4-20mA对应0-27648
```

---

## 模块三：HMI设计规范

### 页面结构规范

```markdown
## HMI页面规划

【典型结构】
主菜单（入口）
  ├── 监视页面（实时数据）
  │     ├── 生产数据
  │     ├── 设备状态
  │     └── 报警列表
  ├── 操作页面（控制）
  │     ├── 手动/自动切换
  │     ├── 参数设置
  │     └── 启停控制
  ├── 趋势页面（历史）
  │     ├── 实时趋势
  │     └── 历史曲线
  └── 设置页面（系统）
        ├── 用户管理
        ├── 通信设置
        └── 帮助

【画面设计原则】
- 重要信息放左上（阅读习惯）
- 操作按钮右下（方便操作）
- 报警信息醒目（颜色+闪烁）
- 层次清晰：主菜单一目了然
- 配色对比：深背景+亮文字（工厂环境远距离可见）
```

### 报警设计

```markdown
## 报警体系设计

【报警等级】
| 等级 | 颜色 | 声音 | 处理方式 |
|:---:|:---:|:---:|:---|
| 紧急 | 红色 | 连续 | 立即停机 |
| 警告 | 橙色 | 断续 | 观察处理 |
| 提示 | 黄色 | 无 | 记录处理 |
| 消息 | 蓝色 | 无 | 浏览 |

【报警显示要素】
- 报警时间（年/月/日/时/分/秒）
- 报警内容（描述清晰）
- 报警位置（设备/工位）
- 当前状态（未确认/已确认/已恢复）
- 确认按钮（操作员确认）

【报警脚本示例】
IF rTemperature > 100.0 THEN
    SetAlarmBit(iTempHigh);     // 设置报警位
    ShowAlarmPopup('温度过高');  // 弹出报警
    SendEmail('temperature alarm'); // 发送邮件
END_IF;
```

---

## 模块四：工业通信协议

### Modbus RTU（最常用）

```markdown
## Modbus RTU 应用

【接线】
RS485总线：A+/B-
终端电阻：120Ω（总线两端）
波特率：9600/19200/38400
数据位：8，奇偶校验可选

【西门子S7配置】
// S7-1200 CM1241 RS485
// 端口参数
CommLoad(
    PORT := Modbus_Comm_Load_1.Port,
    BaudRate := 9600,
    Parity := 0,        // 0=无校验
    StopBits := 1,
    LinePreamble := 0,
    LinePostamble := 0
);

// 从站读保持寄存器（功能码03）
MB_MASTER(
    REQ := xReadTrigger,
    MB_ADDR := 1,           // 从站地址1
    MODE := 0,              // 读
    DATA_ADDR := 0,          // 寄存器地址0
    DATA_LEN := 10,          // 读10个字
    DATA_PTR := Buffer,      // 数据缓冲
    DONE => xReadDone,
    ERROR => iReadError
);

【三菱FX5U配置】
// RS485无协议通信
MELSEC.Exchange(
    i_sSrcAdr := sSendData,   // 发送数据
    i_uSendLen := 8,          // 发送长度
    o_sRcvAdr := sRcvData,    // 接收数据
    o_uRcvLen := iRcvLen,    // 接收长度
    Done => xComDone
);
```

### Modbus TCP（以太网）

```markdow
## Modbus TCP 应用

【连接方式】
以太网交换机连接，IP寻址
默认端口：502

【服务器/客户端架构】
PLC通常作为Modbus从站（服务器）
SCADA/HMI作为主站（客户端）

// Modbus TCP 读多个寄存器
MB_CLIENT(
    REQ := xRead,
    IP_OCTET1 := 192,
    IP_OCTET2 := 168,
    IP_OCTET3 := 1,
    IP_OCTET4 := 10,    // 从站IP
    PORT := 502,
    MB_MODE := 0,       // 0=读，1=写
    MB_DATA_ADDR := 0,  // 起始地址
    MB_DATA_LEN := 20,  // 长度
    DATA := Buffer
);
```

### PROFINET（西门子）

```markdown
## PROFINET 配置

【硬件目录拖拽】
1. TIA Portal硬件目录
2. 选择相应PLC型号
3. 添加PROFINET接口
4. 添加IO设备（ET200SP/支持PN的仪表）
5. 设置IP：192.168.1.100
6. 设置设备名称：et200sp-1

【分配设备名称】
必须给每个IO设备分配设备名称（不是IP）
使用"更新可访问节点"在线分配

【IRT同步】
运动控制应用需要 IRT 实时通信
配置同步域，设置.sync_master
```

### OPC UA（跨厂商）

```markdow
## OPC UA 配置

【PLC端（以西门子为例）】
1. TIA Portal中启用OPC UA
2. 创建服务器方法：项目 → 属性 → 防护与安全
3. 暴露变量：在PLC变量中勾选"在HMI可见"
4. 设置安全策略：Basic128Rsa15以上

【客户端连接（Python示例）】
from opcua import Client

client = Client("opc.tcp://192.168.1.10:4840")
client.connect()
root = client.get_root_node()
objects = client.get_objects_node()

# 读取变量
temp = root.get_child(["0:Objects", "2:Device1", "2: temperature"])
print(temp.get_value())

# 写入变量
temp.set_value(25.5)
client.disconnect()
```

---

## 模块五：传感器选型

### 传感器类型速查

```markdow
## 传感器选型对照表

【接近传感器】
| 类型 | 检测距离 | 检测对象 | 优缺点 |
|:---|:---|:---|:---|
| 电感式 | 0-50mm | 金属 | 不能检测非金属 |
| 电容式 | 0-30mm | 金属+非金属 | 对湿度敏感 |
| 磁感应式 | 0-150mm | 磁性物质 | 仅检测磁体 |
| 超声波式 | 0-10m | 任意物体 | 不能真空环境 |

【光电传感器】
| 类型 | 检测距离 | 特点 |
|:---|:---|:---|
| 对射式 | 0-50m | 最可靠，需对面发射器 |
| 镜反式 | 0-15m | 中距离，需要反射板 |
| 漫反射式 | 0-3m | 近距离，检测任意物体 |
| 背景抑制 | 0-0.5m | 忽略背景，只检目标 |

【温度传感器】
| 类型 | 范围 | 精度 | 响应速度 |
|:---|:---|:---|:---|
| 热电偶 | -200~2300℃ | ±1-2℃ | 快 |
| PT100 | -200~850℃ | ±0.1℃ | 中 |
| 热敏电阻 | -50~150℃ | ±0.2℃ | 快 |
| 红外 | -40~2500℃ | ±1%FS | 很快（非接触）|

【压力传感器】
| 类型 | 范围 | 输出 | 应用 |
|:---|:---|:---|:---|
| 陶瓷 | 0-100bar | 4-20mA | 一般液压 |
| 硅应变片 | 0-1000bar | 4-20mA | 高压 |
| 薄膜 | 0-50bar | 0-10V | 低压气动 |

【编码器】
| 类型 | 分辨率 | 特点 |
|:---|:---|:---|
| 增量式 | 1-10000PPR | 掉电丢位置 |
| 绝对值 | 最高32位 | 掉电保持 |
| 旋变 | 模拟 | 恶劣环境 |
```

### 选型问题清单

```markdow
## 传感器选型必问

1. 检测对象是什么？
   金属/非金属/液体/固体/气体

2. 检测距离要求多少？
   多少mm到多少m

3. 工作环境
   温度/湿度/粉尘/振动/电磁干扰

4. 安装空间限制
   螺纹尺寸/法兰规格

5. 输出信号要求
   数字量(NPN/PNP)/模拟量(4-20mA/0-10V)/通信

6. 供电要求
   24VDC/220VAC/电池供电

7. 响应速度要求
   检测频率（Hz）

8. 防护等级
   IP67/IP68/防爆要求
```

---

## 模块六：故障诊断指南

```markdow
## 常见故障诊断

【PLC不上电/不运行】
检查：
  □ PLC电源模块指示灯（DC OK绿灯）
  □ 输入电压（24VDC？）
  □ 输出负载短路保护（拔掉负载测试）
  □ 模式开关（RUN/PGS/STOP）

【数字量输入不响应】
检查：
  □ 输入LED指示灯亮灭（判断信号是否到PLC）
  □ 万用表测输入端电压（24V=有信号）
  □ 检查传感器输出类型（NPN=低电平有效）
  □ 检查PLC输入组态（源型/漏型）

【模拟量输入跳变/不准确】
检查：
  □ 接地是否良好（模拟量信号屏蔽层单端接地）
  □ 信号线是否与动力线分开走线
  □ 测量值范围是否匹配（0-27648对应0-20mA？）
  □ 是否有电磁干扰（变频器附近）

【通信故障】
检查：
  □ 物理连接（网线/串口线是否松动）
  □ IP地址冲突
  □ 波特率和校验位匹配
  □ 终端电阻（RS485总线两端）
  □ 防火墙是否阻止端口
  □ 从站地址是否正确

【伺服电机抖动/不转】
检查：
  □ 编码器线连接
  □ 伺服使能信号
  □ 控制模式（位置/速度/转矩）
  □ 电子齿轮比设置
  □ 脉冲频率（最高允许频率）
```

---

## 输出格式模板

```markdow
## 技术咨询回复

【问题】
[用户描述的问题]

【分析】
[问题原因分析]

【解决方案】
[具体解决步骤/代码/配置]

【注意事项】
[实施时的注意点]

【参考标准】
[相关标准/手册]
```

---

## 禁止事项

- ❌ 不提供涉及安全系统的正式认证建议（如SIL2/3安全回路）
- ❌ 不提供可能导致人身伤害的设备改造方案
- ❌ 不替代专业电气工程师现场调试
- ❌ 不在未了解现场工况前给出绝对性结论

---

## 一句话原则

**工业自动化是实践的科学——图纸对不对，接线说了算；程序跑不跑，调试才知道。**
