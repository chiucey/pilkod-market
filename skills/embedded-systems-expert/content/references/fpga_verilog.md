---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 25dae9d569248b2ff85b5ab854d5d6e3
    PropagateID: 25dae9d569248b2ff85b5ab854d5d6e3
    ReservedCode1: 3045022001331bb194afef79a30249437aceee8229174609ed1adabd2608e9a2d775c804022100c41dc8fa07053e1a14722208f07bc41e59de1b8427a0b7d0f2ed4c445204604e
    ReservedCode2: 3045022100e1de2eb0a5cef6792110505c76918d3d878beff6460c675516f597c6da2941b40220518c08469a8b94d7d7b35fef8abe02e4b20017f3a7b9a419ac89f209452642de
---

# FPGA/Verilog开发参考指南

## 时序约束最佳实践

### 完整SDC约束模板

```tcl
#========================================
# 主时钟约束
#========================================
# 板级50MHz时钟
create_clock -period 20.000 -name clk_50m [get_ports CLK_50M]
set_clock_uncertainty 0.200 [get_clocks clk_50m]

# DDR3参考时钟200MHz
create_clock -period 5.000 -name mem_ref_clk [get_ports MEM_REFCLK]

#========================================
# 生成时钟约束
#========================================
# PLL输出时钟
create_generated_clock -name pll_sys_clk \
    -source [get_pins u_pll/clk_in] \
    -divide_by 2 -multiply_by 10 \
    [get_pins u_pll/clk_out_sys]

create_generated_clock -name pll_mem_clk \
    -source [get_pins u_pll/clk_in] \
    -divide_by 1 -multiply_by 40 \
    [get_pins u_pll/clk_out_mem]

#========================================
# 输入延迟约束 (采集外部数据)
#========================================
# SRAM接口 - 建立/保持时间分析
set_input_delay -clock clk_50m -max 3.0 \
    [get_ports {DIN[*]}]
set_input_delay -clock clk_50m -min 1.0 \
    [get_ports {DIN[*]}]

# SDRAM接口
set_input_delay -clock mem_ref_clk -max 1.5 \
    [get_ports {SDRAM_DQ[*]}]
set_input_delay -clock mem_ref_clk -min 0.3 \
    [get_ports {SDRAM_DQ[*]}]

#========================================
# 输出延迟约束 (驱动外部器件)
#========================================
set_output_delay -clock clk_50m -max 4.0 \
    [get_ports {DOUT[*]}]
set_output_delay -clock clk_50m -min 1.5 \
    [get_ports {DOUT[*]}]

#========================================
# 时钟域交叉约束
#========================================
# 异步复位同步化
set_false_path -from [get_async_pins u_top/sys_rst_n]

# 跨时钟域数据路径
set_clock_groups -asynchronous \
    -group [get_clocks clk_50m] \
    -group [get_clocks mem_ref_clk] \
    -group [get_clocks pll_sys_clk]

#========================================
# 多周期路径
#========================================
# 复杂运算路径
set_multicycle_path -setup -from [get_cells {accumul[*]}] \
    -to [get_cells {result_reg[*]}] 3
set_multicycle_path -hold -from [get_cells {accumul[*]}] \
    -to [get_cells {result_reg[*]}] 2

#========================================
# 最大过渡时间约束
#========================================
set_max_transition 0.500 [current_design]
set_max_fanout 20 [current_design]
```

## 射频接口设计模板

### JESD204B/C接口

```verilog
`timescale 1ns/1ps

