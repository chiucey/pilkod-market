# 交互表单配置

## 学习计划设置表单

### 单页快速配置（默认）

当用户提供了基本信息时，使用简化表单：

```xml
<genui-form-wizard title="设置学习计划" action-id="learning_plan_setup">
  <genui-form-page title="步骤1: 学习目标">
    <genui-radio-group name="learningDays">
      <genui-radio value="7">7天速成</genui-radio>
      <genui-radio value="14">14天系统学习</genui-radio>
      <genui-radio value="30">30天精通</genui-radio>
      <genui-radio value="custom">自定义天数</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="customDays" placeholder="请输入自定义天数（如：21）"></genui-input>
  </genui-form-page>
  <genui-form-page title="步骤2: 每日安排">
    <genui-radio-group name="dailyTime">
      <genui-radio value="15">15分钟（碎片时间）</genui-radio>
      <genui-radio value="30">30分钟（标准）</genui-radio>
      <genui-radio value="60">1小时（深入学习）</genui-radio>
      <genui-radio value="120">2小时以上（高强度）</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="pushTime" placeholder="每日推送时间（如：09:00）"></genui-input>
  </genui-form-page>
  <genui-form-page title="步骤3: 学习偏好">
    <genui-checkbox-group name="preferences">
      <genui-checkbox value="case">补充真实案例</genui-checkbox>
      <genui-checkbox value="image">生成知识图片</genui-checkbox>
      <genui-checkbox value="exercise">包含练习题</genui-checkbox>
      <genui-checkbox value="quiz">包含小测验</genui-checkbox>
    </genui-checkbox-group>
    <genui-input selection-mode="checkbox" name="level" placeholder="当前基础（入门/进阶/精通）"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

### 多页详细配置（高级）

当需要更精细的设置时：

```xml
<genui-form-wizard title="个性化学习配置" action-id="advanced_learning_setup">
  <genui-form-page title="基础信息">
    <genui-input name="materialName" placeholder="学习材料名称（如：Python编程基础）"></genui-input>
    <genui-input selection-mode="checkbox" name="materialSource" placeholder="材料来源（书籍/课程/文档/其他）"></genui-input>
  </genui-form-page>
  <genui-form-page title="时间规划">
    <genui-input name="totalDays" placeholder="总学习天数"></genui-input>
    <genui-input selection-mode="checkbox" name="dailyMinutes" placeholder="每日学习时长（分钟）"></genui-input>
  </genui-form-page>
  <genui-form-page title="推送设置">
    <genui-radio-group name="pushTime">
      <genui-radio value="morning">早上（6:00-9:00）</genui-radio>
      <genui-radio value="noon">中午（11:00-13:00）</genui-radio>
      <genui-radio value="evening">晚上（19:00-22:00）</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="exactTime" placeholder="精确时间（如：08:30）"></genui-input>
  </genui-form-page>
  <genui-form-page title="内容偏好">
    <genui-checkbox-group name="contentTypes">
      <genui-checkbox value="theory">理论知识</genui-checkbox>
      <genui-checkbox value="practice">实践操作</genui-checkbox>
      <genui-checkbox value="case">案例分析</genui-checkbox>
      <genui-checkbox value="quiz">测验练习</genui-checkbox>
    </genui-checkbox-group>
    <genui-input selection-mode="checkbox" name="difficulty" placeholder="难度级别（入门/进阶/精通）"></genui-input>
  </genui-form-page>
  <genui-form-page title="确认配置">
    <genui-radio-group name="confirm">
      <genui-radio value="start">确认，开始学习</genui-radio>
      <genui-radio value="modify">需要调整</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="additionalNotes" placeholder="其他要求或备注（可选）"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

## 快速开始表单（极简版）

当用户直接提供材料并表达明确意向时：

```xml
<genui-form-wizard title="快速开始" action-id="quick_start">
  <genui-form-page title="学习设置">
    <genui-radio-group name="days">
      <genui-radio value="7">7天</genui-radio>
      <genui-radio value="14">14天</genui-radio>
      <genui-radio value="30">30天</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="dailyDuration" placeholder="每日学习时长（分钟）"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

## 进度确认表单

```xml
<genui-form-wizard title="记录学习进度" action-id="progress_update">
  <genui-form-page title="今日完成">
    <genui-radio-group name="completed">
      <genui-radio value="yes">已完成学习</genui-radio>
      <genui-radio value="partial">部分完成</genui-radio>
      <genui-radio value="skip">跳过明天继续</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="notes" placeholder="学习心得或问题（可选）"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

## 表单使用场景

| 场景 | 推荐表单 | 触发条件 |
|------|----------|----------|
| 首次设置 | 快速开始 | 用户直接提供材料 |
| 详细规划 | 详细配置 | 用户要求个性化设置 |
| 快速配置 | 单页配置 | 用户时间紧迫 |
| 每日记录 | 进度确认 | 每次推送后 |
| 计划调整 | 详细配置 | 用户要求修改计划 |
