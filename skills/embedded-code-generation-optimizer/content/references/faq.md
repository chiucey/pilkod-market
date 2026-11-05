# Embedded Code Optimization FAQ

## 代码大小优化

### Q: 如何确定代码大小的瓶颈?
**A**: 使用以下工具分析:

```bash
# ARM GCC
arm-none-eabi-size -A -d firmware.elf
arm-none-eabi-objdump -h -S firmware.elf | less

# Keil
fromelf --text -c firmware.axf

# IAR
ielfdumparm --text firmware.out
```

### Q: 内联函数的最佳实践?
**A**:
- 小型函数（<10行）优先内联
- 使用 `__attribute__((always_inline))` 强制内联
- 避免递归函数内联
- 高频调用函数优先内联

### Q: 如何减少Flash使用?
**A**:
1. 启用链接器垃圾回收: `-ffunction-sections -fdata-sections`
2. 使用编译优化级别 `-Os`
3. 避免浮点运算，改用定点数
4. 使用查表法替代计算
5. 减少字符串常量的使用

## 功耗优化

### Q: 如何选择最佳低功耗模式?
**A**:

| 模式 | 功耗 | 唤醒时间 | 适用场景 |
|-----|------|---------|---------|
| Sleep | ~1mA | ~2us | 短期等待 |
| Stop | ~50uA | ~50us | 中等等待 |
| Standby | ~2uA | ~1ms | 长时间等待 |

### Q: 如何优化DMA传输?
**A**:
1. 使用双缓冲减少CPU干预
2. 配置正确的传输宽度
3. 使用突发传输(Burst)
4. 避免跨AHB从机边界

## 实时性能

### Q: 中断延迟如何测量?
**A**:

```c
volatile uint32_t interrupt_latency;

void TIM2_IRQHandler(void) {
    uint32_t start = DWT->CYCCNT;
    // 中断处理...
    interrupt_latency = start - interrupt_trigger_time;
}

void trigger_interrupt(void) {
    interrupt_trigger_time = DWT->CYCCNT;
    NVIC_SetPendingIRQ(TIM2_IRQn);
}
```

### Q: 如何减少中断嵌套?
**A**:
1. 限制中断优先级数量（建议<4级）
2. 最小化ISR执行时间
3. 使用Deferred Procedure Call (DPC)模式
4. 避免在ISR中启用/禁用其他中断

## 内存优化

### Q: 如何避免堆碎片化?
**A**:
1. 使用内存池分配器
2. 预分配所有需要的内存
3. 避免动态分配在中断中
4. 固定大小的内存块分配

### Q: 栈溢出如何检测?
**A**:

```c
// 方法1: 填充模式
#define STACK_FILL_VALUE 0xA5A5A5A5
void check_stack(void) {
    extern uint32_t _estack;
    extern uint32_t _sstack;
    uint32_t *p = (uint32_t *)&_estack;
    uint32_t count = 0;
    while (*--p == STACK_FILL_VALUE) count++;
    printf("Stack used: %u bytes\n", count * 4);
}

// 方法2: MPU保护
void mpu_config(void) {
    MPU->RNR = 0;  // 栈区域
    MPU->RBAR = (uint32_t)&_sstack | MPU_RBAR_ADDR_Msk | 0;
    MPU->RASR = MPU_RASR_ENABLE_Msk | MPU_RASR_SIZE_Msk |
                MPU_RASR_AP_PNO_Msk;  // 无访问权限
}
```

## 编译优化

### Q: -O2 vs -Os 如何选择?
**A**:

| 场景 | 推荐级别 | 原因 |
|-----|---------|------|
| 资源受限 | -Os | 减少代码大小 |
| 性能关键 | -O2 | 平衡速度与大小 |
| 极限性能 | -O3 | 最大优化 |
| 调试模式 | -O0 | 可调试 |

### Q: 如何处理优化导致的问题?
**A**:
1. 使用 `__attribute__((optimize("O0")))` 禁用特定函数优化
2. 使用 `volatile` 防止变量优化
3. 使用内存屏障 `__asm__ volatile("" ::: "memory")`
4. 检查变量别名问题（restrict关键字）