module jesd204b_rx #(
    parameter LANES = 4,
    parameter M = 2,          // converters per device
    parameter N = 14,         // converter resolution
    parameter NP = 16,        // packed resolution
    parameter S = 1,          // samples per frame
    parameter K = 32,         // frames per multiframe
    parameter F = 4           // octets per frame
)(
    input  wire                 dev_clk,
    input  wire                 sysref,
    input  wire [LANES-1:0]      lane_data_p,
    input  wire [LANES-1:0]     lane_data_n,
    output wire [M*NP-1:0]      sample_out,
    output wire                 sync_out,
    output wire                 status
);

    // GT接口
    wire [LANES-1:0] rx_data;
    wire [LANES-1:0] rx_header;
    wire [LANES-1:0] rx_valid;

    // 8b/10b解码后数据
    wire [9:0] decoded_data [LANES-1:0];

    genvar i;
    generate
        for (i = 0; i < LANES; i = i + 1) begin : lane_inst
            // GT收发器原语
            GTYE4_CHANNEL #(
                .RX_OUT_DIV  (1),
                .RX_USRCLK_DIV(2),
                .RX_PRBS31_CHECKER(0)
            ) u_gt_rx (
                .RXSYSCLKSEL (2'b00),
                .RXRUSRCLK    (dev_clk),
                .RXRUSRCLK2   (dev_clk2x),
                .RXRECLK      (dev_clk),
                .GTREFCLK00   (ref_clk),
                .PRBSCNTRESET (1'b0),
                .RXPRBSERR    (),
                .GTYRXP       (lane_data_p[i]),
                .GTYRXN       (lane_data_n[i]),
                .RXRESTART    (1'b0),
                .RXDATA       (rx_data[i]),
                .RXHEADER     (rx_header[i]),
                .RXHEADERVALID(rx_valid[i])
            );

            // 8b/10b解码
            wire [7:0] char_disp_err;
            always @(posedge dev_clk2x) begin
                decode_8b10b u_decode (
                    .clk    (dev_clk2x),
                    .rst_n  (rst_n),
                    .enc_in (rx_data[i]),
                    .dec_out(decoded_data[i]),
                    .disp_err(char_disp_err[i])
                );
            end
        end
    endgenerate

    // 链路同步状态机
    typedef enum {
        RESET,
        WAIT_FOR_K,
        SYNC_ACQUIRED,
        DATA_MODE
    } link_state_t;

    link_state_t link_state, next_state;

    always_ff @(posedge dev_clk) begin
        if (!rst_n)
            link_state <= RESET;
        else
            link_state <= next_state;
    end

    // 数据组装
    reg [M*NP-1:0] sample_data;
    always_ff @(posedge dev_clk) begin
        if (link_state == DATA_MODE) begin
            sample_data <= {decoded_data[1], decoded_data[0]};
        end
    end

    assign sample_out = sample_data;
    assign status = (link_state == DATA_MODE);

endmodule
```

### LVDS/SerDes接口

```verilog
module lvds_if #(
    parameter CHANNELS = 8,
    parameter SER_FACTOR = 10  // 10:1 串行化
)(
    input  wire                  ref_clk,      // 200MHz
    input  wire                  lvds_clk_p,
    input  wire                  lvds_clk_n,
    input  wire [CHANNELS-1:0]   lvds_data_p,
    input  wire [CHANNELS-1:0]   lvds_data_n,
    output reg  [CHANNELS*8-1:0] lvds_parallel,

    input  wire                  bit_clk,      // ISERDES位时钟
    input  wire                  frame_clk      // ISERDES字时钟
);

    // LVDS时钟缓冲
    wire lvds_clk;
    IBUFDS #(.DIFF_TERM("TRUE"), .IBUF_LOW_PWR("FALSE"))
        u_clk_buf (.I(lvds_clk_p), .IB(lvds_clk_n), .O(lvds_clk));

    genvar ch;
    generate
        for (ch = 0; ch < CHANNELS; ch = ch + 1) begin : channel_gen
            // 数据通道缓冲
            wire lvds_data;
            IBUFDS u_data_buf (
                .I  (lvds_data_p[ch]),
                .IB (lvds_data_n[ch]),
                .O  (lvds_data)
            );

            // ISERDESE2 原语 - NETWORKING模式
            (* DONT_TOUCH = "true" *)
            wire [7:0] serdes_out;
            ISERDESE2 #(
                .DATA_RATE         ("DDR"),
                .INTERFACE_TYPE    ("NETWORKING"),
                .DATA_WIDTH        (SER_FACTOR),
                .SERDES_MODE       ("MASTER"),
                .IO_DELAY_GROUP    ("lvds_group")
            ) u_iserdes (
                .RST       (~rst_n),
                .CLK       (lvds_clk),
                .CLKB      (~lvds_clk),
                .CLKDIV    (frame_clk),
                .BITSLIP   (bitslip_en),
                .CE1       (1'b1),
                .D         (lvds_data),
                .Q1-Q8     (serdes_out)
            );

            // 输出寄存器
            always @(posedge frame_clk) begin
                lvds_parallel[(ch+1)*8-1:ch*8] <= serdes_out;
            end
        end
    endgenerate

endmodule
```

## 仿真验证框架

### UVM验证模板

```verilog
`timescale 1ns/1ps
package rf_rx_pkg;
    import uvm_pkg::*;
    `include "uvm_macros.svh"

    // 事务定义
    class rf_sample_trans extends uvm_sequence_item;
        rand bit [13:0] i_data;
        rand bit [13:0] q_data;
        rand int        timestamp;

        `uvm_object_utils_begin(rf_sample_trans)
            `uvm_field_int(i_data, UVM_DEFAULT)
            `uvm_field_int(q_data, UVM_DEFAULT)
        `uvm_object_utils_end
    endclass

    // 驱动器
    class rf_driver extends uvm_driver #(rf_sample_trans);
        virtual interface rf_if vif;

        `uvm_component_utils(rf_driver)

        function void build_phase(uvm_phase phase);
            super.build_phase(phase);
            if (!uvm_config_db #(virtual rf_if)::get(this, "", "vif", vif))
                `uvm_fatal("DRV", "Virtual interface not found")
        endfunction

        task run_phase(uvm_phase phase);
            forever begin
                seq_item_port.get_next_item(req);
                drive_sample(req);
                seq_item_port.item_done();
            end
        endtask

        task drive_sample(rf_sample_trans t);
            @(posedge vif.clk);
            vif.i_data <= t.i_data;
            vif.q_data <= t.q_data;
        endtask
    endclass

    // 记分板
    class rf_scoreboard extends uvm_scoreboard;
        uvm_analysis_export #(rf_sample_trans) expect_export;
        uvm_analysis_export #(rf_sample_trans) actual_export;

        `uvm_component_utils(rf_scoreboard)

        function void build_phase(uvm_phase phase);
            expect_export = new("expect_export", this);
            actual_export = new("actual_export", this);
        endfunction

        function void write_expect(rf_sample_trans t);
            // 参考模型计算
        endfunction

        function void write_actual(rf_sample_trans t);
            // 结果比对
        endfunction
    endclass

endpackage
```
