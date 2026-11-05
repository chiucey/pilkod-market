# ARM开发参考指南

## Cortex-M系列开发

### 寄存器组结构

```
Cortex-M4 寄存器组织:
- R0-R12: 通用寄存器
  - R0-R7: 低寄存器 (Thumb-2 所有指令)
  - R8-R12: 高寄存器 (部分指令受限)
- R13 (SP): 堆栈指针
  - PSP: 进程堆栈指针
  - MSP: 主堆栈指针 (复位后默认)
- R14 (LR): 链接寄存器
- R15 (PC): 程序计数器
- xPSR: 程序状态寄存器
  - APSR: 应用状态 (N,Z,C,V,Q)
  - IPSR: 中断状态
  - EPSR: 执行状态
```

### 中断优先级配置

```c
/* NVIC优先级配置 */
void nvic_config(uint8_t irq_num, uint8_t priority) {
    /* 优先级分组: 0位子优先级, 8位抢占优先级 */
    uint32_t priority_group = SCB->AIRCR & SCB_AIRCR_PRIGROUP_Msk;

    if (irq_num >= 16) {  /* 外部中断 */
        NVIC->IP[irq_num - 16] = (priority << (8 - __NVIC_PRIO_BITS));
    } else {  /* 系统异常 */
        /* 系统异常优先级在SCB->SHP中配置 */
    }
}

/* 使能/禁止中断 */
void enable_irq(uint8_t irq_num) {
    NVIC->ISER[irq_num / 32] = (1 << (irq_num % 32));
}

void disable_irq(uint8_t irq_num) {
    NVIC->ICER[irq_num / 32] = (1 << (irq_num % 32));
}
```

### DSP指令集优化

```c
/* CMSIS-DSP 矩阵运算优化 */
#include "arm_math.h"

void matrix_multiply_opt(float32_t *A, float32_t *B, float32_t *C,
                         uint16_t rowsA, uint16_t colsA, uint16_t colsB) {
    arm_matrix_instance_f32 M_A, M_B, M_C;

    arm_mat_init_f32(&M_A, rowsA, colsA, A);
    arm_mat_init_f32(&M_B, colsA, colsB, B);
    arm_mat_init_f32(&M_C, rowsA, colsB, C);

    arm_mat_mult_f32(&M_A, &M_B, &M_C);
}

/* FIR滤波器优化 */
void fir_filter_opt(const float32_t *pSrc, float32_t *pDst,
                    uint32_t blockSize, const float32_t *pCoeffs,
                    float32_t *pState, uint32_t numTaps) {
    arm_fir_instance_f32 fir_inst;

    arm_fir_init_f32(&fir_inst, numTaps, (float32_t *)pCoeffs, pState);
    arm_fir_f32(&fir_inst, pSrc, pDst, blockSize);
}
```

## Cortex-A系列开发

### SVC和异常处理

```asm
@ SVC调用示例 (ARM ASM)
.syntax unified

SVC_Handler:
    push {lr}
    mrs lr, ipsr
    tst lr, #0x1F
    bne SVC_Exception

    ldr lr, =SVC_Return
    ldr pc, [lr, r0, lsl #2]

SVC_Return:
    pop {pc}

SVC_Exception:
    @ 异常处理代码
    pop {pc}
```

### MMU配置

```c
/* MMU页表配置 - 3级页表, 4KB粒度 */
#define MMU_SECTION_BASE    0x100000
#define MMU_SECTION_MASK    0xFFF00000
#define MMU_SECTION_SIZE    0x00100000

typedef struct {
    uint32_t desc[4096];
} mmu_l1_table_t;

void mmu_init(void) {
    mmu_l1_table_t *ttb = (mmu_l1_table_t *)TTB_BASE;

    for (int i = 0; i < 4096; i++) {
        uint32_t vaddr = i << 20;
        uint32_t paddr = vaddr;  /* 1:1映射 */

        /* Section描述符 */
        uint32_t desc = paddr | SECTION_DESC_AP_RW_RW |
                        SECTION_DESC_CACHE_WB | SECTION_DESC_NS;
        ttb->desc[i] = desc;
    }

    /* 设置TTBR0 */
    __asm volatile(
        "mcr p15, 0, %0, c2, c0, 0"
        : : "r"(TTB_BASE)
    );

    /* 启用MMU */
    __asm volatile(
        "mrc p15, 0, r0, c1, c0, 0\n"
        "orr r0, r0, #0x1\n"
        "mcr p15, 0, r0, c1, c0, 0"
    );
}
```

## 功耗管理

### 低功耗模式配置

```c
/* STM32L4 低功耗模式 */
typedef enum {
    SLEEP_MODE,
    STOP2_MODE,
    STANDBY_MODE
} low_power_mode_t;

void enter_low_power(low_power_mode_t mode) {
    /* 禁用外设时钟 */
    HAL_SuspendTick();
    HAL_PWR_EnterSTOPMode(mode == STOP2_MODE ?
        PWR_LOWPOWERMODE_STOP2 : PWR_LOWPOWERMODE_STOP1);
}

/* RTC唤醒配置 */
void config_rtc_wakeup(uint32_t seconds) {
    RTC_HandleTypeDef hrtc;

    hrtc.Instance = RTC;
    hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
    hrtc.Init.AsynchPrediv = 127;
    hrtc.Init.SynchPrediv = 255;

    /* 配置唤醒定时器 */
    HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds * 32768,
                                 RTC_WAKEUPCLOCK_RTCCLK_DIV16);
}
```
